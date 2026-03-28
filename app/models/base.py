from enum import StrEnum
from typing import ClassVar, get_args, get_origin

from pydantic.v1 import validator
from sqlmodel import SQLModel


class DisplayEnum(StrEnum):
    _custom_labels: ClassVar[dict[str, str]]

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

            # Normalize human → enum
            normalized = cls._normalize(value)

            for member in cls:
                if normalized == member.value:
                    return member

        raise ValueError(f"Invalid value '{value}' for {cls.__name__}")

    @staticmethod
    def _normalize(value: str) -> str:
        return (
            value.upper()
            .replace("'", "")  # remove apostrophes
            .replace("-", "_")  # hyphen → underscore
            .replace(" ", "_")  # spaces → underscore
        )

    @property
    def label(self) -> str:
        if self in self._custom_labels:
            return self._custom_labels[self]
        return self.value.replace("_", " ").title()


DisplayEnum._custom_labels = {}  # initialize custom labels, empty by default


class APLGLBaseModel(SQLModel):
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
