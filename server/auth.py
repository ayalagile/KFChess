from server.db.users_repo import register_user, verify_user

async def handle_register(payload: dict) -> dict:
    username = payload.get("username")
    password = payload.get("password")
    
    if not username or not password:
        return {"success": False, "message": "Username and password required"}
        
    success = await register_user(username, password)
    if success:
        return {"success": True, "message": "User registered successfully"}
    else:
        return {"success": False, "message": "Username already exists"}

async def handle_login(payload: dict) -> dict:
    username = payload.get("username")
    password = payload.get("password")
    
    if not username or not password:
        return {"success": False, "message": "Username and password required"}
        
    user_data = await verify_user(username, password)
    if user_data:
        return {
            "success": True, 
            "message": "Login successful", 
            "user": user_data
        }
    else:
        return {"success": False, "message": "Invalid username or password"}