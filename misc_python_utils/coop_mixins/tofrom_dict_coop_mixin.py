from dataclasses import Field, dataclass, fields
from typing import Any, final

from nested_dataclass_serialization.dataclass_serialization_utils import SPECIAL_KEYS
from typing_extensions import Self

from misc_python_utils.dataclass_utils import FixedDict

KeyValue = tuple[str, Any]

AT_LEAST_SOME_WERE_COOPERATIVE = "<AT_LEAST_SOME_WERE_COOPERATIVE>"


@dataclass
class FromDictCoopMixin(FixedDict):
    @final
    @classmethod
    def from_dict(cls, jsn: dict) -> Self:
        assert AT_LEAST_SOME_WERE_COOPERATIVE not in jsn
        cls._at_least_some_were_cooperative = False
        parsed_jsn = cls._from_dict(jsn)
        assert (
            AT_LEAST_SOME_WERE_COOPERATIVE in parsed_jsn
        ), f" all subclasses of {cls.__name__} are UN-cooperative!"
        parsed_jsn.pop(AT_LEAST_SOME_WERE_COOPERATIVE)
        just_known_kwargs = {
            f.name: parsed_jsn[f.name]
            for f in fields(cls)
            if f.init and f.name in parsed_jsn.keys()
        }
        return cls(**just_known_kwargs)

    @classmethod
    def _from_dict(cls, jsn: dict) -> dict:
        """
        you are supposed to override this method in your child class
        """
        return jsn | {AT_LEAST_SOME_WERE_COOPERATIVE: True}


@dataclass
class ToDictCoopMixin(FixedDict):
    @final
    def to_dict(self) -> dict:
        dct = self._to_dict()
        assert (
            AT_LEAST_SOME_WERE_COOPERATIVE in dct
        ), f" all subclasses of {self.__class__.__name__} are UN-cooperative!"
        dct.pop(AT_LEAST_SOME_WERE_COOPERATIVE)
        return dct

    def _to_dict(self) -> dict:
        """
        you are supposed to override this method in your child class
        """
        return {AT_LEAST_SOME_WERE_COOPERATIVE: True} | {
            f.name: getattr(self, f.name)
            for f in fields(self)
            if included_by_default(f)
        }


def included_by_default(f: Field) -> bool:
    return (
        f.init
        and f.name not in (SPECIAL_KEYS + ["_pseudo_slots"])  # noqa: RUF005
        and not f.name.startswith("_")
        and f.repr
    )


@dataclass
class ToFromDictCoopMixin(FromDictCoopMixin, ToDictCoopMixin):
    pass
