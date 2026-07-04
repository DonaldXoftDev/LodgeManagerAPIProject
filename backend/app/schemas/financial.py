"""
Pydantic schemas for financial summaries.

This module contains the schema used to represent financial statistics
for the landlord's dashboard.
"""
from pydantic import BaseModel, ConfigDict, Field


class FinancialResponse(BaseModel):
    """
    Schema representing the financial summary for a landlord.

    Attributes:
        potential_revenue (int): The maximum possible revenue.
        expected_revenue (int): The revenue expected based on current leases.
        collected_revenue (int): The actual revenue collected.
        unpaid_rent (int): The amount of rent that is unpaid.
    """
    potential_revenue: int = Field(..., description="The maximum possible revenue in KOBO.", examples=[500000000])
    forecasted_revenue: int = Field(..., description="The forecasted revenue in KOBO.", examples=[450000000])
    expected_revenue: int = Field(..., description="The revenue expected based on current leases in KOBO.", examples=[400000000])
    collected_revenue: int = Field(..., description="The actual revenue collected in KOBO.", examples=[350000000])
    unpaid_rent: int = Field(..., description="The amount of rent that is unpaid in KOBO.", examples=[50000000])

    model_config = ConfigDict(from_attributes=True)