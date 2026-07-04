"""
API routes for managing payments.

Provides endpoints for creating payments and fetching payment histories for both landlords and tenants.
"""
from typing import Optional, List
from app.schemas import payment as schema_payment
from app.schemas.error import ErrorResponseSchema
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, get_landlord_user, get_tenant_user
from app.models.user import User
from app.services import payment_service

router = APIRouter()


@router.post(
    '/create-payment',
    response_model=schema_payment.PaymentResponse,
    summary="Record a rent payment",
    description=(
        "Records a payment against an active lease. "
        "The payment cannot exceed the remaining balance owed. "
        "Payments cannot be made against terminated leases."
    ),
    response_description="The recorded payment",
    responses={
        400: {"model": ErrorResponseSchema, "description": "Cannot record a payment on a terminated lease / Payment amount exceeds the remaining balance"},
        401: {"model": ErrorResponseSchema, "description": "Missing, invalid, or expired access token"},
        403: {"model": ErrorResponseSchema, "description": "Only landlord accounts can perform this action"},
        404: {"model": ErrorResponseSchema, "description": "Lease does not exist / Landlord does not own the lodge associated with this lease's room"},
    },
)
def create_payment(
        payment_data: schema_payment.PaymentCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_landlord_user)
):
    """
    Create a new payment record.

    Args:
        payment_data (schema_payment.PaymentCreate): The payment data to record.
        db (Session): The database session.
        current_user (User): The authenticated landlord user.

    Returns:
        schema_payment.PaymentResponse: The created payment record.
    """

    #does the lease exist and belong in the lodge of the current landlord

    return payment_service.add_payment_record(
        db,
        current_landlord_id=current_user.id,
        payment_data=payment_data
    )


@router.get(
    '/{lease_id}',
    response_model=List[schema_payment.PaymentResponse],
    summary="List payments for a lease",
    description=(
        "Retrieves all payment records for a specific lease. "
        "The landlord must own the lodge containing the leased room."
    ),
    response_description="List of payment records",
    responses={
        401: {"model": ErrorResponseSchema, "description": "Missing, invalid, or expired access token"},
        404: {"model": ErrorResponseSchema, "description": "Lease does not exist / Landlord does not own the lodge associated with this lease's room"},
    },
)
def list_lease_payments_for_landlord(
        lease_id: int,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    List all payments associated with a specific lease for the landlord.

    Args:
        lease_id (int): The ID of the lease.
        skip (Optional[int]): Number of records to skip.
        limit (Optional[int]): Maximum number of records to return.
        db (Session): The database session.
        current_user (User): The authenticated user (landlord).

    Returns:
        List[schema_payment.PaymentResponse]: A list of payments.
    """
    #only get payments that the landlord has access to....
    #use pagination while fetching the payment history

    return payment_service.fetch_payments_by_lease(
        db,
        lease_id= lease_id,
        skip=skip,
        limit=limit,
        landlord_id=current_user.id
    )

@router.get(
    '/me/{lease_id}',
    response_model=List[schema_payment.PaymentResponse],
    summary="List my payments for a lease",
    description=(
        "Retrieves all payments the authenticated tenant has made for a specific lease."
    ),
    response_description="List of tenant's payment records",
    responses={
        401: {"model": ErrorResponseSchema, "description": "Missing, invalid, or expired access token"},
        403: {"model": ErrorResponseSchema, "description": "Only tenant accounts can perform this action"},
        404: {"model": ErrorResponseSchema, "description": "Lease does not exist or does not belong to the authenticated tenant"},
    },
)
def list_tenant_payments(
        lease_id: int,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        db: Session = Depends(get_db),
        tenant_user: User = Depends(get_tenant_user)

):
    """
    List all payments associated with a specific lease for the tenant.

    Args:
        lease_id (int): The ID of the lease.
        skip (Optional[int]): Number of records to skip.
        limit (Optional[int]): Maximum number of records to return.
        db (Session): The database session.
        tenant_user (User): The authenticated tenant user.

    Returns:
        List[schema_payment.PaymentResponse]: A list of the tenant's payments.
    """
    return payment_service.fetch_tenant_lease_payments(
        db,
        lease_id=lease_id,
        skip=skip,
        limit=limit,
        tenant_id = tenant_user.tenant_profile.id
    )



# @router.get('/{pay_id}', response_model=schema_payment.PaymentResponse, summary="Retrieve resource at /{pay_id}", description="Retrieve resource at /{pay_id} endpoint.")
# def get_payment_by_id(
#         pay_id : int,
#         db: Session = Depends(get_db),
#         current_user: User = Depends(get_current_user)
# ):
#     lease = crud_payment.get_payment_by_id(db=db, pay_id=pay_id)
#     if not lease:
#         raise HTTPException(
#             status_code=404,
#             detail='Lease not Found'
#         )
#     return lease



