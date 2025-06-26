from enum import Enum

from datetime import datetime, date
from pydantic import ConfigDict, BaseModel
from pymongo import IndexModel
from typing import List, Any, Sequence, Mapping, TypeVar, Type, Union, ClassVar
from uuid import UUID


def _safe_document(doc: Any):
    if doc is None:
        return doc
    if isinstance(doc, Enum):
        return doc.value
    if isinstance(doc, (str, int, float, bool, UUID, datetime)):
        return doc
    if isinstance(doc, Mapping):
        return {k: _safe_document(v) for k, v in doc.items()}
    if isinstance(doc, Sequence):
        return [_safe_document(x) for x in doc]
    if isinstance(doc, date):
        return doc.toordinal()
    raise ValueError(f"Invalid document of type {type(doc)}: {doc}")

TDocument = TypeVar('TDocument', bound='BaseSubDocument')


class BaseSubDocument(BaseModel):
    model_config = ConfigDict(validate_by_name=True, validate_assignment=True)


class BaseDocument(BaseSubDocument):
    __indexes__: ClassVar[List[IndexModel]] = []
    __collection_name__: ClassVar[str]

    def document(self):
        return _safe_document(self.model_dump(exclude_none=True, by_alias=True))

    @classmethod
    def validate_override(cls: Type[TDocument], data: Union[dict, BaseModel], **overrides) -> TDocument:
        if isinstance(data, BaseModel):
            data = data.model_dump(exclude=set(overrides.keys()))
        assert isinstance(data, dict)
        data.update(overrides)
        if 'id' in data:
            data['_id'] = data.pop('id')
        return cls.model_validate(data)

    @classmethod
    def validate_document(cls: Type[TDocument], doc: Union[dict, BaseModel]) -> TDocument:
        if isinstance(doc, BaseModel):
            doc = doc.model_dump(exclude_none=True)
            if 'id' in doc:
                doc['_id'] = doc.pop('id')
        assert isinstance(doc, dict)
        return cls.model_validate(doc)

    def update_from(self, src_doc):
        if isinstance(src_doc, BaseModel):
            for key in src_doc.model_fields.keys():
                if key in self.model_fields:
                    setattr(self, key, getattr(src_doc, key))
        else:
            assert False
