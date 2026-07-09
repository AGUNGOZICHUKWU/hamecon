"""Unit tests for the password hashing used in operator authentication."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.models.user import User


def test_hash_password_produces_non_empty_value():
    """Any password should produce a non-empty hash."""
    h = User.hash_password("MySecretPassword123")
    assert h is not None
    assert len(str(h)) > 0


def test_same_password_produces_different_hashes():
    """bcrypt uses a random salt, so identical passwords give different hashes.
    This defends against rainbow table attacks."""
    h1 = User.hash_password("SamePassword")
    h2 = User.hash_password("SamePassword")
    assert h1 != h2


def test_hash_is_long_enough_to_be_bcrypt():
    """A proper bcrypt hash is at least 50 characters long."""
    h = User.hash_password("AnyPassword")
    assert len(str(h)) >= 50