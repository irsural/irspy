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

    # TODO: Проверить есть ли необходимость в этом
    @model_validator(mode='after')
    def convert_default(self) -> 'ParamScheme[T]':
        if self.default is not None:
            match self.type:
                case ParamTypes.ENUM:
                    self.default = int(self.default)
                case ParamTypes.INT32:
                    self.default = int(self.default)
                case ParamTypes.DOUBLE:
                    self.default = float(self.default)
                case ParamTypes.STRING:
                    self.default = str(self.default)
                case ParamTypes.COUNTER:
                    self.default = int(self.default)
        return self


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
