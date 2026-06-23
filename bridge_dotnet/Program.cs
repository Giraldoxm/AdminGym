using BridgeDP;

var builder = WebApplication.CreateBuilder(args);

var bridgeConfig = builder.Configuration.GetSection("Bridge").Get<BridgeConfig>()
    ?? throw new InvalidOperationException("Falta sección 'Bridge' en appsettings.json");

builder.Services.AddSingleton(bridgeConfig);
builder.Services.AddSingleton<EnrollmentState>();
builder.Services.AddSingleton<BackendClient>();
builder.Services.AddSingleton<FingerprintService>();
builder.Services.AddHostedService(sp => sp.GetRequiredService<FingerprintService>());

// Mantener nombres de propiedad tal cual (sin camelCase) — el frontend espera
// claves en snake_case: usuario_id, ultimo_evento, templates_en_cache, etc.
builder.Services.ConfigureHttpJsonOptions(opts =>
{
    opts.SerializerOptions.PropertyNamingPolicy = null;
    opts.SerializerOptions.DictionaryKeyPolicy = null;
});

builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy => policy
        .WithOrigins(bridgeConfig.AllowedOrigins)
        .AllowAnyMethod()
        .AllowAnyHeader());
});

builder.WebHost.UseUrls($"http://0.0.0.0:{bridgeConfig.Port}");

var app = builder.Build();
app.UseCors();

app.MapGet("/status", (FingerprintService fp, EnrollmentState st) =>
{
    return Results.Ok(new Dictionary<string, object?>
    {
        ["dispositivo"]        = fp.DeviceStatus,
        ["modo"]               = fp.Mode,
        ["ultimo_evento"]      = fp.LastEvent,
        ["enrolamiento"]       = st.Snapshot(),
        ["templates_en_cache"] = fp.CacheCount,
    });
});

app.MapPost("/enroll/{usuarioId:int}", (int usuarioId, string? nombre, EnrollmentState st, FingerprintService fp) =>
{
    if (st.IsActive)
        return Results.Ok(new { error = "Ya hay un enrolamiento en curso." });

    fp.StartEnrollment(usuarioId, string.IsNullOrWhiteSpace(nombre) ? $"Usuario #{usuarioId}" : nombre);
    return Results.Ok(new { mensaje = "Enrolamiento iniciado.", usuario_id = usuarioId });
});

app.MapDelete("/enroll", (FingerprintService fp) =>
{
    fp.CancelEnrollment();
    return Results.Ok(new { mensaje = "Enrolamiento cancelado." });
});

Console.WriteLine("=======================================================");
Console.WriteLine("  JainSportBox - Bridge .NET DigitalPersona U.are.U");
Console.WriteLine($"  API Bridge: http://localhost:{bridgeConfig.Port}");
Console.WriteLine($"  Backend:    {bridgeConfig.ApiBase}");
Console.WriteLine("=======================================================");

app.Run();

public sealed class BridgeConfig
{
    public int Port { get; set; } = 8001;
    public string ApiBase { get; set; } = "http://127.0.0.1:8000";
    public string EnvFile { get; set; } = "../../../../backend/.env";
    public int SamplesEnrol { get; set; } = 4;
    public int CacheRefreshSeconds { get; set; } = 60;
    public int Threshold1N { get; set; } = 2290;
    public string[] AllowedOrigins { get; set; } = Array.Empty<string>();
}
