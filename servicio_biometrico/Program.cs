using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;
using System.Windows.Forms;

namespace HuelleroBridge
{
    internal static class Program
    {
        // ===== Thread Execution State (evita idle/sleep del sistema) =====
        [DllImport("kernel32.dll")]
        private static extern uint SetThreadExecutionState(uint esFlags);

        private const uint ES_CONTINUOUS       = 0x80000000;
        private const uint ES_SYSTEM_REQUIRED  = 0x00000001;

        // ===== Detach console (FreeConsole) =====
        [DllImport("kernel32.dll", SetLastError = true)]
        private static extern bool FreeConsole();

        private static void EvitarSuspensionSistema()
        {
            try { SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED); }
            catch { }
        }

        // Redirige Console.Out/Error a un archivo de log (junto al .exe) y luego
        // suelta la consola con FreeConsole(). El proceso queda como app de fondo.
        // Las llamadas a Console.WriteLine existentes siguen funcionando: ahora
        // van a bridge.log en lugar de a la ventana.
        private static void RedirigirLogsYSoltarConsola()
        {
            try
            {
                var dir     = AppDomain.CurrentDomain.BaseDirectory;
                var logPath = Path.Combine(dir, "bridge.log");

                // append mode + autoflush para que se vea en tiempo real con `Get-Content -Wait`
                var stream = new FileStream(logPath, FileMode.Append, FileAccess.Write, FileShare.Read);
                var writer = new StreamWriter(stream, new UTF8Encoding(false)) { AutoFlush = true };

                writer.WriteLine();
                writer.WriteLine($"===== Bridge iniciado {DateTime.Now:yyyy-MM-dd HH:mm:ss} =====");

                Console.SetOut(writer);
                Console.SetError(writer);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[WARN] No se pudo redirigir logs: {ex.Message}");
            }

            try { FreeConsole(); } catch { }
        }

        [STAThread]
        private static void Main()
        {
            EvitarSuspensionSistema();

            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);

            Console.Title = "JainSportBox - Huellero Bridge";
            Console.WriteLine("=== Huellero Bridge (DigitalPersona U.are.U 4500) ===");
            Console.WriteLine("La ventana de consola se cerrará en breve.");
            Console.WriteLine("Logs en tiempo real: bridge.log (junto al .exe).");

            RedirigirLogsYSoltarConsola();

            // Deja claro en el log a qué backend apunta el bridge y si el secreto
            // está definido. Crítico para diagnosticar fallos de enrolamiento/asistencia.
            Console.WriteLine($"[CONFIG] ApiBase      = {BridgeConfig.ApiBase}");
            Console.WriteLine($"[CONFIG] BridgeSecret = {(string.IsNullOrEmpty(BridgeConfig.BridgeSecret) ? "(vacío)" : "(definido)")}");

            var state = new EnrollmentState();

            var hub = new WebSocketHub("ws://0.0.0.0:8765");
            hub.Start();
            Console.WriteLine("[WS] Escuchando en ws://localhost:8765");

            var form = new BridgeForm(state, hub);

            // HttpApi necesita referencia al capture para cargar templates en verify mode
            // BridgeForm crea el capture; lo pasamos después de construir el form
            var api = new HttpApi(state, form.Capture, form.Relay, port: 8001);
            api.Start();

            Console.CancelKeyPress += (_, e) => { e.Cancel = true; Application.Exit(); };
            Application.Run(form);
            Console.WriteLine("Bye.");
        }
    }
}
