import asyncio
from client.network.network_client import NetworkClient

async def main():
    client = NetworkClient()
    try:
        await client.connect()
        
        # האזנה לתשובות מהשרת ברקע
        listen_task = asyncio.create_task(client.listen())
        
        # 1. בדיקת הרשמה של משתמש חדש
        print("--- Testing Registration ---")
        await client.send_message(
            msg_type="register", 
            payload={"username": "player1", "password": "mypassword123"},
            request_id="req_reg"
        )
        await asyncio.sleep(1)
        
        # 2. בדיקת התחברות עם אותו משתמש
        print("--- Testing Login ---")
        await client.send_message(
            msg_type="login", 
            payload={"username": "player1", "password": "mypassword123"},
            request_id="req_login"
        )
        await asyncio.sleep(1)
        
        # ביטול משימת ההאזנה לפני סגירה
        listen_task.cancel()
        
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())