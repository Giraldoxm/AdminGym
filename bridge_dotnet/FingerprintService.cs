using DPUruNet;

namespace BridgeDP;

public sealed class FingerprintService : BackgroundService
{
    private readonly BridgeConfig _config;
    private readonly EnrollmentState _enrolState;
    private readonly BackendClient _backend;
    private readonly ILogger<FingerprintService> _log;

    private Reader? _reader;
    private List<CachedTemplate> _templates = new();
    private readonly object _cacheLock = new();
    private DateTime _lastCacheRefresh = DateTime.MinValue;
    private CancellationTokenSource _cancelEnrol = new();

    private string _deviceStatus = "iniciando";
    private string _mode = "iniciando";
    private object? _lastEvent;

    public FingerprintService(
        BridgeConfig config,
        EnrollmentState enrolState,
        BackendClient backend,
        ILogger<FingerprintService> log)
    {
        _config = config;
        _enrolState = enrolState;
        _backend = backend;
        _log = log;
    }

    public string DeviceStatus { get { lock (_cacheLock) return _deviceStatus; } }
    public string Mode { get { lock (_cacheLock) return _mode; } }
    public object? LastEvent { get { lock (_cacheLock) return _lastEvent; } }
    public int CacheCount { get { lock (_cacheLock) return _templates.Count; } }

    public void StartEnrollment(int usuarioId, string usuarioNombre)
    {
        _cancelEnrol = new CancellationTokenSource();
        _enrolState.Begin(usuarioId, usuarioNombre, _config.SamplesEnrol);
        SetMode("enrolando");
    }

