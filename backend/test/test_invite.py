

import pytest
from fastapi import status
from datetime import timedelta

from app.core.enums import LeaseStatus, InviteStatus
from test.conftest import base_url

invite_url = f'{base_url}/invites'

def test_landlord_create_invite_record_returns_201(authenticated_landlord_client, invite_schema_factory, add_lodge_to_db):
    payload = invite_schema_factory(lodge_id=add_lodge_to_db.id).model_dump(mode='json')

    response = authenticated_landlord_client.post(f'{invite_url}', json=payload)
    data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert data['lodge_id'] == add_lodge_to_db.id
    assert data['status'] == InviteStatus.SENT



def test_landlord_get_invite_by_id_returns_200(authenticated_landlord_client, add_invite_to_db, add_lodge_to_db):
    invite_id= add_invite_to_db.id

    response = authenticated_landlord_client.get(f'{invite_url}/{invite_id}')
    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert data['lodge_name'] == add_lodge_to_db.name



