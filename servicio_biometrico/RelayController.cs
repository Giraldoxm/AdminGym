using System;
using System.IO.Ports;
using System.Threading;

namespace HuelleroBridge
{
    /// <summary>
    /// Controla la palanquera vía un Arduino UNO conectado por USB-serial.
    /// El Arduino es el dueño del tiempo de pulso: el bridge solo manda el byte
    /// 'A' (abrir) y el Arduino mantiene el relé activado N segundos y cierra solo.
    ///
    /// Protocolo (9600 baud):
    ///   bridge -> arduino : 'A' = abrir palanquera, 'P' = ping (autodetección)
    ///   arduino -> bridge : "JSB-PALANQUERA..." al arrancar / en respuesta a 'P'
    ///
    /// El puerto COM se toma de la variable de entorno PALANQUERA_COM (ej "COM3").
    /// Si no está definida, se autodetecta pingueando los puertos disponibles.
    /// Si no hay Arduino conectado, el bridge sigue funcionando normalmente: el
    /// acceso se registra igual, solo no se abre la palanquera.
    /// </summary>
    public class RelayController
    {
        private const int    BaudRate  = 9600;
        private const string FirmaPing = "JSB-PALANQUERA";

        private readonly object _lock = new object();
        private SerialPort _port;
        private string     _portName;

        public RelayController()
        {
            _portName = Environment.GetEnvironmentVariable("PALANQUERA_COM");
        }

        /// <summary>Intenta conectar al arrancar el bridge. No lanza si falla.</summary>
        public void Iniciar()
        {
            lock (_lock)
            {
                try { Conectar(); }
                catch (Exception ex)
                {
                    Console.WriteLine($"[RELE] No se pudo conectar al Arduino al iniciar: {ex.Message}");
                }
            }
        }

        /// <summary>
        /// Envía el comando de apertura. No bloquea por los 5 s de la palanquera
        /// (de eso se encarga el Arduino). Reconecta si el puerto se cayó.
        /// </summary>
        public void Abrir()
        {
            lock (_lock)
            {
                try
                {
                    if (_port == null || !_port.IsOpen)
                        Conectar();

                    if (_port != null && _port.IsOpen)
                    {
                        _port.Write("A");
                        Console.WriteLine("[RELE] Comando de apertura enviado a la palanquera.");
                    }
                    else
                    {
                        Console.WriteLine("[RELE] Sin conexión al Arduino — no se abrió la palanquera.");
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"[RELE] Error enviando apertura: {ex.Message}");
                    CerrarPuerto();   // forzar reconexión en el próximo intento
                }
            }
        }

        public void Detener()
        {
            lock (_lock) { CerrarPuerto(); }
        }

        // ============ internos ============

        private void Conectar()
        {
            var nombre = !string.IsNullOrWhiteSpace(_portName) ? _portName : Autodetectar();
            if (string.IsNullOrWhiteSpace(nombre))
            {
                Console.WriteLine("[RELE] No se encontró ningún Arduino de palanquera. " +
                                  "Define PALANQUERA_COM (ej. COM3) si la autodetección falla.");
                return;
            }

            var p = AbrirPuerto(nombre);
            _port     = p;
            _portName = nombre;
            Console.WriteLine($"[RELE] Conectado a la palanquera en {nombre}.");
        }

        private static SerialPort AbrirPuerto(string nombre)
        {
            var p = new SerialPort(nombre, BaudRate)
            {
                ReadTimeout  = 2500,
                WriteTimeout = 1500,
                DtrEnable    = true,   // el UNO se reinicia al abrir el puerto
                NewLine      = "\n",
            };
            p.Open();
            // El UNO se reinicia al abrirse el puerto: esperar a que arranque el sketch.
            Thread.Sleep(2000);
            return p;
        }

        /// <summary>
        /// Recorre los puertos COM, abre cada uno y manda 'P'. El que responde con
        /// la firma "JSB-PALANQUERA" es nuestro Arduino. Sirve porque el número de
        /// COM puede cambiar entre reinicios/reconexiones del cable.
        /// </summary>
        private string Autodetectar()
        {
            foreach (var nombre in SerialPort.GetPortNames())
            {
                try
                {
                    using (var p = AbrirPuerto(nombre))
                    {
                        p.DiscardInBuffer();
                        p.Write("P");
                        // Puede llegar primero "JSB-PALANQUERA READY" (boot) o el "OK".
                        var resp = p.ReadLine();
                        if (resp != null && resp.Contains(FirmaPing))
                        {
                            Console.WriteLine($"[RELE] Arduino de palanquera detectado en {nombre}.");
                            return nombre;
                        }
                    }
                }
                catch
                {
                    // Puerto ocupado, sin Arduino o sin respuesta a tiempo — siguiente.
                }
            }
            return null;
        }

        private void CerrarPuerto()
        {
            try { _port?.Close(); } catch { }
            _port = null;
        }
    }
}
