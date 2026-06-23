using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using DPFP;
using DPFP.Capture;
using DPFP.Processing;
using DPFP.Verification;

namespace HuelleroBridge
{
    public class TemplateEntry
    {
        public int    UsuarioId { get; set; }
        public string Nombre    { get; set; }
        public string Base64    { get; set; }
    }

    public class FingerprintCapture : DPFP.Capture.EventHandler
    {
        private readonly Capture         _capturer;
        private readonly Enrollment      _enrollment;
        private readonly Verification    _verificator;
        private readonly EnrollmentState _state;
        private readonly Action<string>  _broadcast;
        private readonly RelayController _relay;
        private static readonly HttpClient _http = new HttpClient();

        private List<TemplateEntry> _templates = new List<TemplateEntry>();

        // Cooldown por usuario: evita doble-registro cuando el usuario pone el dedo
        // varias veces seguidas mientras el HTTP está en vuelo.
        private readonly Dictionary<int, DateTime> _ultimoAcceso = new Dictionary<int, DateTime>();
        private const int CooldownSegundos = 4;

        // Configurables por entorno (JSB_API_BASE / BRIDGE_SECRET). Ver BridgeConfig.
        private static readonly string ApiBase      = BridgeConfig.ApiBase;
        private static readonly string BridgeSecret = BridgeConfig.BridgeSecret;

        public FingerprintCapture(EnrollmentState state, Action<string> broadcast, RelayController relay = null)
        {
            _state       = state;
            _broadcast   = broadcast;
            _relay       = relay;
            // Priority.Normal (default) solo captura cuando la ventana vinculada al hilo
            // tiene foco. Como nuestra BridgeForm está oculta y nunca toma foco, los
            // eventos OnComplete/OnFingerTouch nunca se entregan. High permite captura en
            // segundo plano sin importar el foreground. Es read-only, hay que pasarla por
            // constructor.
            _capturer    = new Capture(Priority.High);
            _capturer.EventHandler = this;
            _enrollment  = new Enrollment();
            _verificator = new Verification();
        }

        public void Start()
        {
            try
            {
                _capturer.StartCapture();
                Console.WriteLine("[HUELLERO] Capturando. Coloca el dedo en el lector...");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[HUELLERO] No se pudo iniciar la captura: {ex.Message}");
            }
        }

        public void Stop()
        {
            try { _capturer.StopCapture(); } catch { }
        }

        public void CargarTemplates(List<TemplateEntry> templates)
        {
            _templates = templates ?? new List<TemplateEntry>();
            _state.TemplatesEnCache = _templates.Count;
            Console.WriteLine($"[HUELLERO] Templates cargados: {_templates.Count}");
        }

        /// <summary>
        /// Descarga todos los templates desde el backend. Pensado para refrescar el cache
        /// del modo acceso después de un enrolamiento o periódicamente.
        /// </summary>
        public async Task<int> RecargarTemplatesAsync()
        {
            try
            {
                var req  = new HttpRequestMessage(HttpMethod.Get, $"{ApiBase}/usuarios/con-template/lista");
                req.Headers.Add("X-Bridge-Secret", BridgeSecret);
                var resp = await _http.SendAsync(req);
                var json = await resp.Content.ReadAsStringAsync();
                var entries = HttpApi.ParseTemplateList(json);
                CargarTemplates(entries);
                return entries.Count;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[HUELLERO] Error recargando templates: {ex.Message}");
                return -1;
            }
        }

        // ============ Eventos del SDK ============

        public void OnComplete(object Capture, string ReaderSerialNumber, Sample Sample)
        {
            Console.WriteLine("[HUELLERO] Huella capturada");

            // Prioridad: enrolamiento manual > verificación one-shot > acceso permanente.
            if (_state.Activo)
            {
                ProcesarEnrolamiento(Sample);
            }
            else if (_state.VerifyActivo)
            {
                ProcesarVerificacion(Sample);
            }
            else if (_state.AccesoActivo)
            {
                ProcesarAcceso(Sample);
            }
            else
            {
                var extractor = new FeatureExtraction();
                var feedback  = CaptureFeedback.None;
                var features  = new FeatureSet();
                extractor.CreateFeatureSet(Sample, DataPurpose.Verification, ref feedback, ref features);
                if (feedback == CaptureFeedback.Good)
                {
                    var b64  = Convert.ToBase64String(features.Bytes);
                    _broadcast($"{{\"tipo\":\"featureset\",\"data\":\"{b64}\",\"reader\":\"{ReaderSerialNumber}\"}}");
                }
            }
        }

