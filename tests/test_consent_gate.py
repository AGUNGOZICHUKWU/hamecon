"""Unit tests for the consent gate logic used by the campaign dispatcher."""
from datetime import datetime, timedelta


class _ConsentRecord:
    """Mirrors the consent record structure used by the dispatcher.
    A consent is active only if granted_at is set and revoked_at is not."""

    def __init__(self, granted_at, revoked_at=None):
        self.granted_at = granted_at
        self.revoked_at = revoked_at

    def is_active(self):
        return self.granted_at is not None and self.revoked_at is None


def test_fresh_consent_is_active():
    record = _ConsentRecord(granted_at=datetime.now())
    assert record.is_active() is True


def test_revoked_consent_is_no_longer_active():
    yesterday = datetime.now() - timedelta(days=1)
    now = datetime.now()
    record = _ConsentRecord(granted_at=yesterday, revoked_at=now)
    assert record.is_active() is False


def test_missing_consent_record_is_not_active():
    record = _ConsentRecord(granted_at=None)
    assert record.is_active() is False


def test_regrant_after_revocation_needs_a_new_record():
    """Once a record is revoked, it stays revoked. A new grant creates a new record."""
    old = _ConsentRecord(
        granted_at=datetime.now() - timedelta(days=2),
        revoked_at=datetime.now() - timedelta(days=1),
    )
    new = _ConsentRecord(granted_at=datetime.now())

    assert old.is_active() is False
    assert new.is_active() is True