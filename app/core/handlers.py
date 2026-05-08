from .exceptions import (
    BaseAlreadyExistError,
    BaseNotFoundError,
    UnauthorizedAccessError,
    LeaseAlreadyTerminated,
    LeaseAlreadyExpired,

)
from fastapi.responses import JSONResponse
from fastapi import Request


async def not_found_exception_handler(request: Request, exc: BaseNotFoundError):
    return JSONResponse(
        status_code=404,
        content={
            'error': 'Not Found',
            'detail': exc.detail
        }
    )


async def already_exist_exception_handler(request: Request, exc: BaseAlreadyExistError):
    return JSONResponse(
        status_code=400,
        content={
            'error': 'Already exists',
            'detail': exc.detail
        }
    )


async def unauthorized_access_exception_handler(request: Request, exc: UnauthorizedAccessError):
    return JSONResponse(
        status_code=403,
        content={
            'error': 'Not authorized',
            'detail': exc.detail
        }
    )

async def already_terminated_lease_handler(request: Request, exc: LeaseAlreadyTerminated):
    return JSONResponse(
        status_code=400,
        content={
            'error': 'Already terminated',
            'detail': exc.detail
        }
    )

async def already_expired_lease_handler(request: Request, exc: LeaseAlreadyExpired):
    return JSONResponse(
        status_code=400,
        content={
            'error': 'Already Expired',
            'detail': exc.detail
        }
    )

lodge_ops_handlers = {
    BaseNotFoundError: not_found_exception_handler,
    BaseAlreadyExistError: already_exist_exception_handler,
    UnauthorizedAccessError: unauthorized_access_exception_handler,
    LeaseAlreadyTerminated: already_terminated_lease_handler,
    LeaseAlreadyExpired: already_expired_lease_handler

}
