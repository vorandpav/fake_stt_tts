import asyncio
import websockets

async def test_connection():
    uri = "ws://localhost:8080/call/b662ae75a725411c8da0943cdb279bad"
    async with websockets.connect(uri) as websocket:
        # Отправляем тестовые байты
        await websocket.send(b"test audio bytes")
        print("Отправлены тестовые байты")

        # Получаем аудиофайл от сервера
        audio_data = await websocket.recv()
        print(f"Получено {len(audio_data)} байт аудио от сервера")

asyncio.run(test_connection())
