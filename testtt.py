import asyncio
import websockets
import json

async def test_game_flow():
    uri = "ws://localhost:8001/ws"
    
    # חיבור שני לקוחות במקביל
    async with websockets.connect(uri) as ws1, websockets.connect(uri) as ws2:
        print("שני הלקוחות התחברו בהצלחה.")
        
        # 1. יצירת חדר או חיבור למשחק דרך הלקוח הראשון
        await ws1.send(json.dumps({
            "type": "create_room",
            "payload": {}
        }))
        res1 = await ws1.recv()
        data1 = json.loads(res1)
        print("תשובת יצירת חדר:", data1)
        room_id = data1["payload"]["room_id"]
        
        # 2. הלקוח השני מצטרף לחדר
        await ws2.send(json.dumps({
            "type": "join_room",
            "payload": {"room_id": room_id}
        }))
        res2 = await ws2.recv()
        print("תשובת הצטרפות לחדר:", json.loads(res2))
        
        # 3. שליחת מהלך (Move) מהלקוח הראשון
        move_message = {
            "type": "move",
            "payload": {
                "move": {"from": "A1", "to": "A2"}
            }
        }
        await ws1.send(json.dumps(move_message))
        
        # 4. בדיקה האם שני הלקוחות קיבלו את עדכון מצב המשחק (Broadcast)
        update_ws1 = await ws1.recv()
        update_ws2 = await ws2.recv()
        
        print("עדכון שהתקבל אצל לקוח 1:", json.loads(update_ws1))
        print("עדכון שהתקבל אצל לקוח 2:", json.loads(update_ws2))

asyncio.run(test_game_flow())