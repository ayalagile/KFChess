import asyncio
import websockets
import json

async def test_edge_cases():
    uri = "ws://localhost:8001/ws"
    
    print("--- בדיקת מקרי קצה ואיטרציה 8 ---")
    
    async with websockets.connect(uri) as ws1, websockets.connect(uri) as ws2, websockets.connect(uri) as ws_viewer:
        
        # 1. בדיקת ניסיון כניסה ל־Room ID שאינו קיים
        print("\n[בדיקה 1] ניסיון התחברות לחדר שאינו קיים...")
        await ws1.send(json.dumps({
            "type": "join_room",
            "payload": {"room_id": "FAKE99"}
        }))
        res_fake = await ws1.recv()
        print("תשובת שרת לחדר לא קיים:", json.loads(res_fake))
        
        # 2. יצירת חדר תקין על ידי שחקן 1
        print("\n[בדיקה 2] יצירת חדר חדש...")
        await ws1.send(json.dumps({"type": "create_room", "payload": {}}))
        
         # קריאת הודעות עד לקבלת אישור יצירת החדר
        room_id = None
        while True:
            res1 = await ws1.recv()
            room_data = json.loads(res1)
            if room_data.get("type") == "room_created":
                room_id = room_data.get("payload", {}).get("room_id")
                break
                
        print(f"החדר נוצר בהצלחה עם מזהה: {room_id}")
        
        # 3. הצטרפות שחקן 2 לחדר
        print("\n[בדיקה 3] שחקן 2 מצטרף לחדר...")
        await ws2.send(json.dumps({
            "type": "join_room",
            "payload": {"room_id": room_id}
        }))
        res2 = await ws2.recv()
        print("תשובת הצטרפות שחקן 2:", json.loads(res2))
        
        # לקרוא את הודעת ה־Broadcast שהגיעה לשחקן 1 על הצטרפות שחקן 2
        # במקום: update_ws1 = await ws1.recv()
        try:
            update_ws1 = await asyncio.wait_for(ws1.recv(), timeout=2.0)
            print("עדכון שהתקבל אצל שחקן 1:", json.loads(update_ws1))
        except asyncio.TimeoutError:
            print("מידע: לא התקבלה הודעת עדכון אצל שחקן 1 (השרת לא שלח Broadcast). ממשיכים בטסט...")

        # 4. בדיקת צופה (Viewer) שמצטרף באמצע משחק
        print("\n[בדיקה 4] צופה (Viewer) מצטרף לחדר שכבר פעיל...")
        await ws_viewer.send(json.dumps({
            "type": "join_room",
            "payload": {"room_id": room_id}
        }))
        res_viewer = await ws_viewer.recv()
        print("תשובת הצטרפות צופה (כולל מצב משחק נוכחי):", json.loads(res_viewer))

        # 5. בדיקת ניתוק ו־Auto-Resign / הודעה ליריב
        print("\n[בדיקה 5] הדמיית ניתוק של שחקן 2 יקת התראה ליריב...")
        # סגירת החיבור של שחקן 2 בכוח
        await ws2.close()
        
        # בדיקה האם שחקן 1 קיבל הודעת ניתוק (Opponent disconnected)
        try:
            disconnect_notice = await asyncio.wait_for(ws1.recv(), timeout=3.0)
            print("הודעה שהתקבלה אצל שחקן 1 עקב ניתוק היריב:", json.loads(disconnect_notice))
        except asyncio.TimeoutError:
            print("אזהרה: לא התקבלה הודעת ניתוק אצל שחקן 1 במסגרת הזמן שהוקצתה.")

asyncio.run(test_edge_cases())