    public void CancelEnrollment()
    {
        _cancelEnrol.Cancel();
        try { _reader?.CancelCapture(); } catch { /* ignore */ }
        _enrolState.Fail("Cancelado por el usuario.");
        SetMode(_reader != null ? "identificando" : "esperando");
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        await Task.Yield();

        for (int i = 0; i < 10 && !stoppingToken.IsCancellationRequested; i++)
        {
            if (await _backend.LoginAsync(stoppingToken))
            {
                _log.LogInformation("Autenticado con backend");
                break;
            }
            await SafeDelay(2000, stoppingToken);
        }

        await RefreshCacheAsync(stoppingToken);

        if (!OpenReader())
        {
            _log.LogWarning("No se pudo abrir el lector. El bridge se mantendrá en espera.");
            SetDeviceStatus("no_disponible");
            SetMode("esperando");
            await SafeDelay(Timeout.Infinite, stoppingToken);
            return;
        }

        SetDeviceStatus("conectado");
        SetMode("identificando");

        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                var modo = Mode;
                if (modo == "identificando")
                {
                    await IdentificationStepAsync(stoppingToken);
                }
                else if (modo == "enrolando")
                {
                    await EnrollmentLoopAsync(stoppingToken);
                }
                else
                {
                    await SafeDelay(200, stoppingToken);
                }
            }
            catch (OperationCanceledException) when (stoppingToken.IsCancellationRequested)
            {
                break;
            }
            catch (Exception ex)
            {
                _log.LogError(ex, "Error en bucle principal");
                await SafeDelay(500, stoppingToken);
            }
        }

        try { _reader?.Dispose(); } catch { /* ignore */ }
    }

    // ── Lector ────────────────────────────────────────────────────────────────

    private bool OpenReader()
    {
        try
        {
            var readers = ReaderCollection.GetReaders();
            if (readers.Count == 0)
            {
                _log.LogError("No hay lectores conectados.");
                return false;
            }

            _reader = readers[0];
            var open = _reader.Open(Constants.CapturePriority.DP_PRIORITY_COOPERATIVE);
            if (open != Constants.ResultCode.DP_SUCCESS)
            {
                _log.LogError("Reader.Open falló: {Code}", open);
                return false;
            }

            _log.LogInformation(
                "Lector conectado: {Name} (SN: {Sn})",
                _reader.Description.Name,
                _reader.Description.SerialNumber);
            return true;
        }
        catch (FileNotFoundException)
        {
            _log.LogError(
                "DPUruNet.dll no encontrado. Copia el archivo a bridge_dotnet/lib/DPUruNet.dll. " +
                "Ruta típica: C:\\Program Files\\DigitalPersona\\U.are.U SDK\\Windows\\Lib\\DotNet\\DPUruNet.dll");
            return false;
        }
        catch (Exception ex)
        {
            _log.LogError(ex, "Error al abrir lector");
            return false;
        }
    }

    // ── Identificación ────────────────────────────────────────────────────────

    private async Task IdentificationStepAsync(CancellationToken stoppingToken)
    {
        var fmd = CaptureFmd(timeoutMs: 3000);
        if (fmd == null)
        {
            await SafeDelay(300, stoppingToken);
            return;
        }

        if ((DateTime.UtcNow - _lastCacheRefresh).TotalSeconds > _config.CacheRefreshSeconds)
            await RefreshCacheAsync(stoppingToken);

        var match = Identify(fmd);
        if (match == null)
        {
            SetLastEvent("desconocido", "Huella no reconocida", false, "Sin coincidencia");
            _log.LogInformation("[DENEGADO] Huella no reconocida");
            return;
        }

        var resultado = await _backend.RegistrarAsistenciaAsync(match.Id, stoppingToken);
        if (resultado == null) return;

        if (resultado.Error != null)
        {
            SetLastEvent("entrada", match.Nombre, false, resultado.Error);
            _log.LogInformation("[DENEGADO] {Nombre}: {Error}", match.Nombre, resultado.Error);
        }
        else
        {
            var tipo = resultado.Tipo ?? "entrada";
            SetLastEvent(tipo, match.Nombre, true, "");
            _log.LogInformation("[OK] {Tipo} - {Nombre}", tipo.ToUpper(), match.Nombre);
        }
    }

    // ── Enrolamiento ──────────────────────────────────────────────────────────

    private async Task EnrollmentLoopAsync(CancellationToken stoppingToken)
    {
        using var combined = CancellationTokenSource.CreateLinkedTokenSource(stoppingToken, _cancelEnrol.Token);
        var samples = new List<Fmd>();

        for (int paso = 1; paso <= _config.SamplesEnrol; paso++)
        {
            if (combined.IsCancellationRequested)
            {
                _enrolState.Fail("Enrolamiento cancelado.");
                SetMode("identificando");
                return;
            }

            _enrolState.Update(paso, $"Coloca el dedo firmemente ({paso}/{_config.SamplesEnrol})");
            _log.LogInformation("[ENROL] Muestra {Paso}/{Total} - {Nombre}",
                paso, _config.SamplesEnrol, _enrolState.UsuarioNombre);

            Fmd? fmd = null;
            int reintentos = 0;
            while (fmd == null && !combined.IsCancellationRequested)
            {
                fmd = CaptureFmdRaw(timeoutMs: -1);
                if (fmd == null && !combined.IsCancellationRequested)
                {
                    reintentos++;
                    _enrolState.Update(paso, $"Huella borrosa, vuelve a intentar ({paso}/{_config.SamplesEnrol})");
                    _log.LogInformation("[ENROL] Captura {Paso} fallida (intento {N}), reintentando...", paso, reintentos);
                    await SafeDelay(400, stoppingToken);
                }
            }

            if (fmd == null)
            {
                _enrolState.Fail("Enrolamiento cancelado.");
                SetMode("identificando");
                return;
            }

            samples.Add(fmd);
            _log.LogInformation("[ENROL] Muestra {Paso}/{Total} OK", paso, _config.SamplesEnrol);

            if (paso < _config.SamplesEnrol)
            {
                _enrolState.Update(paso, "Levanta el dedo...");
                await SafeDelay(1500, stoppingToken);
            }
        }

        _enrolState.Update(_config.SamplesEnrol, "Procesando huella...");

        var enroll = Enrollment.CreateEnrollmentFmd(Constants.Formats.Fmd.ANSI, samples);
        if (enroll.ResultCode != Constants.ResultCode.DP_SUCCESS || enroll.Data == null)
        {
            _log.LogWarning("CreateEnrollmentFmd falló: {Code}", enroll.ResultCode);
            _enrolState.Fail("Error al crear el template.");
            SetMode("identificando");
            return;
        }

        var bytes = enroll.Data.Bytes;
        var usuarioId = _enrolState.UsuarioId ?? 0;
        var nombre = _enrolState.UsuarioNombre ?? $"Usuario #{usuarioId}";

        var ok = await _backend.GuardarTemplateAsync(usuarioId, bytes, stoppingToken);
        if (!ok)
        {
            _enrolState.Fail("Error al guardar en el servidor.");
            SetMode("identificando");
            return;
        }

        await RefreshCacheAsync(stoppingToken);
        _enrolState.Finish($"Huella de {nombre} registrada correctamente.");
        SetMode("identificando");
        _log.LogInformation("[OK] Enrolamiento completado para {Nombre}", nombre);
    }

    // ── SDK helpers ───────────────────────────────────────────────────────────

    private Fmd? CaptureFmdRaw(int timeoutMs)
    {
        if (_reader == null) return null;
        try
        {
            var resolutions = _reader.Capabilities.Resolutions;
            if (resolutions == null || resolutions.Length == 0) return null;
            var resolution = resolutions[0];

            var capture = _reader.Capture(
                Constants.Formats.Fid.ANSI,
                Constants.CaptureProcessing.DP_IMG_PROC_ENHANCED,
                timeoutMs,
                resolution);

            if (capture == null || capture.ResultCode != Constants.ResultCode.DP_SUCCESS) return null;
            if (capture.Quality != Constants.CaptureQuality.DP_QUALITY_GOOD) return null;
            if (capture.Data == null) return null;

            var fmd = FeatureExtraction.CreateFmdFromFid(capture.Data, Constants.Formats.Fmd.ANSI);
            if (fmd.ResultCode != Constants.ResultCode.DP_SUCCESS || fmd.Data == null) return null;
            return fmd.Data;
        }
        catch (Exception ex)
        {
            _log.LogWarning(ex, "Error en captura SDK");
            return null;
        }
    }

    private byte[]? CaptureFmd(int timeoutMs) => CaptureFmdRaw(timeoutMs)?.Bytes;

    private IdentifyMatch? Identify(byte[] probeBytes)
    {
        var probe = ImportFmd(probeBytes);
        if (probe == null) return null;

        List<CachedTemplate> snapshot;
        lock (_cacheLock) snapshot = _templates.ToList();

        int? bestScore = null;
        IdentifyMatch? best = null;

        foreach (var t in snapshot)
        {
            var cmp = Comparison.Compare(probe, 0, t.Fmd, 0);
            if (cmp.ResultCode != Constants.ResultCode.DP_SUCCESS) continue;
            int score = cmp.Score;
            if (bestScore == null || score < bestScore)
            {
                bestScore = score;
                best = new IdentifyMatch(t.UserId, t.Name);
            }
        }

        return bestScore != null && bestScore <= _config.Threshold1N ? best : null;
    }

    private static Fmd? ImportFmd(byte[] bytes)
    {
        try
        {
            var result = Importer.ImportFmd(bytes, Constants.Formats.Fmd.ANSI, Constants.Formats.Fmd.ANSI);
            return result.ResultCode == Constants.ResultCode.DP_SUCCESS ? result.Data : null;
        }
        catch
        {
            return null;
        }
    }

    private async Task RefreshCacheAsync(CancellationToken ct)
    {
        var records = await _backend.FetchTemplatesAsync(ct);
        var nuevos = new List<CachedTemplate>();
        foreach (var r in records)
        {
            try
            {
                var bytes = Convert.FromBase64String(r.Template);
                var fmd = ImportFmd(bytes);
                if (fmd != null) nuevos.Add(new CachedTemplate(r.Id, r.Nombre, fmd));
            }
            catch { /* skip malformed */ }
        }
        lock (_cacheLock) _templates = nuevos;
        _lastCacheRefresh = DateTime.UtcNow;
        _log.LogInformation("Cache refrescado: {Count} templates", nuevos.Count);
    }

    // ── State setters ─────────────────────────────────────────────────────────

    private void SetMode(string modo)
    {
        lock (_cacheLock) _mode = modo;
    }

    private void SetDeviceStatus(string estado)
    {
        lock (_cacheLock) _deviceStatus = estado;
    }

    private void SetLastEvent(string tipo, string nombre, bool acceso, string detalle)
    {
        var ev = new Dictionary<string, object?>
        {
            ["tipo"]    = tipo,
            ["nombre"]  = nombre,
            ["acceso"]  = acceso,
            ["detalle"] = detalle,
            ["hora"]    = DateTime.Now.ToString("HH:mm:ss"),
        };
        lock (_cacheLock) _lastEvent = ev;
    }

    private static async Task SafeDelay(int ms, CancellationToken ct)
    {
        try { await Task.Delay(ms, ct); }
        catch (OperationCanceledException) { /* ignore */ }
    }

    // ── Tipos auxiliares ──────────────────────────────────────────────────────

    private sealed record CachedTemplate(int UserId, string Name, Fmd Fmd);
    private sealed record IdentifyMatch(int Id, string Nombre);
}
