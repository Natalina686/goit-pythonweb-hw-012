from fastapi import Depends, HTTPException
from src.dependencies.auth import get_current_user

async def admin_required(current_user=Depends(get_current_user)):
    """
    Dependency that ensures the current user has admin privileges.

    This can be used in FastAPI routes to restrict access to admins only.

    Args:
        current_user (dict | User, optional): The current authenticated user, 
            injected via `get_current_user` dependency.

    Raises:
        HTTPException: If the user's role is not "admin" (403 Forbidden).

    Returns:
        dict | User: The current user object if they are an admin.
    """
    role = current_user.get("role") if isinstance(current_user, dict) else current_user.role
    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user
