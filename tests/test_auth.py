"""Unit tests for Firebase token verification and Google OAuth setup."""

from unittest.mock import Mock

import pytest

from auth import AuthManager, AuthenticationError


def test_missing_bearer_token_is_rejected():
    # Missing authorization headers must never reach protected application logic.
    manager = AuthManager(firebase_verifier=Mock())

    with pytest.raises(AuthenticationError, match="Bearer token"):
        manager.authenticate_header(None)


def test_firebase_token_is_verified_and_identity_returned():
    # A verified Firebase claim set becomes the application's user identity.
    verifier = Mock(return_value={"uid": "user-1", "email": "user@example.com"})
    manager = AuthManager(firebase_verifier=verifier)

    identity = manager.authenticate_header("Bearer id-token")

    verifier.assert_called_once_with("id-token")
    assert identity.uid == "user-1"
    assert identity.email == "user@example.com"


def test_oauth_authorization_url_uses_sheets_scope():
    # OAuth setup must return the provider URL and CSRF state value.
    flow = Mock()
    flow.authorization_url.return_value = ("https://accounts.google.test/consent", "state-1")
    manager = AuthManager(firebase_verifier=Mock(), oauth_flow_factory=lambda: flow)

    url, state = manager.google_authorization_url()

    assert url == "https://accounts.google.test/consent"
    assert state == "state-1"
    flow.authorization_url.assert_called_once()
