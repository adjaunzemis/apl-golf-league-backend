from enum import StrEnum
from typing import get_args, get_origin

from pydantic.v1 import validator
from sqlmodel import SQLModel


class DisplayEnum(StrEnum):
    @classmethod
    def from_any(cls, value):
        if isinstance(value, cls):
            return value

        if isinstance(value, str):
            # Try exact match first
            try:
                return cls(value)
            except ValueError:
                pass

            # Human-readable → enum
            normalized = value.upper().replace(" ", "_")
            return cls(normalized)

        raise TypeError(f"Invalid value for {cls.__name__}: {value}")

    @property
    def label(self) -> str:
        return self.value.replace("_", " ").title().replace("Apl", "APL")


class APLGLBase(SQLModel):
    class Config:
        use_enum_values = False
        json_encoders = {DisplayEnum: lambda v: v.label}

    @validator("*", pre=True)
    def parse_enums(cls, v, field):
        if v is None:
            return v

        field_type = field.type_

        # Direct enum
        try:
            if issubclass(field_type, DisplayEnum):
                return field_type.from_any(v)
        except TypeError:
            pass

        # List[Enum]
        if get_origin(field.outer_type_) is list:
            inner = get_args(field.outer_type_)[0]
            if isinstance(v, list) and issubclass(inner, DisplayEnum):
                return [inner.from_any(i) for i in v]

        return v
