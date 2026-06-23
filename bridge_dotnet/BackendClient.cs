using System.Net;
using System.Net.Http.Headers;
using System.Net.Http.Json;
using System.Text.Json.Serialization;

namespace BridgeDP;

public sealed class BackendClient
{
    private readonly HttpClient _http;
    private readonly BridgeConfig _config;
    private readonly ILogger<BackendClient> _log;

    public BackendClient(BridgeConfig config, ILogger<BackendClient> log)
    {
        _config = config;
        _log = log;
        _http = new HttpClient
        {
            BaseAddress = new Uri(config.ApiBase),
            Timeout = TimeSpan.FromSeconds(5),
        };
    }

    public async Task<bool> LoginAsync(CancellationToken ct = default)
    {
        var (email, password) = ReadAdminCreds();
        if (string.IsNullOrEmpty(email) || string.IsNullOrEmpty(password))
        {
            _log.LogWarning("No hay credenciales de admin en {EnvFile}", _config.EnvFile);
            return false;
        }

        try
        {
            using var form = new FormUrlEncodedContent(new[]
            {
                new KeyValuePair<string, string>("username", email),
                new KeyValuePair<string, string>("password", password),
            });
            using var resp = await _http.PostAsync("/login", form, ct);
            if (!resp.IsSuccessStatusCode) return false;

            var body = await resp.Content.ReadFromJsonAsync<LoginResponse>(cancellationToken: ct);
            if (string.IsNullOrEmpty(body?.AccessToken)) return false;

            _http.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", body.AccessToken);
            return true;
        }
        catch (Exception ex)
        {
            _log.LogWarning(ex, "Error al autenticar con backend");
            return false;
        }
    }

    public async Task<List<TemplateRecord>> FetchTemplatesAsync(CancellationToken ct = default)
    {
        try
        {
            using var resp = await _http.GetAsync("/usuarios/con-template/lista", ct);
            if (!resp.IsSuccessStatusCode) return new();
            return await resp.Content.ReadFromJsonAsync<List<TemplateRecord>>(cancellationToken: ct) ?? new();
        }
        catch (Exception ex)
        {
            _log.LogWarning(ex, "Error al obtener templates");
            return new();
        }
    }

    public async Task<AsistenciaResult?> RegistrarAsistenciaAsync(int usuarioId, CancellationToken ct = default)
    {
        try
        {
            using var resp = await _http.PostAsync($"/asistencia/por-usuario/{usuarioId}", null, ct);

            if (resp.StatusCode == HttpStatusCode.Created)
            {
                var data = await resp.Content.ReadFromJsonAsync<AsistenciaPayload>(cancellationToken: ct);
                return new AsistenciaResult { Tipo = data?.Tipo ?? "entrada" };
            }

            if (resp.StatusCode == HttpStatusCode.Forbidden)
            {
                var data = await resp.Content.ReadFromJsonAsync<ErrorPayload>(cancellationToken: ct);
                return new AsistenciaResult { Error = data?.Detail ?? "Membresía vencida" };
            }
        }
        catch (Exception ex)
        {
            _log.LogWarning(ex, "Error al registrar asistencia para usuario {Id}", usuarioId);
            return new AsistenciaResult { Error = ex.Message };
        }
        return null;
    }

    public async Task<bool> GuardarTemplateAsync(int usuarioId, byte[] fmd, CancellationToken ct = default)
    {
        try
        {
            var b64 = Convert.ToBase64String(fmd);
            using var resp = await _http.PostAsJsonAsync(
                $"/usuarios/{usuarioId}/huella-template",
                new { template = b64 },
                ct);
            return resp.IsSuccessStatusCode;
        }
        catch (Exception ex)
        {
            _log.LogWarning(ex, "Error al guardar template para usuario {Id}", usuarioId);
            return false;
        }
    }

    private (string email, string password) ReadAdminCreds()
    {
        try
        {
            var path = Path.GetFullPath(Path.Combine(AppContext.BaseDirectory, _config.EnvFile));
            if (!File.Exists(path))
            {
                _log.LogWarning("No se encontró .env en {Path}", path);
                return ("", "");
            }

            string email = "", password = "";
            foreach (var line in File.ReadAllLines(path))
            {
                if (string.IsNullOrWhiteSpace(line) || line.StartsWith("#")) continue;
                var idx = line.IndexOf('=');
                if (idx < 0) continue;
                var key = line[..idx].Trim();
                var value = line[(idx + 1)..].Trim();
                if (key == "ADMIN_EMAIL") email = value;
                else if (key == "ADMIN_PASSWORD") password = value;
            }
            return (email, password);
        }
        catch (Exception ex)
        {
            _log.LogWarning(ex, "Error leyendo .env");
            return ("", "");
        }
    }

    public sealed class LoginResponse
    {
        [JsonPropertyName("access_token")] public string? AccessToken { get; set; }
    }

    public sealed class TemplateRecord
    {
        [JsonPropertyName("id")] public int Id { get; set; }
        [JsonPropertyName("nombre")] public string Nombre { get; set; } = "";
        [JsonPropertyName("template")] public string Template { get; set; } = "";
    }

    public sealed class AsistenciaPayload
    {
        [JsonPropertyName("tipo")] public string? Tipo { get; set; }
    }

    public sealed class ErrorPayload
    {
        [JsonPropertyName("detail")] public string? Detail { get; set; }
    }

    public sealed class AsistenciaResult
    {
        public string? Tipo { get; set; }
        public string? Error { get; set; }
    }
}
