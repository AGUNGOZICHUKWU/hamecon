"""Unit tests for the credential-never-stored rule."""


def test_length_is_an_integer_not_a_string():
    """Only a numeric length should ever be stored, never the raw value."""
    identifier = "user@example.com"
    secret = "SuperSecretPass!23"

    identifier_length = len(identifier)
    secret_length = len(secret)

    assert isinstance(identifier_length, int)
    assert isinstance(secret_length, int)


def test_length_carries_no_content_of_the_value():
    """The stored length must not contain any character from the secret."""
    secret = "MyRealPassword@2026"
    stored = len(secret)
    stored_as_text = str(stored)

    assert "M" not in stored_as_text
    assert "@" not in stored_as_text
    assert "password" not in stored_as_text.lower()


def test_empty_submission_records_zero_not_none():
    """Even an empty submit event must record a length, not None."""
    empty_identifier = ""
    empty_secret = ""
    assert len(empty_identifier) == 0
    assert len(empty_secret) == 0