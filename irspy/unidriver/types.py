from enum import StrEnum
from typing import Optional, List, Dict, Any, TypeVar, Generic

from pydantic import BaseModel, model_validator


class ParamTypes(StrEnum):
    INT32 = 'int32'
    DOUBLE = 'double'
    STRING = 'string'
    COUNTER = 'counter'
    ENUM = 'enum'


T = TypeVar('T')


class ParamScheme(BaseModel, Generic[T]):
    id: int
    name: int
    type: ParamTypes
    default: Optional[T] = None
    enum_fields: Optional[Dict[str, int]] = None

class BuilderScheme(BaseModel):
    id: int
    name: int
    params: List[int]


class GroupScheme(BaseModel):
    id: int
    name: int
    builders: List[BuilderScheme]


class ErrorScheme(BaseModel):
    id: int
    name: int


class Device(BaseModel):
    handle: int
    name: str
