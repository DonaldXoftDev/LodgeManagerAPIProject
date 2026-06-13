
import pytest
from fastapi import status

from app.core.enums import RoomStatus
from test.conftest import base_url

dashboard_url = f'{base_url}/dashboard-landlord'

def test_landlord_get_paginated_dashboard_stats(authenticated_landlord_client, add_dashboard_stats):
    #authenticated landlord,
    #a fixture adds random payment amt to a list of leases , adds vacant rooms, maintenance rooms
    #it shd decide when to make complete payment,
    """"""
    lodge_id = add_dashboard_stats

    response = authenticated_landlord_client.get(url=f'{dashboard_url}/me/landlord/{lodge_id}')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    print(data)
    assert 'financials' in data
    assert 'entity_counts' in data
    assert 'occupied_rooms_lease' in data
    assert 'maintenance_rooms' in data
    assert 'vacant_rooms' in data



