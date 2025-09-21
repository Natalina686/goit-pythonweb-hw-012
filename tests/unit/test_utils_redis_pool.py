import pytest
from src.auth.password_reset import generate_reset_token, verify_reset_token

def test_password_reset_token():
    email = "a@test.com"
    token = generate_reset_token(email)
    assert verify_reset_token(token) == email
