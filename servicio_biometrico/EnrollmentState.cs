using System;

namespace HuelleroBridge
{
    public class VerifyResult
    {
        public int    UsuarioId { get; set; }
        public string Nombre    { get; set; }
    }

    public class AccesoEvento
    {
        public int     UsuarioId { get; set; }
        public string  Nombre    { get; set; }
        public string  Tipo      { get; set; }   // "entrada" | "salida"
        public bool    Acceso    { get; set; }   // true = OK, false = denegado/no-match
        public string  Detalle   { get; set; }   // mensaje de error si Acceso=false
        public string  Hora      { get; set; }   // ISO8601 local
    }

    public class EnrollmentState
    {
        private readonly object _lock = new object();

        // ── Lector ──────────────────────────────────────────────
        public bool LectorConectado { get; set; }

        // ── Enrolamiento ─────────────────────────────────────────
        public bool   Activo     { get; private set; }
        public int?   UsuarioId  { get; private set; }
        public string Nombre     { get; private set; }
        public int    Paso       { get; private set; }
        public int    Total      { get; private set; } = 4;
        public bool   Completado { get; private set; }
        public bool   Error      { get; private set; }
        public string Mensaje    { get; private set; } = "";

        // ── Acceso (modo permanente, gimnasio en horario) ────────
        public bool         AccesoActivo    { get; private set; }
        public int          TemplatesEnCache { get; set; }
        public AccesoEvento UltimoEvento    { get; private set; }

        // ── Verificación ──────────────────────────────────────────
        public bool         VerifyActivo    { get; private set; }
        public bool         VerifyEspera    { get; private set; }  // esperando dedo
        public VerifyResult VerifyResultado { get; private set; }  // null = no encontrado aún
        public bool         VerifyNoMatch   { get; private set; }  // huella no reconocida
        public bool         VerifyError     { get; private set; }
        public string       VerifyMensaje   { get; private set; } = "";

        // ── Enrolamiento: métodos ────────────────────────────────

        public void IniciarEnrolamiento(int usuarioId, string nombre)
        {
            lock (_lock)
            {
                CancelarVerify();
                Activo     = true;
                UsuarioId  = usuarioId;
                Nombre     = nombre;
                Paso       = 0;
                Completado = false;
                Error      = false;
                Mensaje    = "Coloca el dedo en el lector";
            }
        }

        public void AvanzarPaso(int paso)
        {
            lock (_lock) { Paso = paso; Mensaje = $"Muestra {paso} de {Total} capturada"; }
        }

        public void MarcarCompletado()
        {
            lock (_lock) { Completado = true; Activo = false; Mensaje = "Huella registrada correctamente"; }
        }

        public void MarcarError(string mensaje)
        {
            lock (_lock) { Error = true; Activo = false; Mensaje = mensaje; }
        }

        public void Cancelar()
        {
            lock (_lock)
            {
                Activo = false; UsuarioId = null; Nombre = null;
                Paso = 0; Completado = false; Error = false; Mensaje = "";
            }
        }

        public (int id, string nombre) GetTarget()
        {
            lock (_lock) return (UsuarioId ?? 0, Nombre ?? "");
        }

        // ── Verificación: métodos ────────────────────────────────

        public void IniciarVerify()
        {
            lock (_lock)
            {
                Cancelar();
                VerifyActivo  = true;
                VerifyEspera  = true;
                VerifyResultado = null;
                VerifyNoMatch = false;
                VerifyError   = false;
                VerifyMensaje = "Coloca el dedo en el lector";
            }
        }

        public void MarcarVerifyEncontrado(VerifyResult resultado)
        {
            lock (_lock)
            {
                VerifyActivo    = false;
                VerifyEspera    = false;
                VerifyResultado = resultado;
                VerifyNoMatch   = false;
                VerifyMensaje   = $"Usuario identificado: {resultado.Nombre}";
            }
        }

        public void MarcarVerifyNoMatch()
        {
            lock (_lock)
            {
                VerifyActivo  = false;
                VerifyEspera  = false;
                VerifyNoMatch = true;
                VerifyMensaje = "Huella no reconocida";
            }
        }

        public void MarcarVerifyError(string mensaje)
        {
            lock (_lock)
            {
                VerifyActivo  = false;
                VerifyEspera  = false;
                VerifyError   = true;
                VerifyMensaje = mensaje;
            }
        }

        public void CancelarVerify()
        {
            lock (_lock)
            {
                VerifyActivo    = false;
                VerifyEspera    = false;
                VerifyResultado = null;
                VerifyNoMatch   = false;
                VerifyError     = false;
                VerifyMensaje   = "";
            }
        }

        // ── Acceso: métodos ──────────────────────────────────────

        public void IniciarAcceso()
        {
            lock (_lock) { AccesoActivo = true; }
        }

        public void DetenerAcceso()
        {
            lock (_lock) { AccesoActivo = false; }
        }

        public void RegistrarEvento(AccesoEvento ev)
        {
            lock (_lock) { UltimoEvento = ev; }
        }
    }
}
