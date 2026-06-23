namespace BridgeDP;

public sealed class EnrollmentState
{
    private readonly object _lock = new();

    public bool Activo { get; private set; }
    public int? UsuarioId { get; private set; }
    public string? UsuarioNombre { get; private set; }
    public int Paso { get; private set; }
    public int Total { get; private set; }
    public string Mensaje { get; private set; } = "";
    public bool Completado { get; private set; }
    public string? Error { get; private set; }

    public bool IsActive { get { lock (_lock) return Activo; } }

    public void Begin(int usuarioId, string usuarioNombre, int total)
    {
        lock (_lock)
        {
            Activo = true;
            UsuarioId = usuarioId;
            UsuarioNombre = usuarioNombre;
            Paso = 0;
            Total = total;
            Mensaje = "Iniciando enrolamiento...";
            Completado = false;
            Error = null;
        }
    }

    public void Update(int paso, string mensaje)
    {
        lock (_lock)
        {
            Paso = paso;
            Mensaje = mensaje;
        }
    }

    public void Finish(string mensaje)
    {
        lock (_lock)
        {
            Activo = false;
            Completado = true;
            Mensaje = mensaje;
        }
    }

    public void Fail(string error)
    {
        lock (_lock)
        {
            Activo = false;
            Error = error;
        }
    }

    public Dictionary<string, object?> Snapshot()
    {
        lock (_lock)
        {
            return new Dictionary<string, object?>
            {
                ["activo"]         = Activo,
                ["usuario_id"]     = UsuarioId,
                ["usuario_nombre"] = UsuarioNombre,
                ["paso"]           = Paso,
                ["total"]          = Total,
                ["mensaje"]        = Mensaje,
                ["completado"]     = Completado,
                ["error"]          = Error,
            };
        }
    }
}
