import asyncio
import websockets
import json
import os
import http

connected_clients = set()

# 处理聊天逻辑
async def chat_handler(websocket):
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            for client in list(connected_clients):
                try:
                    await client.send(message)
                except:
                    pass
    finally:
        connected_clients.remove(websocket)

# 核心：这个函数专门应付 Render 的“巡逻员”，让它能顺利上线
async def process_request(path, request_headers):
    if path == "/":
        return http.HTTPStatus.OK, [], b"Server is running!"
    return None

async def main():
    port = int(os.environ.get("PORT", 8765))
    # 加入了 process_request 
    async with websockets.serve(chat_handler, "0.0.0.0", port, process_request=process_request):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
