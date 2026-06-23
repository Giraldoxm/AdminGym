using System.Collections.Generic;
using Fleck;

namespace HuelleroBridge
{
    public class WebSocketHub
    {
        private readonly WebSocketServer _server;
        private readonly List<IWebSocketConnection> _clients = new List<IWebSocketConnection>();
        private readonly object _lock = new object();

        public WebSocketHub(string url)
        {
            _server = new WebSocketServer(url);
        }

        public void Start()
        {
            _server.Start(socket =>
            {
                socket.OnOpen = () =>
                {
                    lock (_lock) _clients.Add(socket);
                    System.Console.WriteLine($"[WS] Cliente conectado: {socket.ConnectionInfo.ClientIpAddress}");
                };
                socket.OnClose = () =>
                {
                    lock (_lock) _clients.Remove(socket);
                    System.Console.WriteLine("[WS] Cliente desconectado");
                };
                socket.OnError = ex =>
                {
                    System.Console.WriteLine($"[WS] Error: {ex.Message}");
                };
                socket.OnMessage = msg =>
                {
                    System.Console.WriteLine($"[WS] Mensaje recibido del cliente: {msg}");
                };
            });
        }

        public void Broadcast(string message)
        {
            List<IWebSocketConnection> snapshot;
            lock (_lock) snapshot = new List<IWebSocketConnection>(_clients);
            foreach (var c in snapshot)
            {
                if (c.IsAvailable) c.Send(message);
            }
        }
    }
}
