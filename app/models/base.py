from enum import StrEnum
from typing import ClassVar, get_args, get_origin

from pydantic.v1 import validator
from sqlmodel import SQLModel


class DisplayEnum(StrEnum):
    _custom_labels: ClassVar[dict[str, str]]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Initialize the dict per subclass
        cls._custom_labels = {}

    @classmethod
    def from_any(cls, value: str):
        """
        Convert any input into the corresponding enum member.
        Tries exact match, then normalizes strings, then checks custom labels.
        """
        if isinstance(value, cls):
            return value

        if isinstance(value, str):
            # Exact match on value
            try:
                return cls(value)
            except ValueError:
                pass

            normalized = cls._normalize(value)

            # Match normalized value
            for member in cls:
                if normalized == member.value:
                    return member

            # Match custom label
            for member, label in cls._custom_labels.items():
                if value == label or normalized == cls._normalize(label):
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
        """Return the human-friendly label, falling back to formatted enum value."""
        return self._custom_labels.get(self.value, self.value.replace("_", " ").title())


class APLGLBaseModel(SQLModel):
    class Config:
        use_enum_values = False  # store actual Enum, not string
        json_encoders = {
            DisplayEnum: lambda v: v.label  # always serialize with label
        }

    @validator("*", pre=True)
    def parse_enums(cls, v, field):
        """
        Automatically convert values to DisplayEnum if needed.
        Supports single enum or List[enum].
        """
        if v is None:
            return v

        field_type = getattr(field, "type_", None)

        # direct enum
        try:
            if field_type and issubclass(field_type, DisplayEnum):
                return field_type.from_any(v)
        except TypeError:
            pass  # field_type not a class, skip

        # List[Enum]
        outer_type = getattr(field, "outer_type_", None)
        if get_origin(outer_type) is list:
            inner_type = get_args(outer_type)[0]
            if isinstance(v, list) and issubclass(inner_type, DisplayEnum):
                return [inner_type.from_any(i) for i in v]

        return v
