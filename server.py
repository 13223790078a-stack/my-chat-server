import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import os

app = FastAPI()
connected_clients = set()

# 1. 专门应付 Render 保安的检查 (支持正常访问和 HEAD 敲门)
@app.get("/")
@app.head("/")
async def ping():
    return {"status": "ok", "message": "保安你好，运行正常！"}

# 2. 我们的跨国聊天隧道
@app.websocket("/")
async def chat(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            # 接收前端发来的包裹
            data = await websocket.receive_text()
            # 瞬间广播给群里所有人（包括自己）
            for client in list(connected_clients):
                try:
                    await client.send_text(data)
                except Exception:
                    pass
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

if __name__ == "__main__":
    # 获取 Render 分配的端口
    port = int(os.environ.get("PORT", 8765))
    print(f"🚀 终极云端服务器启动，端口: {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
