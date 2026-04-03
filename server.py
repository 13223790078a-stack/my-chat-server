import asyncio
import websockets
import json

# 用两个“通讯录”分别记录玩家和客服
clients = {}  # 记录玩家，格式: {"玩家ID": 对应的websocket连接}
admins = set()  # 记录客服，格式: {客服的websocket连接1, 客服的websocket连接2...}


async def cs_server(websocket):
    try:
        # 1. 每个人刚连进来时，必须先自报家门（发送注册消息）
        register_msg = await websocket.recv()
        user_info = json.loads(register_msg)

        role = user_info.get("role")

        if role == "admin":
            admins.add(websocket)
            print("👨‍💻 一位【客服】上线了！")
        elif role == "client":
            client_id = user_info.get("id")
            clients[client_id] = websocket
            print(f"👤 【玩家 {client_id}】 上线了！")
            # 通知所有客服，有新玩家上线
            for admin in admins:
                await admin.send(json.dumps({"type": "system", "msg": f"玩家 {client_id} 已上线"}))

        # 2. 开始持续监听他们发来的消息
        async for message in websocket:
            data = json.loads(message)

            if role == "client":
                # 如果是玩家发的消息，全部转发给所有【客服】
                client_id = user_info.get("id")
                print(f"收到玩家 {client_id} 消息: {data['text']}")

                # 包装一下，告诉客服是谁发的
                msg_to_admin = json.dumps({
                    "type": "chat",
                    "from_id": client_id,
                    "text": data["text"]
                })
                for admin in admins:
                    await admin.send(msg_to_admin)

            elif role == "admin":
                # 如果是客服发的消息，必须找到指定的【玩家】转发
                target_id = data.get("target_id")
                text = data.get("text")
                print(f"客服试图回复玩家 {target_id}: {text}")

                if target_id in clients:
                    target_ws = clients[target_id]
                    msg_to_client = json.dumps({
                        "type": "chat",
                        "text": text
                    })
                    await target_ws.send(msg_to_client)
                else:
                    # 如果玩家离线了，提示客服
                    await websocket.send(json.dumps({
                        "type": "system",
                        "msg": f"发送失败，玩家 {target_id} 不在线或已离开。"
                    }))

    except websockets.exceptions.ConnectionClosed:
        pass
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        # 3. 玩家或客服断开连接时的清理工作
        if 'role' in locals():
            if role == "admin" and websocket in admins:
                admins.remove(websocket)
                print("👨‍💻 一位【客服】下线了。")
            elif role == "client":
                client_id = user_info.get("id")
                if client_id in clients:
                    del clients[client_id]
                    print(f"👤 【玩家 {client_id}】 下线了。")


async def main():
    print("🚀 真实迷你客服系统服务器已启动 (端口 8765)...")
    async with websockets.serve(cs_server, "0.0.0.0", 8765):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())