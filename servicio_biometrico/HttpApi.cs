using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Net.Http;
using System.Text;
using System.Threading;

namespace HuelleroBridge
{
    public class HttpApi
    {
        private readonly HttpListener    _listener;
        private readonly EnrollmentState _state;
        private readonly FingerprintCapture _capture;
        private readonly RelayController _relay;
        private Thread _thread;

        // Configurables por entorno (JSB_API_BASE / BRIDGE_SECRET). Ver BridgeConfig.
        private static readonly string BridgeSecret = BridgeConfig.BridgeSecret;
        private static readonly string ApiBase      = BridgeConfig.ApiBase;
        private static readonly HttpClient _http = new HttpClient();

        public HttpApi(EnrollmentState state, FingerprintCapture capture, RelayController relay, int port = 8001)
        {
            _state   = state;
            _capture = capture;
            _relay   = relay;
            _listener = new HttpListener();
            _listener.Prefixes.Add($"http://localhost:{port}/");
        }

        public void Start()
        {
            _listener.Start();
            _thread = new Thread(Loop) { IsBackground = true };
            _thread.Start();
            Console.WriteLine("[HTTP] API REST escuchando en http://localhost:8001");
        }

        private void Loop()
        {
            while (_listener.IsListening)
            {
                try { var ctx = _listener.GetContext(); ThreadPool.QueueUserWorkItem(_ => Handle(ctx)); }
                catch { }
            }
        }

        private void Handle(HttpListenerContext ctx)
        {
            ctx.Response.Headers.Add("Access-Control-Allow-Origin", "*");
            ctx.Response.Headers.Add("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS");
            ctx.Response.Headers.Add("Access-Control-Allow-Headers", "Content-Type");
            ctx.Response.ContentType = "application/json";

            var method = ctx.Request.HttpMethod;
            var path   = ctx.Request.Url.AbsolutePath.TrimEnd('/');

            if (method == "OPTIONS") { ctx.Response.StatusCode = 204; ctx.Response.Close(); return; }

            try
            {
                if      (method == "GET"    && path == "/status")          HandleStatus(ctx);
                else if (method == "POST"   && path.StartsWith("/enroll/")) HandleEnrollStart(ctx, path);
                else if (method == "DELETE" && path == "/enroll")           HandleEnrollCancel(ctx);
                else if (method == "POST"   && path == "/verify/start")     HandleVerifyStart(ctx);
                else if (method == "DELETE" && path == "/verify")           HandleVerifyCancel(ctx);
                else if (method == "POST"   && path == "/access/reload")    HandleAccessReload(ctx);
                else if (method == "POST"   && path == "/palanquera/abrir") HandleAbrirPalanquera(ctx);
                else { ctx.Response.StatusCode = 404; Write(ctx, "{\"error\":\"not found\"}"); }
            }
            catch (Exception ex)
            {
                ctx.Response.StatusCode = 500;
                Write(ctx, $"{{\"error\":\"{Esc(ex.Message)}\"}}");
            }
        }

        private void HandleStatus(HttpListenerContext ctx)
        {
            var e  = _state;
            var vr = e.VerifyResultado;
            var ev = e.UltimoEvento;
            var dispositivo = e.LectorConectado ? "conectado" : "desconectado";
            var modo = e.Activo
                ? "enrolando"
                : e.VerifyActivo ? "verificando"
                : e.AccesoActivo ? "acceso"
                : "idle";

            var verJson = $@"{{
    ""activo"": {B(e.VerifyActivo)},
    ""espera"": {B(e.VerifyEspera)},
    ""encontrado"": {B(vr != null)},
    ""no_match"": {B(e.VerifyNoMatch)},
    ""error"": {B(e.VerifyError)},
    ""mensaje"": ""{Esc(e.VerifyMensaje)}"",
    ""usuario"": {(vr != null ? $"{{\"id\":{vr.UsuarioId},\"nombre\":\"{Esc(vr.Nombre)}\"}}" : "null")}
  }}";

