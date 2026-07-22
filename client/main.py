import asyncio
import sys
from client.network.network_client import NetworkClient

async def run_client(mode: str, extra_arg: str = None, username: str = None):
    client = NetworkClient()
    try:
        await client.connect()
        listen_task = asyncio.create_task(client.listen())

        # קביעת שם המשתמש: לפי הפרמטר, או ברירת מחדל לפי המצב
        user_to_login = username if username else ("player1" if mode == "play" else f"player_{mode}")

        # 1. התחברות
        print(f"--- Login ({user_to_login}) ---")
        await client.send_message(
            msg_type="login",
            payload={"username": user_to_login, "password": "mypassword123"},
            request_id=f"req_login_{user_to_login}"
        )
        await asyncio.sleep(1)

        # 2. ביצוע הפעולה לפי המצב
        if mode == "register":
            print(f"\n--- Registering user {user_to_login}... ---")
            await client.send_message(
                msg_type="register",
                payload={"username": user_to_login, "password": "mypassword123"},
                request_id=f"req_reg_{user_to_login}"
            )
        elif mode == "create":
            print("\n--- Creating room... ---")
            await client.send_message(
                msg_type="create_room",
                payload={},
                request_id="req_create"
            )
        elif mode == "join" and extra_arg:
            print(f"\n--- Joining room {extra_arg}... ---")
            await client.send_message(
                msg_type="join_room",
                payload={"room_id": extra_arg},
                request_id="req_join"
            )
        elif mode == "play":
            print("\n--- Entering Matchmaking Queue... ---")
            await client.send_message(
                msg_type="play",
                payload={},
                request_id="req_play"
            )
            print("DEBUG: Processing play message...")
        else:
            print("\nUnknown mode or missing parameters")

        # המתנה לקבלת תשובות/אירועים מהשרת
        await asyncio.sleep(30)
        listen_task.cancel()
    finally:
        await client.close()

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "play"
    arg = sys.argv[2] if len(sys.argv) > 2 else None
    user = sys.argv[3] if len(sys.argv) > 3 else None
    
    asyncio.run(run_client(action, arg, user))