        private void ProcesarEnrolamiento(Sample Sample)
        {
            var extractor = new FeatureExtraction();
            var feedback  = CaptureFeedback.None;
            var features  = new FeatureSet();
            extractor.CreateFeatureSet(Sample, DataPurpose.Enrollment, ref feedback, ref features);

            if (feedback != CaptureFeedback.Good || features == null)
            {
                Console.WriteLine($"[HUELLERO] Captura no usable: {feedback}");
                _state.MarcarError($"Calidad insuficiente: {feedback}");
                return;
            }

            try { _enrollment.AddFeatures(features); }
            catch (Exception ex) { Console.WriteLine($"[HUELLERO] AddFeatures: {ex.Message}"); return; }

            _state.AvanzarPaso(_state.Total - (int)_enrollment.FeaturesNeeded);

            if (_enrollment.TemplateStatus == Enrollment.Status.Ready && _enrollment.Template != null)
            {
                var templateB64 = Convert.ToBase64String(_enrollment.Template.Bytes);
                _enrollment.Clear();
                var (uid, nombre) = _state.GetTarget();
                Console.WriteLine($"[HUELLERO] Template listo para usuario {uid} ({nombre}). Guardando...");
                Task.Run(() => GuardarTemplate(uid, templateB64));
            }
        }

        private void ProcesarVerificacion(Sample Sample)
        {
            var extractor = new FeatureExtraction();
            var feedback  = CaptureFeedback.None;
            var features  = new FeatureSet();
            extractor.CreateFeatureSet(Sample, DataPurpose.Verification, ref feedback, ref features);

            if (feedback != CaptureFeedback.Good || features == null)
            {
                Console.WriteLine($"[HUELLERO] Verificación — calidad insuficiente: {feedback}");
                _state.MarcarVerifyError($"Calidad insuficiente: {feedback}");
                return;
            }

            Console.WriteLine($"[HUELLERO] Comparando contra {_templates.Count} templates...");
            foreach (var entry in _templates)
            {
                try
                {
                    var tmpl = new Template();
                    tmpl.DeSerialize(Convert.FromBase64String(entry.Base64));

                    var result = new Verification.Result();
                    _verificator.Verify(features, tmpl, ref result);

                    if (result.Verified)
                    {
                        Console.WriteLine($"[HUELLERO] Coincidencia: usuario {entry.UsuarioId} ({entry.Nombre})");
                        _state.MarcarVerifyEncontrado(new VerifyResult { UsuarioId = entry.UsuarioId, Nombre = entry.Nombre });
                        _broadcast($"{{\"tipo\":\"verify_match\",\"usuario_id\":{entry.UsuarioId},\"nombre\":\"{entry.Nombre}\"}}");
                        return;
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"[HUELLERO] Error comparando template {entry.UsuarioId}: {ex.Message}");
                }
            }

            Console.WriteLine("[HUELLERO] No se encontró coincidencia.");
            _state.MarcarVerifyNoMatch();
            _broadcast("{\"tipo\":\"verify_no_match\"}");
        }

        private void ProcesarAcceso(Sample Sample)
        {
            var extractor = new FeatureExtraction();
            var feedback  = CaptureFeedback.None;
            var features  = new FeatureSet();
            extractor.CreateFeatureSet(Sample, DataPurpose.Verification, ref feedback, ref features);

            if (feedback != CaptureFeedback.Good || features == null)
            {
                Console.WriteLine($"[ACCESO] Calidad insuficiente: {feedback}");
                _state.RegistrarEvento(new AccesoEvento {
                    Acceso  = false,
                    Nombre  = "Lectura inválida",
                    Detalle = $"Calidad insuficiente: {feedback}",
                    Hora    = DateTime.Now.ToString("HH:mm:ss"),
                });
                _broadcast("{\"tipo\":\"acceso_calidad\"}");
                return;
            }

            foreach (var entry in _templates)
            {
                try
                {
                    var tmpl = new Template();
                    tmpl.DeSerialize(Convert.FromBase64String(entry.Base64));
                    var result = new Verification.Result();
                    _verificator.Verify(features, tmpl, ref result);
                    if (result.Verified)
                    {
                        // Cooldown: ignorar si ya se procesó este usuario hace menos de N segundos.
                        if (_ultimoAcceso.TryGetValue(entry.UsuarioId, out var ultimoTs) &&
                            (DateTime.UtcNow - ultimoTs).TotalSeconds < CooldownSegundos)
                        {
                            Console.WriteLine($"[ACCESO] Cooldown activo para {entry.Nombre} — ignorando captura.");
                            return;
                        }
                        _ultimoAcceso[entry.UsuarioId] = DateTime.UtcNow;

                        Console.WriteLine($"[ACCESO] Coincidencia: usuario {entry.UsuarioId} ({entry.Nombre})");
                        Task.Run(() => RegistrarAsistencia(entry.UsuarioId, entry.Nombre));
                        return;
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"[ACCESO] Error comparando template {entry.UsuarioId}: {ex.Message}");
                }
            }

            Console.WriteLine("[ACCESO] Huella no reconocida.");
            _state.RegistrarEvento(new AccesoEvento {
                Acceso  = false,
                Nombre  = "Huella no reconocida",
                Detalle = "Sin coincidencia en la base de datos",
                Hora    = DateTime.Now.ToString("HH:mm:ss"),
            });
            _broadcast("{\"tipo\":\"acceso_no_match\"}");
        }

