import asyncio
import os
import logging
from math import expm1

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from starlette.responses import FileResponse

# Настройка логирования для отладки
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

app = FastAPI()

# Путь к аудиофайлу для отправки
AUDIO_FILE = "dummy_audio.mp3"
# Папка для сохранения принятых файлов
RECEIVED_DIR = "received_audio"


@app.on_event("startup")
async def startup_event():
    """Создаем папку для сохранения аудиофайлов при запуске приложения."""
    os.makedirs(RECEIVED_DIR, exist_ok=True)
    log.info(f"Создана папка для сохранения аудио: {RECEIVED_DIR}")
    if not os.path.exists(AUDIO_FILE):
        log.warning(f"Файл {AUDIO_FILE} не найден. Отправка аудио не будет работать.")


@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Fake STT/TTS server is running"}


@app.websocket("/call/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    """Обработка WebSocket-соединения для звонка."""
    await websocket.accept()
    log.info(f"WebSocket-соединение установлено для токена: {token}")

    file_path = os.path.join(RECEIVED_DIR, f"{token}.webm")

    # Открываем файл для записи бинарных данных
    with open(file_path, "wb") as f:
        log.info(f"Начинаем запись данных в {file_path}")

        try:
            receive_task = asyncio.create_task(receive_audio(websocket, f))
            send_task = asyncio.create_task(send_audio(websocket))

            done, pending = await asyncio.wait(
                [receive_task, send_task],
                return_when=asyncio.FIRST_COMPLETED
            )

            log.info(f"Tasks completed. Done: {len(done)}, Pending: {len(pending)}")

            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

            try:
                if websocket.client_state.name == 'CONNECTED':
                    await websocket.close()
            except RuntimeError as e:
                log.warning(f"Error closing websocket: {e}")
            except Exception as e:
                log.error(f"Unexpected error closing websocket: {e}")

            log.info("Соединение WebSocket закрыто и задачи завершены.")

        except WebSocketDisconnect:
            log.info("WebSocket-соединение закрыто клиентом.")
        except Exception as e:
            log.error(f"Ошибка в WebSocket-соединении: {e}")


async def receive_audio(websocket: WebSocket, file_handle):
    try:
        while True:
            data = await websocket.receive_bytes()
            if data:
                file_handle.write(data)
                log.info(f"Получено {len(data)} байт аудио.")
    except WebSocketDisconnect:
        log.info("WebSocket-соединение закрыто при получении аудио.")
    except Exception as e:
        log.error(f"Ошибка при получении аудио: {e}")

async def send_audio(websocket: WebSocket):
    if not os.path.exists(AUDIO_FILE):
        log.error("Невозможно отправить аудиофайл, он не найден.")
        return

    try:
        with open(AUDIO_FILE, "rb") as f:
            audio_bytes = f.read()

        while True:
            await websocket.send_bytes(audio_bytes)
            log.info("Отправлены байты аудио на клиент.")
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        log.info("WebSocket-соединение закрыто при отправке аудио.")
    except RuntimeError:
        log.info("WebSocket уже закрыт, отправка невозможна.")
    except Exception as e:
        log.error(f"Ошибка при отправке аудио: {e}")