import pytest
from fastapi import HTTPException
from src.dependencies.roles import admin_required

class DummyUser:
    def __init__(self, role):
        self.role = role

import asyncio
import pytest

@pytest.mark.asyncio
async def test_admin_required():
    admin_user = {"role": "admin"}
    result = await admin_required(admin_user)
    assert result == admin_user

    normal_user = {"role": "user"}
    with pytest.raises(HTTPException):
        await admin_required(normal_user)
