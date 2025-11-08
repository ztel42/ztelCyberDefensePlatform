import socket
import threading
import time
import json
import requests
import yaml
import logging
from datetime import datetime

# ============================
# CONFIGURATION AND LOGGING
# ============================
CONFIG_PATH = 'config.yaml'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler('honeygrid_agent.log'), logging.StreamHandler()]
)

# ============================
# LOAD CONFIGURATION
# ============================
def load_config():
    try:
        with open(CONFIG_PATH, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logging.error("Configuration file not found.")
        exit(1)

config = load_config()
API_ENDPOINT = config.get('api_endpoint', 'http://localhost:8000/api/v1/ingest')
LISTEN_PORTS = config.get('ports', [22, 80, 445])

# ============================
# PACKET HANDLER FUNCTION
# ============================
def handle_client(conn, addr, port):
    try:
        data = conn.recv(2048)
        payload = data.decode(errors='ignore') if data else ''

        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'source_ip': addr[0],
            'source_port': addr[1],
            'destination_port': port,
            'payload': payload.strip(),
        }

        logging.info(f"[+] Connection from {addr[0]}:{addr[1]} on port {port}")

        try:
            response = requests.post(API_ENDPOINT, json=log_entry, timeout=5)
            if response.status_code == 200:
                logging.info(f"[OK] Event sent to collector.")
            else:
                logging.warning(f"[!] Collector responded with {response.status_code}")
        except Exception as e:
            logging.error(f"[x] Failed to send data to collector: {e}")
            with open('unsent_logs.json', 'a') as backup:
                backup.write(json.dumps(log_entry) + '\n')

    except Exception as e:
        logging.error(f"Error handling client {addr}: {e}")
    finally:
        conn.close()

# ============================
# HONEYPOT LISTENER FUNCTION
# ============================
def start_listener(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        sock.bind(('0.0.0.0', port))
        sock.listen(10)
        logging.info(f"[*] Listening on port {port}")
    except Exception as e:
        logging.error(f"Failed to bind port {port}: {e}")
        return

    while True:
        try:
            conn, addr = sock.accept()
            threading.Thread(target=handle_client, args=(conn, addr, port), daemon=True).start()
        except KeyboardInterrupt:
            logging.info("Agent interrupted by user.")
            break
        except Exception as e:
            logging.error(f"Socket error on port {port}: {e}")
            time.sleep(2)

# ============================
# MAIN EXECUTION ENTRY
# ============================
def main():
    logging.info("=== Honeygrid Agent Started ===")
    threads = []

    for port in LISTEN_PORTS:
        t = threading.Thread(target=start_listener, args=(port,), daemon=True)
        t.start()
        threads.append(t)

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        logging.info("Shutting down agent...")

if __name__ == '__main__':
    main()
