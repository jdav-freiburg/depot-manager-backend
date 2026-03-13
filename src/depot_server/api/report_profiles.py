from typing import List
from uuid import UUID, uuid4

from authlib.oidc.core import UserInfo
from fastapi import APIRouter, Depends, Body, HTTPException, Response

from depot_server.api.models import ReportProfile, ReportProfileInWrite
from depot_server.db import DbReportProfile, collections
from depot_server.helper.auth import Authentication

router = APIRouter()


@router.get(
    '/report-profiles',
    tags=['Report Profile'],
    response_model=List[ReportProfile],
)
async def get_report_profiles(
        _user: UserInfo = Depends(Authentication()),
) -> List[ReportProfile]:
    return [
        ReportProfile.model_validate(report_profile, from_attributes=True)
        async for report_profile in collections.report_profile_collection.find({})
    ]


@router.get(
    '/report-profiles/{report_profile_id}',
    tags=['Report Profile'],
    response_model=ReportProfile,
)
async def get_report_profile(
        report_profile_id: UUID,
        _user: UserInfo = Depends(Authentication()),
) -> ReportProfile:
    report_profile_data = await collections.report_profile_collection.find_one({'_id': report_profile_id})
    if report_profile_data is None:
        raise HTTPException(404)
    return ReportProfile.model_validate(report_profile_data, from_attributes=True)


@router.post(
    '/report-profiles',
    tags=['Report Profile'],
    response_model=ReportProfile,
    status_code=201,
)
async def create_report_profile(
        report_profile: ReportProfileInWrite = Body(...),
        _user: UserInfo = Depends(Authentication(require_admin=True)),
) -> ReportProfile:
    db_report_profile = DbReportProfile(
        id=uuid4(),
        **report_profile.model_dump()
    )
    await collections.report_profile_collection.insert_one(db_report_profile)
    return ReportProfile.model_validate(db_report_profile, from_attributes=True)


@router.put(
    '/report-profiles/{report_profile_id}',
    tags=['Report Profile'],
    response_model=ReportProfile,
)
async def update_report_profile(
        report_profile_id: UUID,
        report_profile: ReportProfileInWrite = Body(...),
        _user: UserInfo = Depends(Authentication(require_admin=True)),
) -> ReportProfile:
    db_report_profile = DbReportProfile(
        id=report_profile_id,
        **report_profile.model_dump()
    )
    if not await collections.report_profile_collection.replace_one(db_report_profile):
        raise HTTPException(404, f"No report_profile for id {report_profile_id}")
    return ReportProfile.model_validate(db_report_profile, from_attributes=True)


@router.delete(
    '/report-profiles/{report_profile_id}',
    tags=['Report Profile'],
    status_code=204,
    response_class=Response,
)
async def delete_report_profile(
        report_profile_id: UUID,
        _user: UserInfo = Depends(Authentication(require_admin=True)),
) -> None:
    if not await collections.report_profile_collection.delete_one({'_id': report_profile_id}):
        raise HTTPException(404, f"No report_profile for id {report_profile_id}")
    await collections.item_collection.update_many(
        {'report_profile_id': report_profile_id}, {'$unset': {'report_profile_id': report_profile_id}}
    )
