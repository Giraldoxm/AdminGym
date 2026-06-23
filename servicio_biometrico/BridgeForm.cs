using System;
using System.Drawing;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace HuelleroBridge
{

    // Ventana invisible — solo existe para proveer el HWND y message pump COM que
    // necesita el SDK de DigitalPersona para despachar eventos. Se posiciona fuera de
    // pantalla con tamaño 1×1 y opacidad 0 para que nunca sea visible. La captura en
    // background no depende de esta ventana sino de Priority.High en FingerprintCapture.
    internal class BridgeForm : Form
    {
        private readonly FingerprintCapture _capture;
        private readonly EnrollmentState    _state;
        private readonly RelayController    _relay;
        private System.Windows.Forms.Timer  _reloadTimer;

        public FingerprintCapture Capture => _capture;
        public RelayController    Relay   => _relay;

        // No activar la ventana al mostrarse (el HWND existe pero nunca toma foco)
        protected override bool ShowWithoutActivation => true;

        public BridgeForm(EnrollmentState state, WebSocketHub hub)
        {
            ShowInTaskbar   = false;
            FormBorderStyle = FormBorderStyle.None;
            WindowState     = FormWindowState.Normal;
            StartPosition   = FormStartPosition.Manual;
            Location        = new Point(-32000, -32000);
            Width           = 1;
            Height          = 1;
            Opacity         = 0;

            _state   = state;
            _relay   = new RelayController();
            _capture = new FingerprintCapture(state, json => hub.Broadcast(json), _relay);
        }

        protected override void OnLoad(EventArgs e)
        {
            base.OnLoad(e);
            // Conectar a la palanquera (Arduino). No bloquea ni falla si no está presente.
            _relay.Iniciar();
            // Iniciar captura una vez que la ventana (y su HWND) existen
            _capture.Start();
            Console.WriteLine("Presiona Ctrl+C para salir.");

            // Arranque automático del modo acceso: el gimnasio queda activo todo el horario.
            // Se carga el cache de templates y se entra en estado AccesoActivo. Cada huella
            // que se coloque (cuando no hay enrolamiento ni verify activos) registra
            // entrada/salida automáticamente en el backend.
            _ = IniciarAccesoAuto();

            // Refresco periódico de templates (5 min) para captar enrolamientos hechos
            // desde otra terminal o el frontend.
            _reloadTimer = new System.Windows.Forms.Timer { Interval = 5 * 60 * 1000 };
            _reloadTimer.Tick += async (s, ev) => await _capture.RecargarTemplatesAsync();
            _reloadTimer.Start();
        }

        private async Task IniciarAccesoAuto()
        {
            try
            {
                var n = await _capture.RecargarTemplatesAsync();
                _state.IniciarAcceso();
                Console.WriteLine($"[ACCESO] Modo acceso permanente ACTIVO ({n} usuarios cargados).");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[ACCESO] No se pudo iniciar modo acceso: {ex.Message}");
            }
        }

        protected override void OnFormClosed(FormClosedEventArgs e)
        {
            _reloadTimer?.Stop();
            _capture.Stop();
            _relay.Detener();
            base.OnFormClosed(e);
        }
    }
}
