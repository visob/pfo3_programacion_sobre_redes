import socket
import json
import threading
import time
import random
import logging
import uuid


SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9999
BUFFER_SIZE = 4096
SOCKET_TIMEOUT = 60  # segundos

TASK_TYPES = [
    "compute",
    "io_read",
    "ml_inference",
    "data_transform",
    "report_gen",
]

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("client")


def send_task(task: dict, host: str = SERVER_HOST, port: int = SERVER_PORT) -> dict | None:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(SOCKET_TIMEOUT)
            s.connect((host, port))

            message = json.dumps(task) + "\n"
            s.sendall(message.encode())

            
            data = b""
            while True:
                chunk = s.recv(BUFFER_SIZE)
                if not chunk:
                    break
                data += chunk
                if b"\n" in data:
                    break

            return json.loads(data.decode().strip())

    except ConnectionRefusedError:
        log.error(f"No se pudo conectar a {host}:{port}. ¿Está corriendo el servidor?")
    except socket.timeout:
        log.error("Tiempo de conexión agotado.")
    except json.JSONDecodeError as exc:
        log.error(f"Respuesta inválida del servidor: {exc}")
    except Exception as exc:
        log.exception(f"Error inesperado: {exc}")

    return None



def run_client_session(client_name: str, num_tasks: int = 4):

    log.info(f"[{client_name}] Iniciando sesión con {num_tasks} tareas")

    successes = 0
    failures  = 0

    for i in range(num_tasks):
        task = {
            "id"       : str(uuid.uuid4())[:8],
            "type"     : random.choice(TASK_TYPES),
            "payload"  : f"Datos de {client_name}, tarea #{i + 1}",
            "priority" : random.choice(["low", "medium", "high"]),
            "timestamp": time.time(),
        }

        log.info(f"[{client_name}] Enviando tarea {task['id']!r} ({task['type']})")
        result = send_task(task)

        if result is None:
            failures += 1
            continue

        if result.get("status") == "success":
            successes += 1
            log.info(
                f"[{client_name}] ✓ Tarea {result['task_id']!r} completada "
                f"en {result.get('duration_s', '?')}s "
                f"por {result.get('worker', '?')}"
            )
        else:
            failures += 1
            log.warning(f"[{client_name}] ✗ Error: {result.get('message')}")

        
        time.sleep(random.uniform(0.1, 0.4))

    log.info(
        f"[{client_name}] Sesión finalizada — "
        f"éxitos: {successes}, fallos: {failures}"
    )



def main():
    clientes = [
        "mobile-iOS-1",
        "mobile-Android-1",
        "web-browser-1",
        "web-browser-2",
    ]

    hilos = []
    for nombre in clientes:
        t = threading.Thread(
            target=run_client_session,
            args=(nombre, 3),
            daemon=False,
        )
        hilos.append(t)

    log.info(f"Iniciando {len(clientes)} clientes concurrentes...")

    for t in hilos:
        t.start()
        time.sleep(0.15)

    for t in hilos:
        t.join()

    log.info("Todas las sesiones completadas.")


if __name__ == "__main__":
    main()
