"""Tax computation API integration tests."""

from decimal import Decimal

import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestTaxEndpoints:
    """Tests for /api/v1/tax endpoints."""

    @pytest.fixture
    def compute_payload(self) -> dict[str, object]:
        """Sample tax computation request payload."""
        return {
            "pan": "ABCDE1234F",
            "assessment_year": "2025-26",
            "regime": "old",
            "gross_salary": "1200000",
            "other_income": "50000",
            "section_80c": "150000",
            "section_80d": "25000",
            "hra_exemption": "100000",
            "standard_deduction": "50000",
        }

    async def test_compute_tax_creates_assessment(
        self,
        client: AsyncClient,
        compute_payload: dict[str, object],
    ) -> None:
        """Tax computation should create and return an assessment."""
        response = await client.post("/api/v1/tax/compute", json=compute_payload)
        assert response.status_code == 201

        data = response.json()
        assert data["pan"] == "ABCDE1234F"
        assert data["assessment_year"] == "2025-26"
        assert Decimal(data["tax_payable"]) > 0
        assert "id" in data

    async def test_compute_tax_invalid_pan(
        self,
        client: AsyncClient,
        compute_payload: dict[str, object],
    ) -> None:
        """Invalid PAN should return validation error."""
        compute_payload["pan"] = "INVALID"
        response = await client.post("/api/v1/tax/compute", json=compute_payload)
        assert response.status_code == 422

    async def test_get_assessment_not_found(self, client: AsyncClient) -> None:
        """Non-existent assessment should return 404."""
        response = await client.get("/api/v1/tax/assessments/nonexistent-id")
        assert response.status_code == 404

    async def test_list_assessments_empty(self, client: AsyncClient) -> None:
        """Empty assessment list should return empty array."""
        response = await client.get("/api/v1/tax/assessments")
        assert response.status_code == 200
        assert response.json() == []

    async def test_compute_and_retrieve_assessment(
        self,
        client: AsyncClient,
        compute_payload: dict[str, object],
    ) -> None:
        """Created assessment should be retrievable by ID."""
        create_response = await client.post("/api/v1/tax/compute", json=compute_payload)
        assert create_response.status_code == 201
        assessment_id = create_response.json()["id"]

        get_response = await client.get(f"/api/v1/tax/assessments/{assessment_id}")
        assert get_response.status_code == 200
        assert get_response.json()["id"] == assessment_id
