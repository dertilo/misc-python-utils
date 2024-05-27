import dataclasses
from typing import Any, TypeVar

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


@dataclasses.dataclass(slots=True)
class EnforcedSlots:
    """
    all children of this class must be slotted

    to match behavior of dataclasses with slots=True that don't inherit from unslotted classes
    a slotted class that inherits from an unslotted one, also inherits the __dict__ attribute

    """

    def __setattr__(self, __name: str, __value: Any) -> None:
        """
        to prevent accidental assignment of attributes that are not in __slots__
        """
        if __name in self.__slots__:
            super(EnforcedSlots, self).__setattr__(__name, __value)
        else:
            msg = f"'{self.__class__.__name__}' object with {self.__slots__=} has no attribute '{__name}'"
            raise AttributeError(msg)


class MaybeEnforcedSlots:
    """
    this class itself is polluting children with a dict-attribute! but thereby also allows non-slotted children

    to match behavior of dataclasses with slots=True that don't inherit from unslotted classes
    a slotted class that inherits from an unslotted one, also inherits the __dict__ attribute
    """

    def __setattr__(self, __name: str, __value: Any) -> None:
        """
        to prevent accidental assignment of attributes that are not in __slots__
        """
        is_slotted = (
            len(getattr(self, "__slots__", {})) > 0
        )  # count existing but empty _slots__ as "unslotted", just to be a little more forgiving
        if not is_slotted or __name in self.__slots__:
            try:
                super().__setattr__(__name, __value)
            except AttributeError as e:
                raise AttributeError(  # noqa: TRY003
                    f"failed to set {__name=} with {__value=} on {self.__class__.__name__} -> did you try to set a property?",  # noqa: EM102
                ) from e
        else:
            msg = f"'{self.__class__.__name__}' object with {self.__slots__=} has no attribute '{__name}'"
            raise AttributeError(msg)


PSEUDO_SLOTS = "_pseudo_slots"


@dataclasses.dataclass
class FixedDict:
    """
    motivation: dataclasses do have a __dict__ attribute where you can assign dynamically whatever you want
    inheriting from this class will prevent that!

    why not using slots=True
    it is workaround cause slots and multi-inheritance don't work together
    """

    _pseudo_slots: tuple[str, ...] = dataclasses.field(init=False, repr=False)

    def __post_init__(self):
        self._pseudo_slots = tuple(f.name for f in dataclasses.fields(self))

    def __setattr__(self, __name: str, __value: Any) -> None:
        """
        to prevent dynamic assignment of unknown/new attributes
        """
        is_already_initialized = hasattr(self, PSEUDO_SLOTS)
        if not is_already_initialized or __name in self._pseudo_slots:
            super().__setattr__(__name, __value)
        else:
            msg = f"'{self.__class__.__name__}' object with {self._pseudo_slots=} has no attribute '{__name}'"
            raise AttributeError(msg)


@dataclasses.dataclass
class DataclassDict(dict):
    def __getitem__(self, __key):  # noqa: ANN001
        return self.__dict__[__key]

    def __setitem__(self, __key, __value):  # noqa: ANN001
        self.__dict__[__key] = __value

    def to_dict(self) -> dict:
        return {k: v for k, v in self.items() if k != PSEUDO_SLOTS}


@dataclasses.dataclass
class DataclassFixedDict(FixedDict, DataclassDict):
    def __setitem__(self, __key, __value):  # noqa: ANN001
        setattr(self, __key, __value)
        self.__dict__[__key] = __value
