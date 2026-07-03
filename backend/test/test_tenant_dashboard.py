import pytest
from fastapi import status

from app.core.enums import BadgeTexts, BadgeVariants
from test.conftest import base_url

tenant_dashboard_url = f'{base_url}/dashboard-tenant'

def test_tenant_get_dashboard_stats_returns_200(authenticated_tenant_client, add_active_lease_to_db):

    response = authenticated_tenant_client.get(f'{tenant_dashboard_url}/me/tenants')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(data, list)
    assert 'room' in data[0]
    assert 'lease' in data[0]
    assert 'finance' in data[0]
    assert 'badge_text' in data[0]
    assert 'badge_variant' in data[0]

def test_tenant_get_dashboard_stat_no_lease_returns_200(authenticated_tenant_client):
    response = authenticated_tenant_client.get(f'{tenant_dashboard_url}/me/tenants')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data == []

def test_landlord_cannot_get_tenant_dashboard_stat_returns_403(authenticated_landlord_client):
    response = authenticated_landlord_client.get(f'{tenant_dashboard_url}/me/tenants')
    data = response.json()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert data['detail'] == 'Only tenants are allowed.'

@pytest.mark.parametrize('fixture_name, expected_badge_text, expected_badge_variant', [
    ('add_active_lease_to_db', BadgeTexts.OWING, BadgeVariants.DANGER),
    ('tenant_safe_payments_in_db', BadgeTexts.SAFE, BadgeVariants.SUCCESS)
])
def test_tenant_dashboard_stat_gives_valid_badge(authenticated_tenant_client, fixture_name,request,
                                                 expected_badge_text, expected_badge_variant):
    request.getfixturevalue(fixture_name)
    response = authenticated_tenant_client.get(f'{tenant_dashboard_url}/me/tenants')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data != []
    assert data[0]['badge_text'] == expected_badge_text.value
    assert data[0]['badge_variant'] == expected_badge_variant.value