from typing import Optional

from fastapi import FastAPI, Request, Cookie, Depends, Query
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import ValidationError
from starlette import status
from starlette.exceptions import WebSocketException
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.api.main import router as main_router
from app.common.swagger.ui.main import swagger_obj
from app.database.main import get_database
from app.database.utils import connect_to_mongo, close_mongo_connection
from app.exception.api import APIException
from app.exception.body import APIRequestValidationException
from app.models.common.exceptions.body import APIRequestValidationModel, RequestValidationDetails
from app.services.websocket.socket import socket_service

app = FastAPI(**swagger_obj)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(main_router, prefix="/api")

@app.exception_handler(APIException)
async def api_exception_handler(_: Request, exc: APIException):
    """ Exception handler for APIException. """

    return JSONResponse(
        status_code=exc.code,
        content={
            "message": exc.message,
            "code": exc.code,
            "translation": exc.translation_key,
        }
    )


@app.exception_handler(RequestValidationError)
@app.exception_handler(APIRequestValidationException)
@app.exception_handler(ValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    """ Exception handler for RequestValidationError. """

    errors = []

    if isinstance(exc, APIRequestValidationException):
        errors = exc.details
    else:

        # Push all validation errors to pretty printed errors list.
        for error in exc.errors():
            errors.append(RequestValidationDetails(
                location=error.get("loc")[0],
                field=error.get("loc")[1] if len(error.get("loc")) > 1 else None,
                message=f'{error.get("msg") if error.get("msg")[0].isupper() else error.get("msg").capitalize()}.',
                translation=error.get("ctx").get("translation_key") if error.get(
                    "ctx") is not None and "translation_key" in error.get("ctx") else None,
            ))

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(
            APIRequestValidationModel(
                details=jsonable_encoder(errors),
                code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        ),
    )


app.add_event_handler("startup", connect_to_mongo)
app.add_event_handler("shutdown", close_mongo_connection)

app.mount("/public", StaticFiles(directory="public", html=True), name="public")


async def get_authorization(
        authorization: Optional[str] = Cookie(None, alias="Authorization"),
        query: Optional[str] = Query(None, alias="token"),
) -> str:
    """
    Validate cookie from

    :param authorization: Cookie value.
    :param query: Query value.
    """

    if authorization is None and query is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    if authorization is not None:
        return authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization

    return query.replace("Bearer ", "") if query.startswith("Bearer ") else query


@app.websocket("/ws")
async def websocket_endpoint(
        websocket: WebSocket,
        credentials: str = Depends(get_authorization),
        db: AsyncIOMotorClient = Depends(get_database)
):
    """ Websocket endpoint. """

    await socket_service.accept(websocket, credentials)

    try:
        while True:
            if not websocket.client_state:
                continue

            data = await websocket.receive_text()
            await socket_service.handle_connection(websocket, data, credentials, db)
    except WebSocketDisconnect:
        await socket_service.disconnect(websocket)
