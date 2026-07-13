"""Google OAuth and per-user credential helpers."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Callable

from google_auth_oauthlib.flow import Flow


class AuthenticationError(Exception):
    """Raised when an OAuth identity cannot be established."""


@dataclass(frozen=True)
class Identity:
    """The Google account associated with the current Flask session."""

    uid: str
    email: str | None = None


class AuthManager:
    def __init__(
        self,
        oauth_flow_factory: Callable[[], Flow] | None = None,
        identity_factory: Callable[[Any], Identity] | None = None,
    ) -> None:
        self.oauth_flow_factory = oauth_flow_factory or self._default_oauth_flow
        self.identity_factory = identity_factory or self._default_identity_from_credentials
        self._credentials: dict[str, Any] = {}

    def google_authorization_url(self) -> tuple[str, str]:
        """Create the Google consent URL and its CSRF state value."""
        flow = self.oauth_flow_factory()
        url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )
        return url, state

    def exchange_google_code(self, code: str) -> Any:
        """Exchange an OAuth callback code for Google credentials."""
        flow = self.oauth_flow_factory()
        flow.fetch_token(code=code)
        return flow.credentials

    def identity_for_credentials(self, credentials: Any) -> Identity:
        """Derive a verified application identity from Google credentials."""
        return self.identity_factory(credentials)

    def save_google_credentials(self, uid: str, credentials: Any) -> None:
        """Associate OAuth credentials with the signed-in user in this process."""
        self._credentials[uid] = credentials

    def google_credentials_for(self, uid: str) -> Any | None:
        """Retrieve the current user's previously granted Google credentials."""
        return self._credentials.get(uid)

    @staticmethod
    def _default_identity_from_credentials(credentials: Any) -> Identity:
        """Verify the OpenID Connect ID token returned by Google's OAuth flow."""
        from google.auth.transport.requests import Request
        from google.oauth2.id_token import verify_oauth2_token

        token = getattr(credentials, "id_token", None)
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        if not token or not client_id:
            raise AuthenticationError("Google identity information is unavailable")
        try:
            claims = verify_oauth2_token(token, Request(), client_id)
        except Exception as exc:
            raise AuthenticationError("Google identity could not be verified") from exc
        uid = claims.get("sub")
        if not uid:
            raise AuthenticationError("Google identity has no subject")
        return Identity(uid=uid, email=claims.get("email"))

    @staticmethod
    def _default_oauth_flow() -> Flow:
        """Construct a web-client OAuth flow from environment settings."""
        client_config = {
            "web": {
                "client_id": os.environ["GOOGLE_CLIENT_ID"],
                "client_secret": os.environ["GOOGLE_CLIENT_SECRET"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [os.environ["GOOGLE_OAUTH_REDIRECT_URI"]],
            }
        }
        return Flow.from_client_config(
            client_config,
            scopes=[
                "openid",
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/spreadsheets",
            ],
            redirect_uri=os.environ["GOOGLE_OAUTH_REDIRECT_URI"],
        )
