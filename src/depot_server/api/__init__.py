import logging
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter, Request, Response
from starlette.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import RegisterTortoise

from depot_server.config import config
from depot_server.mail.return_reservation_mail import startup as mail_cron_startup, shutdown as mail_cron_shutdown
from depot_server.version import version
from .bays import router as bays_router
from .device import router as device_router
from .item_history import router as item_history_router
from .items import router as items_router
from .pictures import router as pictures_router
from .report_elements import router as report_elements_router
from .report_profiles import router as report_profiles_router
from .reservations import router as reservations_router
from .users import router as users_router
from .version import router as version_router

v1_prefix = '/api/v1/depot'
logger = logging.getLogger("Depot")
logging.basicConfig(format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s', level=config.log_level)
router = APIRouter()
router.include_router(bays_router, prefix=v1_prefix)
router.include_router(device_router, prefix=v1_prefix)
router.include_router(item_history_router, prefix=v1_prefix)
router.include_router(items_router, prefix=v1_prefix)
router.include_router(report_elements_router, prefix=v1_prefix)
router.include_router(report_profiles_router, prefix=v1_prefix)
router.include_router(reservations_router, prefix=v1_prefix)
router.include_router(pictures_router, prefix=v1_prefix)
router.include_router(users_router, prefix=v1_prefix)
router.include_router(version_router, prefix=v1_prefix)

from depot_server.db2.models import Tag


@router.get('/')
async def test_route():
    tag = Tag(name="Hallo")
    await tag.save()
    all_tags = await Tag.all()
    return {"message": "Hello, World!", "tags": [t.name for t in all_tags]}




@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting depot server backend, version {version}")
    # startup stuff before the application starts
    reg_tortoise = await  RegisterTortoise(app, config=config.db.to_tortoise_config(), add_exception_handlers=True)
    await reg_tortoise.init_orm()
    if config.debug:
        logger.warning("Server is running in debug mode, don't use this in production!")

    # await db_startup()
    await mail_cron_startup()

    yield

    # tear down and cleanup before quitting the application
    await mail_cron_shutdown()
    await reg_tortoise.close_orm()
    #await db_shutdown()


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.allow_origins,
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
    allow_headers=['*'],
)

app.include_router(router)



#@app.middleware('http')
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        resp = await call_next(request)
        if isinstance(resp, Response):
            if resp.status_code >= 400:
                print(f"Header: {resp.headers}")

                async def stream_print(orig_iterator):
                    async for chunk in orig_iterator:
                        if len(chunk) > 1024:
                            print(f"Body: {chunk[:1024]}")
                        else:
                            print(f"Body: {chunk}")
                        yield chunk

                resp.body_iterator = stream_print(resp.body_iterator)
        elif isinstance(resp, Response):
            if resp.status_code >= 400:
                print(f"Header: {resp.headers}")
                # this is a streaming response now, which doesn't have a body
                # but it's also not the streaming response from above
                # TODO: find a way to print the body if the status code is >= 400
                #print(f"Body: {resp.body()!r}")
        else:
            print(f"Unknown response type: {type(resp)}")
        return resp
    except Exception:
        traceback.print_exc()
        return Response("Internal server error", status_code=500)
