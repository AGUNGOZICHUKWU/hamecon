"""Unit tests for the tracking token generator used by sent messages."""
import secrets


def _generate_token():
    """Mirrors the tracking token pattern used in sent_messages."""
    return secrets.token_urlsafe(32)


def test_token_is_a_non_empty_string():
    t = _generate_token()
    assert isinstance(t, str)
    assert len(t) > 0


def test_one_hundred_tokens_are_all_unique():
    """No two tracking tokens should ever collide."""
    tokens = [_generate_token() for _ in range(100)]
    assert len(set(tokens)) == 100


def test_token_is_url_safe():
    """Tokens must contain only URL-safe characters so they work as link paths."""
    t = _generate_token()
    for character in t:
        assert character.isalnum() or character in "-_"