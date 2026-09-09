import logging
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter, Request, Response
from starlette.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import RegisterTortoise

from depot_server.api.items import router as items_router
from depot_server.api.pictures import router as pictures_router
from depot_server.api.report_elements import router as report_elements_router
from depot_server.api.report_profiles import router as report_profiles_router
from depot_server.api.reservations import router as reservations_router
from depot_server.api.users import router as users_router
from depot_server.api.version import router as version_router
from depot_server.api2.announcement import router as announcement_router
from depot_server.api2.item_group import router as item_group_router
from depot_server.api2.storage_location import router as storage_location_router
from depot_server.api2.tag import router as tags_router
from depot_server.api2.item import router as items_router_v2
from depot_server.api2.item_instance import router as item_instance_router
from depot_server.api2.item_composite import router as item_composite_router
from depot_server.api2.reservation import router as reservations_router_v2
from depot_server.config import config
from depot_server.mail.return_reservation_mail import startup as mail_cron_startup, shutdown as mail_cron_shutdown
from depot_server.version import version
from .item_history import router as item_history_router

v1_prefix = '/api/v1/depot'
v2_prefix = '/api/v2/depot'


logger = logging.getLogger("Depot")
logging.basicConfig(format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s', level=config.log_level)
router = APIRouter()
router.include_router(item_history_router, prefix=v1_prefix)
router.include_router(items_router, prefix=v1_prefix)
router.include_router(report_elements_router, prefix=v1_prefix)
router.include_router(report_profiles_router, prefix=v1_prefix)
router.include_router(reservations_router, prefix=v1_prefix)
router.include_router(pictures_router, prefix=v1_prefix)
router.include_router(users_router, prefix=v1_prefix)
router.include_router(version_router, prefix=v1_prefix)

router.include_router(tags_router, prefix=v2_prefix)
router.include_router(announcement_router, prefix=v2_prefix)
router.include_router(storage_location_router, prefix=v2_prefix)
router.include_router(item_group_router, prefix=v2_prefix)
router.include_router(items_router_v2, prefix=v2_prefix)
router.include_router(item_instance_router, prefix=v2_prefix)
router.include_router(item_composite_router, prefix=v2_prefix)
router.include_router(reservations_router_v2, prefix=v2_prefix)

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
    # await db_shutdown()


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.allow_origins,
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
    allow_headers=['*'],
)

app.include_router(router)


# @app.middleware('http')
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
                # print(f"Body: {resp.body()!r}")
        else:
            print(f"Unknown response type: {type(resp)}")
        return resp
    except Exception:
        traceback.print_exc()
        return Response("Internal server error", status_code=500)
