# import datetime
import typing
# import functools
import importlib

import pydantic
from fastapi import FastAPI, Response, Request
from starlette.responses import StreamingResponse


app = FastAPI()


class Settings(pydantic.BaseSettings):
    url: str = "http://localhost:8000"
    storage_class: str = "storages.FileStorage"


settings = Settings()


def import_string(name):
    s = name.split('.')
    module = importlib.import_module('.'.join(s[:-1]))
    return getattr(module, s[-1])


storage = import_string(settings.storage_class)()


class Error(pydantic.BaseModel):
    code: int
    message: str


# class User(pydantic.BaseModel):
#     name: str


# class Lock(pydantic.BaseModel):
#     id: str
#     path: str
#     owner: User
#     locked_at: datetime.datetime


# class LockRequest(pydantic.BaseModel):
#     path: str


# class LockResponse(pydantic.BaseModel):
#     lock: Lock
#     message: typing.Optional[str]


# class VerifiableLockRequest(pydantic.BaseModel):
#     cusor: typing.Optional[str]
#     limit: typing.Optional[int]


# class VerifiableLockListResponse(pydantic.BaseModel):
#     ours: typing.List[Lock]
#     theirs: typing.List[Lock]
#     next_cursor: typing.Optional[str]
#     message: typing.Optional[str]

# class UnlockRequest(pydantic.BaseModel):
#     force: bool  # NOQA


# class UnlockResponse(pydantic.BaseModel):
#     lock: Lock
#     message: typing.Optional[str]

# @app.get("/{repo}/locks", response_model=LockResponse)
# def get_locks(request: LockRequest):
#     # LocksHandler
#     print('get_locks', request)
#     return LockResponse()

# @app.post("/{repo}/locks/verify", response_model=VerifiableLockListResponse)
# def verify_locks(request: VerifiableLockRequest):
#     # LocksVerifyHandler
#     print('verify_locks', request)
#     return VerifiableLockListResponse(ours=[], theirs=[])

# @app.post("/{repo}/locks", response_model=LockResponse)
# def create_locks(request: LockRequest):
#     # CreateLockHandler
#     print('create_locks', request)
#     return LockResponse()

# @app.post("/{repo}/locks/{id}/unlock", response_model=UnlockResponse)
# def unlock_locks(request: UnlockRequest):
#     # DeleteLockHandler
#     pass


class BatchRequestRef(pydantic.BaseModel):
    name: str


class BatchRequestObject(pydantic.BaseModel):
    oid: str
    size: int


class BatchRequest(pydantic.BaseModel):
    transfers: typing.Optional[typing.List[str]]
    operation: str
    ref: typing.Optional[BatchRequestRef]
    objects: typing.List[BatchRequestObject]
    hash_algo: typing.Optional[str]


class BatchResponseObjectActionsAction(pydantic.BaseModel):
    href: str
    header: typing.Dict[str, str] = {}
    expires_in: typing.Optional[int]
    expires_at: typing.Optional[str]


class BatchResponseObjectActions(pydantic.BaseModel):
    upload: typing.Optional[BatchResponseObjectActionsAction]
    download: typing.Optional[BatchResponseObjectActionsAction]
    verify: typing.Optional[BatchResponseObjectActionsAction]


class BatchResponseObject(pydantic.BaseModel):
    oid: str
    size: int
    authenticated: typing.Optional[bool]
    actions: BatchResponseObjectActions
    error: typing.Optional[Error]


class BatchResponse(pydantic.BaseModel):
    transfer: typing.Optional[str]
    objects: typing.List[BatchResponseObject]
    hash_algo: typing.Optional[str]


@app.post("/{repo}/objects/batch", response_model=BatchResponse, response_model_exclude_unset=True)
async def upload_batch(request: BatchRequest, repo: str):
    objects = []
    for object in request.objects:
        action_kwargs = {}
        if await storage.exists(request, repo, object):
            if hasattr(storage, 'get_download_link'):
                action_kwargs['download'] = BatchResponseObjectActionsAction(
                    **await storage.get_download_link(request, repo, object))
            else:
                action_kwargs['download'] = BatchResponseObjectActionsAction(
                    href=f'{settings.url}/{repo}/objects/{object.oid}',
                )
        elif request.operation == 'upload':
            if hasattr(storage, 'get_upload_link'):
                action_kwargs['upload'] = BatchResponseObjectActionsAction(
                    **await storage.get_upload_link(request, repo, object))
            else:
                action_kwargs['upload'] = BatchResponseObjectActionsAction(
                    href=f'{settings.url}/{repo}/objects/{object.oid}',
                )
        else:
            action_kwargs['error'] = Error(code=404, message='Not Found')

        objects.append(BatchResponseObject(
            oid=object.oid, size=object.size,
            actions=BatchResponseObjectActions(
                **action_kwargs
            )
        ))

    return BatchResponse(objects=objects)


@app.get("/{repo}/objects/{oid}")
async def download_object(repo: str, oid: str):
    return StreamingResponse(storage.read(repo, oid))


@app.put("/{repo}/objects/{oid}")
async def upload_object(repo, oid, request: Request):
    await storage.save(repo, oid, request.stream())
    return Response()
