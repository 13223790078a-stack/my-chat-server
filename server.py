import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import os

app = FastAPI()
connected_clients = set()

@app.get("/")
@app.head("/")
async def ping():
    return {"status": "ok", "message": "保安你好，运行正常！"}

@app.websocket("/")
async def chat(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            for client in list(connected_clients):
                try:
                    await client.send_text(data)
                except Exception:
                    pass
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8765))
    print(f"🚀 终极云端服务器启动，端口: {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
