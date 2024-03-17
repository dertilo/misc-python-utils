import dataclasses
from typing import TypeVar

from misc_python_utils.beartypes import Dataclass
from misc_python_utils.utils import Singleton


@dataclasses.dataclass(frozen=True, slots=True)
class _UNDEFINED(metaclass=Singleton):
    """
    I guess this is a dataclass to enable serialization?
    """


Undefined = _UNDEFINED  # TODO: rename?

T = TypeVar("T")

UNDEFINED = _UNDEFINED()


class FillUndefined:
    def __post_init__(self) -> None:
        all_undefined_must_be_filled(self)


def all_undefined_must_be_filled(
    obj: Dataclass,
    extra_field_names: list[str] | None = None,
) -> None:
    field_names = [
        f.name for f in dataclasses.fields(obj) if not f.name.startswith("_") and f.init
    ]
    if (
        extra_field_names is not None
    ):  # property overwritten by field still not listed in dataclasses.fields!
        field_names += extra_field_names
    undefined_fields = (
        f_name
        for f_name in field_names
        if hasattr(obj, f_name) and getattr(obj, f_name) is UNDEFINED
    )
    for f_name in undefined_fields:
        msg = f"{f_name=} of {obj.name if hasattr(obj, 'name') else obj.__class__.__name__} ({type(obj)}) is UNDEFINED!"
        raise AssertionError(
            msg,
        )
