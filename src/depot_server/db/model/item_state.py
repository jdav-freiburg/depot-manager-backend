from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import Field
from pymongo import IndexModel, ASCENDING, DESCENDING

from depot_server.api.models import ItemCondition, ReportState, TotalReportState
from depot_server.db.model.base import BaseDocument, BaseSubDocument
from depot_server.helper.util import date


class DbStrChange(BaseSubDocument):
    previous: Optional[str] = None
    next: Optional[str] = None


class DbIdChange(BaseSubDocument):
    previous: Optional[UUID] = None
    next: Optional[UUID] = None


class DbDateChange(BaseSubDocument):
    previous: Optional[date] = None
    next: Optional[date] = None


class DbTagsChange(BaseSubDocument):
    previous: List[str]
    next: List[str]


class DbTotalReportStateChange(BaseSubDocument):
    previous: Optional[TotalReportState] = None
    next: Optional[TotalReportState] = None


class DbItemConditionChange(BaseSubDocument):
    previous: ItemCondition
    next: ItemCondition


class DbItemStateChanges(BaseSubDocument):
    external_id: Optional[DbStrChange] = None

    manufacturer: Optional[DbStrChange] = None
    model: Optional[DbStrChange] = None
    serial_number: Optional[DbStrChange] = None
    manufacture_date: Optional[DbDateChange] = None
    purchase_date: Optional[DbDateChange] = None
    first_use_date: Optional[DbDateChange] = None

    name: Optional[DbStrChange] = None
    description: Optional[DbStrChange] = None

    report_profile_id: Optional[DbIdChange] = None

    total_report_state: Optional[DbTotalReportStateChange] = None
    condition: Optional[DbItemConditionChange] = None
    condition_comment: Optional[DbStrChange] = None

    last_service: Optional[DbDateChange] = None

    picture_id: Optional[DbStrChange] = None

    group_id: Optional[DbStrChange] = None

    tags: Optional[DbTagsChange] = None

    bay_id: Optional[DbIdChange] = None


class DbItemReport(BaseSubDocument):
    report_element_id: UUID
    state: ReportState
    comment: Optional[str] = None


class DbItemState(BaseDocument):
    __collection_name__ = 'item_state'
    __indexes__ = [
        IndexModel([('item_id', ASCENDING), ('timestamp', DESCENDING)]),
        IndexModel([('timestamp', ASCENDING)]),
    ]

    id: UUID = Field(..., alias='_id')
    item_id: UUID = Field(...)

    timestamp: datetime = Field(...)

    changes: DbItemStateChanges = Field(...)
    report: Optional[List[DbItemReport]] = None

    user_id: str = Field(...)

    comment: Optional[str] = Field(None)
