from enum import StrEnum
from types import UnionType
from typing import Any, ClassVar, Union, get_args, get_origin

from pydantic import ValidationInfo, field_serializer, field_validator
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
    @field_validator("*", mode="before")
    @classmethod
    def parse_enums(cls, value: Any, info: ValidationInfo) -> Any:
        """
        Automatically convert values to DisplayEnum if needed.
        Supports single enums, optional enums, lists, and optional lists.
        """
        if value is None:
            return value

        annotation = cls.model_fields[info.field_name].annotation

        # Unwrap Optional[T] / T | None
        origin = get_origin(annotation)
        if origin in (Union, UnionType):
            args = [arg for arg in get_args(annotation) if arg is not type(None)]
            if len(args) == 1:
                annotation = args[0]
                origin = get_origin(annotation)

        # List[DisplayEnum]
        if origin is list:
            args = get_args(annotation)
            if not args or not isinstance(value, list):
                return value

            inner_type = args[0]
            if isinstance(inner_type, type) and issubclass(inner_type, DisplayEnum):
                return [
                    inner_type.from_any(item) if item is not None else None
                    for item in value
                ]

        # Direct DisplayEnum
        if isinstance(annotation, type) and issubclass(annotation, DisplayEnum):
            return annotation.from_any(value)

        return value

    @field_serializer("*", when_used="json", check_fields=False)
    def serialize_display_enums(self, value: Any) -> Any:
        """Serialize DisplayEnum instances using their human-friendly labels."""
        if isinstance(value, DisplayEnum):
            return value.label

        if isinstance(value, list):
            return [
                item.label if isinstance(item, DisplayEnum) else item for item in value
            ]

        return value