            var ultimoEventoJson = ev == null
                ? "null"
                : $@"{{
    ""usuario_id"": {ev.UsuarioId},
    ""nombre"": ""{Esc(ev.Nombre)}"",
    ""tipo"": ""{Esc(ev.Tipo ?? "")}"",
    ""acceso"": {B(ev.Acceso)},
    ""detalle"": ""{Esc(ev.Detalle ?? "")}"",
    ""hora"": ""{Esc(ev.Hora ?? "")}""
  }}";

            var json = $@"{{
  ""dispositivo"": ""{dispositivo}"",
  ""modo"": ""{modo}"",
  ""templates_en_cache"": {e.TemplatesEnCache},
  ""acceso_activo"": {B(e.AccesoActivo)},
  ""ultimo_evento"": {ultimoEventoJson},
  ""enrolamiento"": {{
    ""activo"": {B(e.Activo)},
    ""usuario_id"": {(e.UsuarioId.HasValue ? e.UsuarioId.Value.ToString() : "null")},
    ""nombre"": {(e.Nombre != null ? $"\"{Esc(e.Nombre)}\"" : "null")},
    ""paso"": {e.Paso},
    ""total"": {e.Total},
    ""completado"": {B(e.Completado)},
    ""error"": {B(e.Error)},
    ""mensaje"": ""{Esc(e.Mensaje)}""
  }},
  ""verificacion"": {verJson}
}}";
            Write(ctx, json);
        }

        private void HandleEnrollStart(HttpListenerContext ctx, string path)
        {
            var parts = path.Split('/');
            if (!int.TryParse(parts[parts.Length - 1], out int uid))
            { ctx.Response.StatusCode = 400; Write(ctx, "{\"error\":\"usuario_id invalido\"}"); return; }

            var nombre = Uri.UnescapeDataString(ctx.Request.QueryString["nombre"] ?? "");
            _state.IniciarEnrolamiento(uid, nombre);
            Write(ctx, "{\"ok\":true}");
            Console.WriteLine($"[HTTP] Enrolamiento iniciado: usuario {uid} ({nombre})");
        }

        private void HandleEnrollCancel(HttpListenerContext ctx)
        {
            _state.Cancelar();
            Write(ctx, "{\"ok\":true}");
            Console.WriteLine("[HTTP] Enrolamiento cancelado");
        }

        private void HandleVerifyStart(HttpListenerContext ctx)
        {
            System.Threading.Tasks.Task.Run(async () =>
            {
                try
                {
                    var req  = new HttpRequestMessage(HttpMethod.Get, $"{ApiBase}/usuarios/con-template/lista");
                    req.Headers.Add("X-Bridge-Secret", BridgeSecret);
                    var resp = await _http.SendAsync(req);
                    var json = await resp.Content.ReadAsStringAsync();

                    // Parse JSON manualmente: [{"id":N,"nombre":"...","template":"..."}]
                    var entries = ParseTemplateList(json);
                    _capture.CargarTemplates(entries);
                    _state.IniciarVerify();
                    Console.WriteLine($"[HTTP] Verificación iniciada con {entries.Count} templates.");
                }
                catch (Exception ex)
                {
                    _state.MarcarVerifyError($"No se pudieron cargar templates: {ex.Message}");
                    Console.WriteLine($"[HTTP] Error al cargar templates: {ex.Message}");
                }
            });

            Write(ctx, "{\"ok\":true}");
        }

        private void HandleVerifyCancel(HttpListenerContext ctx)
        {
            _state.CancelarVerify();
            Write(ctx, "{\"ok\":true}");
            Console.WriteLine("[HTTP] Verificación cancelada");
        }

        // Apertura manual de la palanquera desde el frontend (admin/coach). Útil cuando
        // la huella no se reconoce o entra un invitado. No registra asistencia.
        private void HandleAbrirPalanquera(HttpListenerContext ctx)
        {
            if (_relay == null)
            {
                ctx.Response.StatusCode = 503;
                Write(ctx, "{\"ok\":false,\"error\":\"relay no disponible\"}");
                return;
            }
            // Abrir en segundo plano: la primera conexión al Arduino puede bloquear ~2 s.
            System.Threading.Tasks.Task.Run(() => _relay.Abrir());
            Console.WriteLine("[HTTP] Apertura manual de palanquera solicitada.");
            Write(ctx, "{\"ok\":true}");
        }

        private void HandleAccessReload(HttpListenerContext ctx)
        {
            System.Threading.Tasks.Task.Run(async () =>
            {
                var n = await _capture.RecargarTemplatesAsync();
                Console.WriteLine($"[HTTP] Templates recargados: {n}");
            });
            Write(ctx, "{\"ok\":true}");
        }

        internal static List<TemplateEntry> ParseTemplateList(string json)
        {
            var result = new List<TemplateEntry>();
            // Simple parser para el array JSON del backend
            // Formato: [{"id":2,"nombre":"Jhon","template":"base64..."},...]
            var items = json.Trim().TrimStart('[').TrimEnd(']').Split(new string[] { "},{" }, StringSplitOptions.None);
            foreach (var item in items)
            {
                var clean = item.Trim('{', '}', ' ');
                var entry = new TemplateEntry();
                foreach (var kv in clean.Split(','))
                {
                    var colon = kv.IndexOf(':');
                    if (colon < 0) continue;
                    var key = kv.Substring(0, colon).Trim().Trim('"');
                    var val = kv.Substring(colon + 1).Trim().Trim('"');
                    if (key == "id")       int.TryParse(val, out int id_parsed) ; // set below
                    if (key == "nombre")   entry.Nombre  = val;
                    if (key == "template") entry.Base64  = val;
                }
                // Re-parse id correctly
                var idMatch = System.Text.RegularExpressions.Regex.Match(clean, "\"id\"\\s*:\\s*(\\d+)");
                if (idMatch.Success) entry.UsuarioId = int.Parse(idMatch.Groups[1].Value);
                if (entry.UsuarioId > 0 && !string.IsNullOrEmpty(entry.Base64))
                    result.Add(entry);
            }
            return result;
        }

        private static void Write(HttpListenerContext ctx, string body)
        {
            var bytes = Encoding.UTF8.GetBytes(body);
            ctx.Response.ContentLength64 = bytes.Length;
            ctx.Response.OutputStream.Write(bytes, 0, bytes.Length);
            ctx.Response.Close();
        }

        private static string B(bool v)   => v ? "true" : "false";
        private static string Esc(string s) => s?.Replace("\\", "\\\\").Replace("\"", "\\\"") ?? "";
    }
}
