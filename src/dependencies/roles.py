from fastapi import Depends, HTTPException, status
from src.dependencies.auth import get_current_user

async def admin_required(current_user=Depends(get_current_user)):
    
    role = current_user.get("role") if isinstance(current_user, dict) else current_user.role
    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user
