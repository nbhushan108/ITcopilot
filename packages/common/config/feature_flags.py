"""Feature flag configuration."""

from pydantic import BaseModel, Field


class FeatureFlags(BaseModel):
    """Runtime feature toggles for optional ITcopilot modules."""

    enable_ai: bool = Field(default=False, description="Enable AI-assisted features")
    enable_excel: bool = Field(default=True, description="Enable Excel engine")
    enable_parser: bool = Field(default=True, description="Enable document parser engine")
    enable_reports: bool = Field(default=True, description="Enable reporting module")
    enable_cache: bool = Field(default=False, description="Enable distributed cache layer")
    enable_rest_api: bool = Field(default=True, description="Enable REST API surface")
    enable_broker_import: bool = Field(default=True, description="Enable broker import adapters")
    enable_dashboard: bool = Field(default=True, description="Enable web dashboard")
    enable_power_bi: bool = Field(default=False, description="Enable Power BI export integration")
    enable_experimental: bool = Field(
        default=False,
        description="Enable experimental and preview features",
    )

    model_config = {"frozen": True}

    def is_enabled(self, feature: str) -> bool:
        """Check whether a named feature flag is enabled.

        Args:
            feature: Feature flag attribute name without the ``enable_`` prefix or with it.

        Returns:
            True when the feature is enabled.
        """
        normalized = feature if feature.startswith("enable_") else f"enable_{feature}"
        return bool(getattr(self, normalized, False))

    @classmethod
    def from_environment(
        cls,
        *,
        enable_ai: bool = False,
        enable_excel: bool = True,
        enable_parser: bool = True,
        enable_reports: bool = True,
        enable_cache: bool = False,
        enable_rest_api: bool = True,
        enable_broker_import: bool = True,
        enable_dashboard: bool = True,
        enable_power_bi: bool = False,
        enable_experimental: bool = False,
    ) -> "FeatureFlags":
        """Build feature flags from resolved environment values."""
        return cls(
            enable_ai=enable_ai,
            enable_excel=enable_excel,
            enable_parser=enable_parser,
            enable_reports=enable_reports,
            enable_cache=enable_cache,
            enable_rest_api=enable_rest_api,
            enable_broker_import=enable_broker_import,
            enable_dashboard=enable_dashboard,
            enable_power_bi=enable_power_bi,
            enable_experimental=enable_experimental,
        )
