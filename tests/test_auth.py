"""Unit tests for Google OAuth setup and identity handling."""

from unittest.mock import Mock

from auth import AuthManager, Identity


def test_google_credentials_produce_an_identity():
    credentials = Mock()
    expected = Identity("user-1", "user@example.com")
    manager = AuthManager(identity_factory=lambda value: expected)

    assert manager.identity_for_credentials(credentials) == expected


def test_oauth_authorization_url_uses_sheets_scope():
    flow = Mock()
    flow.authorization_url.return_value = ("https://accounts.google.test/consent", "state-1")
    manager = AuthManager(oauth_flow_factory=lambda: flow)

    url, state = manager.google_authorization_url()

    assert url == "https://accounts.google.test/consent"
    assert state == "state-1"
    flow.authorization_url.assert_called_once()
