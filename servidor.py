import socket
import threading
import json
import logging
import time
import random
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout


HOST = "0.0.0.0"
PORT = 9999
MAX_WORKERS = 4      
TASK_TIMEOUT = 30 
BUFFER_SIZE = 4096

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("server")



def process_task(task: dict) -> dict:
    task_id   = task.get("id", "?")
    task_type = task.get("type", "generic")
    payload   = task.get("payload", "")


    duration = random.uniform(0.4, 1.8)
    time.sleep(duration)

    result = {
        "task_id"    : task_id,
        "status"     : "success",
        "type"       : task_type,
        "result"     : f"[OK] Procesado: {str(payload)[:60]}",
        "duration_s" : round(duration, 3),
        "worker"     : threading.current_thread().name,
    }
    log.info(f"Tarea {task_id!r} ({task_type}) completada en {duration:.2f}s "
             f"por {threading.current_thread().name}")
    return result



def recv_message(conn: socket.socket) -> bytes:
    data = b""
    while True:
        chunk = conn.recv(BUFFER_SIZE)
        if not chunk:
            break
        data += chunk
        if b"\n" in data:
            break
    return data


def handle_client(conn: socket.socket, addr: tuple, executor: ThreadPoolExecutor):
    log.info(f"Nueva conexión de {addr}")
    try:
        raw = recv_message(conn)
        if not raw:
            return

        task = json.loads(raw.decode().strip())
        log.info(f"Tarea recibida de {addr}: id={task.get('id')!r} tipo={task.get('type')!r}")

        future = executor.submit(process_task, task)
        result = future.result(timeout=TASK_TIMEOUT)

        conn.sendall((json.dumps(result) + "\n").encode())

    except json.JSONDecodeError as exc:
        _send_error(conn, f"JSON inválido: {exc}")
    except FuturesTimeout:
        _send_error(conn, "La tarea superó el tiempo límite")
    except Exception as exc:
        log.exception(f"Error atendiendo {addr}")
        _send_error(conn, str(exc))
    finally:
        conn.close()
        log.info(f"Conexión cerrada: {addr}")


def _send_error(conn: socket.socket, message: str):
    try:
        payload = json.dumps({"status": "error", "message": message}) + "\n"
        conn.sendall(payload.encode())
    except Exception:
        pass



def start_server():
    executor = ThreadPoolExecutor(
        max_workers=MAX_WORKERS,
        thread_name_prefix="worker",
    )

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((HOST, PORT))
    server_sock.listen(50)

    log.info(f"Servidor escuchando en {HOST}:{PORT}")
    log.info(f"Pool de hilos: {MAX_WORKERS} workers")

    try:
        while True:
            conn, addr = server_sock.accept()

            t = threading.Thread(
                target=handle_client,
                args=(conn, addr, executor),
                daemon=True,
            )
            t.start()
    except KeyboardInterrupt:
        log.info("Apagando servidor...")
    finally:
        server_sock.close()
        executor.shutdown(wait=True)
        log.info("Servidor detenido.")


if __name__ == "__main__":
    start_server()
