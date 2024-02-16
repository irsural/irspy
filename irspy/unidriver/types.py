from pydantic import BaseModel


class Device(BaseModel):
    handle: int
    name: str
