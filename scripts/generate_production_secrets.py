#!/usr/bin/env python3
"""Generate production secrets for ITcopilot deployment."""

from app.core.security import hash_password


def main() -> None:
    """Print SECRET_KEY and AUTH_ADMIN_PASSWORD_HASH for production .env."""
    import secrets

    secret_key = secrets.token_hex(32)
    admin_password = secrets.token_urlsafe(16)
    password_hash = hash_password(admin_password)

    print("# Add these to your production .env file:")
    print(f"SECRET_KEY={secret_key}")
    print(f"AUTH_ADMIN_PASSWORD_HASH={password_hash}")
    print()
    print("# One-time admin login password (store securely, not in git):")
    print(f"AUTH_ADMIN_PASSWORD={admin_password}")


if __name__ == "__main__":
    main()
