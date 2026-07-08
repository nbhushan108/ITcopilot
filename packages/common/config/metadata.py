"""Application metadata configuration."""

from datetime import date
from functools import lru_cache
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as pkg_version
from typing import Self

from pydantic import BaseModel, Field, field_validator

from common.config.constants import (
    DEFAULT_APP_NAME,
    DEFAULT_APP_VERSION,
    DEFAULT_BUILD_NUMBER,
    DEFAULT_RELEASE_DATE,
)


class ApplicationMetadata(BaseModel):
    """Canonical application metadata exposed across modules."""

    name: str = Field(default=DEFAULT_APP_NAME, description="Application display name")
    version: str = Field(default=DEFAULT_APP_VERSION, description="Semantic version")
    api_version: str = Field(default="v1", description="REST API version prefix label")
    author: str = Field(default="ITcopilot Contributors")
    license: str = Field(default="Apache-2.0")
    website: str = Field(default="https://nbhushan108.github.io/ITcopilot")
    repository_url: str = Field(default="https://github.com/nbhushan108/ITcopilot")
    build_number: str = Field(default=DEFAULT_BUILD_NUMBER)
    release_date: date = Field(default=date.fromisoformat(DEFAULT_RELEASE_DATE))

    model_config = {"frozen": True}

    @field_validator("release_date", mode="before")
    @classmethod
    def parse_release_date(cls, value: date | str) -> date:
        """Parse release date from ISO string or date object."""
        if isinstance(value, date):
            return value
        return date.fromisoformat(str(value))

    @classmethod
    def from_environment(
        cls,
        *,
        app_name: str | None = None,
        app_version: str | None = None,
        api_version: str | None = None,
        author: str | None = None,
        license_name: str | None = None,
        website: str | None = None,
        repository_url: str | None = None,
        build_number: str | None = None,
        release_date: date | str | None = None,
    ) -> Self:
        """Build metadata from environment overrides with package fallbacks.

        Args:
            app_name: Optional application name override.
            app_version: Optional version override.
            api_version: Optional API version label.
            author: Optional author override.
            license_name: Optional license override.
            website: Optional website URL.
            repository_url: Optional repository URL.
            build_number: Optional build identifier.
            release_date: Optional release date.

        Returns:
            Resolved application metadata instance.
        """
        resolved_version = app_version or _resolve_package_version()
        return cls(
            name=app_name or DEFAULT_APP_NAME,
            version=resolved_version,
            api_version=api_version or "v1",
            author=author or "ITcopilot Contributors",
            license=license_name or "Apache-2.0",
            website=website or "https://nbhushan108.github.io/ITcopilot",
            repository_url=repository_url or "https://github.com/nbhushan108/ITcopilot",
            build_number=build_number or DEFAULT_BUILD_NUMBER,
            release_date=release_date or DEFAULT_RELEASE_DATE,
        )


def _resolve_package_version() -> str:
    """Resolve installed package version from distribution metadata."""
    try:
        return pkg_version("itcopilot")
    except PackageNotFoundError:
        return DEFAULT_APP_VERSION


@lru_cache
def get_application_metadata() -> ApplicationMetadata:
    """Return cached application metadata singleton."""
    return ApplicationMetadata.from_environment()
