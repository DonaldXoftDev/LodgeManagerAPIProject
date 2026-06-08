
from fastapi import status

from test.conftest import base_url

lodge_url = f'{base_url}/lodges'

def test_landlord_register_lodge_returns_200(authenticated_landlord_client,mock_landlord_schema, mock_lodge_schema):
    payload = mock_lodge_schema.model_dump()

    response = authenticated_landlord_client.post(f'{lodge_url}/register', json=payload)
    data = response.json()

    assert  response.status_code == status.HTTP_200_OK
    assert data['name'] == mock_lodge_schema.name
    assert data['address'] == mock_lodge_schema.address
    assert 'id' in data
    assert 'landlord_id' in data


def test_register_duplicate_lodge_returns_400(authenticated_landlord_client, add_lodge_to_db, mock_lodge_schema):
    payload = mock_lodge_schema.model_dump()

    response = authenticated_landlord_client.post(f'{lodge_url}/register', json=payload)
    data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert data['detail'] == f'Lodge: {mock_lodge_schema.name} already exists'


def test_tenant_cannot_register_lodge_returns_403(authenticated_tenant_client, add_lodge_to_db, mock_lodge_schema):
    payload = mock_lodge_schema.model_dump()

    response = authenticated_tenant_client.post(f'{lodge_url}/register', json=payload)
    data = response.json()

    assert response.status_code == status.HTTP_403_FORBIDDEN

    assert data['detail'] == f'Only landlords are allowed.'


def test_landlord_get_lodge_by_id_returns_200(authenticated_landlord_client, add_lodge_to_db, add_landlord_to_db):
    response = authenticated_landlord_client.get(f'{lodge_url}/{add_landlord_to_db.id}')
    data = response.json()

    assert  response.status_code == status.HTTP_200_OK
    assert data['name'] == add_lodge_to_db.name
    assert data['address'] == add_lodge_to_db.address
    assert data['id'] == add_lodge_to_db.id
    assert  data['landlord_id'] == add_lodge_to_db.landlord_id
    assert data['is_active'] == add_lodge_to_db.is_active

def test_landlord_get_lodge_id_not_exist_returns_404(authenticated_landlord_client, add_landlord_to_db):
    fake_landlord_id = 2
    response = authenticated_landlord_client.get(f'{lodge_url}/{fake_landlord_id}')

    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_landlord_get_lodge_not_owned(authenticated_landlord_client,add_landlord_to_db):
    pass

def test_get_landlord_lodges_returns_200(authenticated_landlord_client, lodges_in_db):
    response = authenticated_landlord_client.get(f'{lodge_url}')
    data = response.json()
    print(data)
    assert response.status_code == status.HTTP_200_OK
    assert len(data) == len(lodges_in_db)