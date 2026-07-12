"""Firebase token verification and per-user Google OAuth helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from google_auth_oauthlib.flow import Flow


class AuthenticationError(Exception):
    # Identifies requests that cannot be associated with an authenticated user.
    """Raised when a request cannot be associated with an authenticated user."""


@dataclass(frozen=True)
class Identity:
    # Stores the stable Firebase user identifier and optional email address.
    uid: str
    email: str | None = None


class AuthManager:
    def __init__(
        self,
        firebase_verifier: Callable[[str], dict[str, Any]] | None = None,
        oauth_flow_factory: Callable[[], Flow] | None = None,
    ) -> None:
        # Configure injectable verifiers/flows and an in-memory credential store.
        self.firebase_verifier = firebase_verifier or self._default_firebase_verifier
        self.oauth_flow_factory = oauth_flow_factory or self._default_oauth_flow
        self._credentials: dict[str, Any] = {}

    def authenticate_header(self, authorization: str | None) -> Identity:
        # Verify a bearer token and convert its claims into an application identity.
        if not authorization or not authorization.startswith("Bearer "):
            raise AuthenticationError("Bearer token is required")
        token = authorization.removeprefix("Bearer ").strip()
        if not token:
            raise AuthenticationError("Bearer token is required")
        try:
            claims = self.firebase_verifier(token)
        except Exception as exc:  # Firebase raises several verifier-specific exceptions.
            raise AuthenticationError("Firebase token could not be verified") from exc
        uid = claims.get("uid")
        if not uid:
            raise AuthenticationError("Firebase token has no user identity")
        return Identity(uid=uid, email=claims.get("email"))

    def google_authorization_url(self) -> tuple[str, str]:
        # Create the Google consent URL and CSRF state value.
        flow = self.oauth_flow_factory()
        url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )
        return url, state

    def exchange_google_code(self, code: str) -> Any:
        # Exchange the OAuth callback code for user Google credentials.
        flow = self.oauth_flow_factory()
        flow.fetch_token(code=code)
        return flow.credentials

    def save_google_credentials(self, uid: str, credentials: Any) -> None:
        # Associate OAuth credentials with the authenticated user for this process.
        self._credentials[uid] = credentials

    def google_credentials_for(self, uid: str) -> Any | None:
        # Retrieve the current user's previously granted Google credentials.
        return self._credentials.get(uid)

    @staticmethod
    def _default_firebase_verifier(token: str) -> dict[str, Any]:
        # Lazily initialize Firebase Admin and verify the supplied ID token.
        import firebase_admin
        from firebase_admin import auth

        if not firebase_admin._apps:
            firebase_admin.initialize_app()
        return auth.verify_id_token(token)

    @staticmethod
    def _default_oauth_flow() -> Flow:
        # Construct an OAuth flow from environment-provided web-client settings.
        import os

        client_config = {
            "web": {
                "client_id": os.environ["GOOGLE_CLIENT_ID"],
                "client_secret": os.environ["GOOGLE_CLIENT_SECRET"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [os.environ["GOOGLE_OAUTH_REDIRECT_URI"]],
            }
        }
        flow = Flow.from_client_config(
            client_config,
            scopes=["https://www.googleapis.com/auth/spreadsheets"],
            redirect_uri=os.environ["GOOGLE_OAUTH_REDIRECT_URI"],
        )
        return flow