        private async Task RegistrarAsistencia(int usuarioId, string nombre)
        {
            try
            {
                var req = new HttpRequestMessage(HttpMethod.Post, $"{ApiBase}/asistencia/por-usuario/{usuarioId}");
                req.Content = new StringContent("", Encoding.UTF8, "application/json");
                req.Headers.Add("X-Bridge-Secret", BridgeSecret);
                var resp = await _http.SendAsync(req);
                var body = await resp.Content.ReadAsStringAsync();

                if (resp.IsSuccessStatusCode)
                {
                    // Extraer el "tipo" devuelto (entrada|salida) sin parser JSON.
                    var tipoMatch = System.Text.RegularExpressions.Regex.Match(body, "\"tipo\"\\s*:\\s*\"(entrada|salida)\"");
                    var tipo = tipoMatch.Success ? tipoMatch.Groups[1].Value : "entrada";

                    Console.WriteLine($"[ACCESO] {tipo.ToUpper()} registrada para {nombre} (#{usuarioId})");

                    // Abrir la palanquera solo en ENTRADA: el torniquete controla el ingreso.
                    // En salida no se dispara el relé.
                    if (tipo == "entrada")
                        _relay?.Abrir();

                    _state.RegistrarEvento(new AccesoEvento {
                        UsuarioId = usuarioId,
                        Nombre    = nombre,
                        Tipo      = tipo,
                        Acceso    = true,
                        Hora      = DateTime.Now.ToString("HH:mm:ss"),
                    });
                    _broadcast($"{{\"tipo\":\"acceso_ok\",\"usuario_id\":{usuarioId},\"nombre\":\"{nombre}\",\"evento\":\"{tipo}\"}}");
                }
                else
                {
                    var detMatch = System.Text.RegularExpressions.Regex.Match(body, "\"detail\"\\s*:\\s*\"([^\"]+)\"");
                    var detalle  = detMatch.Success ? detMatch.Groups[1].Value : $"HTTP {resp.StatusCode}";
                    Console.WriteLine($"[ACCESO] Acceso denegado para {nombre}: {detalle}");
                    _state.RegistrarEvento(new AccesoEvento {
                        UsuarioId = usuarioId,
                        Nombre    = nombre,
                        Acceso    = false,
                        Detalle   = detalle,
                        Hora      = DateTime.Now.ToString("HH:mm:ss"),
                    });
                    _broadcast($"{{\"tipo\":\"acceso_denegado\",\"usuario_id\":{usuarioId},\"nombre\":\"{nombre}\"}}");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[ACCESO] Excepción registrando asistencia: {ex.Message}");
                _state.RegistrarEvento(new AccesoEvento {
                    UsuarioId = usuarioId,
                    Nombre    = nombre,
                    Acceso    = false,
                    Detalle   = ex.Message,
                    Hora      = DateTime.Now.ToString("HH:mm:ss"),
                });
            }
        }

        private async Task GuardarTemplate(int usuarioId, string templateB64)
        {
            try
            {
                var body    = $"{{\"template\":\"{templateB64}\"}}";
                var content = new StringContent(body, Encoding.UTF8, "application/json");
                var req     = new HttpRequestMessage(HttpMethod.Post, $"{ApiBase}/usuarios/{usuarioId}/huella-template");
                req.Content = content;
                req.Headers.Add("X-Bridge-Secret", BridgeSecret);
                var resp    = await _http.SendAsync(req);

                if (resp.IsSuccessStatusCode)
                {
                    Console.WriteLine($"[HUELLERO] Template guardado para usuario {usuarioId}.");
                    _state.MarcarCompletado();
                    _broadcast($"{{\"tipo\":\"enrol_ok\",\"usuario_id\":{usuarioId}}}");
                    // Refrescar cache para que el nuevo usuario funcione en modo acceso sin reiniciar.
                    _ = RecargarTemplatesAsync();
                }
                else
                {
                    var err = await resp.Content.ReadAsStringAsync();
                    Console.WriteLine($"[HUELLERO] Error al guardar template: {resp.StatusCode} - {err}");
                    _state.MarcarError($"Error al guardar: {resp.StatusCode}");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[HUELLERO] Excepción al guardar template: {ex.Message}");
                _state.MarcarError(ex.Message);
            }
        }

        public void OnFingerTouch(object Capture, string ReaderSerialNumber)
            => Console.WriteLine("[HUELLERO] Dedo colocado");

        public void OnFingerGone(object Capture, string ReaderSerialNumber)
            => Console.WriteLine("[HUELLERO] Dedo retirado");

        public void OnReaderConnect(object Capture, string ReaderSerialNumber)
        {
            _state.LectorConectado = true;
            Console.WriteLine($"[HUELLERO] Lector conectado: {ReaderSerialNumber}");
        }

        public void OnReaderDisconnect(object Capture, string ReaderSerialNumber)
        {
            _state.LectorConectado = false;
            Console.WriteLine($"[HUELLERO] Lector desconectado: {ReaderSerialNumber}");
        }

        public void OnSampleQuality(object Capture, string ReaderSerialNumber, CaptureFeedback CaptureFeedback)
        {
            if (CaptureFeedback != CaptureFeedback.Good)
                Console.WriteLine($"[HUELLERO] Calidad: {CaptureFeedback}");
        }
    }
}
