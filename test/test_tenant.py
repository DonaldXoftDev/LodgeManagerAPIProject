from fastapi import status

from test.conftest import base_url
tenant_url = f'{base_url}/tenants'

#test that a tenant can get his personal details by id and the right status code