import socket            		# Per creare il server e gestire connessioni di rete
import os                		# Per lavorare con i file e percorsi del filesystem
import mimetypes         		# Per capire il tipo di file da inviare (es. HTML, PNG, CSS)
from datetime import datetime  	# Per stampare data e ora nei log


# Impostazioni di base del server
HOST = '127.0.0.1'      		# Server in ascolto solo sul computer locale
PORT = 8080             		# Porta su cui ascolta il server
WEB_ROOT = './www'      		# Cartella da cui verranno serviti i file statici


# Funzione per stampare nel terminale i dettagli di ogni richiesta ricevuta
def log_request(method, path, status):
    print(f"[{datetime.now()}] {method} {path} -> {status}")


# Funzione principale per gestire ogni richiesta HTTP che arriva al server
def handle_request(request):
    try:
        # Separiamo la richiesta in righe e analizziamo la prima riga (es: "GET /index.html HTTP/1.1")
        lines = request.split('\r\n')
        method, path, _ = lines[0].split()

        # Il nostro server gestisce solo richieste GET
        if method != 'GET':
            return "HTTP/1.1 405 Method Not Allowed\r\n\r\nMethod Not Allowed"

        # Se viene richiesta la root "/", reindirizziamo a una pagina predefinita
        if path == '/':
            path = '/home.html'

        # Costruiamo il percorso reale del file da servire
        filepath = os.path.join(WEB_ROOT, path.lstrip('/'))

        # Se il file non esiste, rispondiamo con un errore 404
        if not os.path.isfile(filepath):
            log_request(method, path, 404)
            return "HTTP/1.1 404 Not Found\r\n\r\n404 Not Found"

        # Leggiamo il contenuto del file richiesto in modalità binaria
        with open(filepath, 'rb') as f:
            content = f.read()

        # Cerchiamo di capire che tipo di file è (per dire al browser come trattarlo)
        mime_type, _ = mimetypes.guess_type(filepath)
        mime_type = mime_type or 'application/octet-stream'  # Default per file sconosciuti

        # Costruiamo l'intestazione HTTP della risposta
        header = (
            f"HTTP/1.1 200 OK\r\n"
            f"Content-Type: {mime_type}\r\n"
            f"Content-Length: {len(content)}\r\n"
            f"\r\n"
        )

        # Logghiamo la richiesta andata a buon fine
        log_request(method, path, 200)

        # Ritorniamo header + contenuto del file (come bytes)
        return header.encode() + content

    # Se qualcosa va storto, restituiamo errore 500
    except Exception as e:
        print("Error:", e)
        return b"HTTP/1.1 500 Internal Server Error\r\n\r\n500 Server Error"


# Funzione che avvia il server e accetta continuamente connessioni
def run_server():
    # Creiamo il socket del server (IPv4, TCP)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))  # Assegniamo IP e porta al server
        s.listen(5)           # Il server può gestire 5 connessioni in coda
        print(f"Server in ascolto su http://{HOST}:{PORT}")

        # Ciclo infinito: il server resta sempre in ascolto
        while True:
            conn, addr = s.accept()  # Accettiamo una nuova connessione
            with conn:
                # Riceviamo la richiesta dal client (massimo 1024 byte)
                request = conn.recv(1024).decode('utf-8')
                if request:
                    # Gestiamo la richiesta e otteniamo la risposta
                    response = handle_request(request)

                    # Inviamo la risposta al client
                    conn.sendall(response if isinstance(response, bytes) else response.encode())


# Se eseguiamo direttamente il file, facciamo partire il server
if __name__ == "__main__":
    run_server()

