"""Testes de autenticação e usuários padrão."""

from core.auth.auth_service import authenticate, bootstrap_users, hash_password, normalize_handle
from core.db.users_repository import ensure_default_users
from core.auth.auth_service import DEFAULT_USERS


def test_normalize_handle():
    assert normalize_handle("suporte") == "@suporte"
    assert normalize_handle("@ROTA") == "@rota"


def test_hash_password_deterministic():
    assert hash_password("123") == hash_password("123")
    assert hash_password("123") != hash_password("456")


def test_bootstrap_and_authenticate_default_users():
    ensure_default_users(DEFAULT_USERS, hash_password)
    user, error = authenticate("@suporte", "123")
    assert error == ""
    assert user is not None
    assert user["handle"] == "@suporte"
    assert user["name"] == "Suporte"

    user2, error2 = authenticate("@rota", "123")
    assert error2 == ""
    assert user2 is not None
    assert user2["handle"] == "@rota"


def test_authenticate_rejects_invalid_credentials():
    bootstrap_users()
    user, error = authenticate("@suporte", "wrong")
    assert user is None
    assert error
