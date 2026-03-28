from enum import StrEnum

from pydantic.v1 import BaseModel, validator


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


class APLGLBase(BaseModel):
    class Config:
        use_enum_values = False  # keep enum objects, not raw strings
        json_encoders = {
            DisplayEnum: lambda v: v.label
            # DisplayEnum: lambda v: {"value": v.value, "label": v.label} # future upgrade path
        }

    @validator("*", pre=True)
    def parse_enums(cls, v, field):
        if v is None:
            return v

        field_type = field.type_

        try:
            if issubclass(field_type, DisplayEnum):
                return field_type.from_any(v)
        except TypeError:
            pass  # field_type might not be a class (e.g. Union, List, etc.)

        return v
