from dataclasses import dataclass, fields
from typing import Any, final

from typing_extensions import Self

from misc_python_utils.dataclass_utils import FixedDict

KeyValue = tuple[str, Any]


@dataclass
class FromDictCoopMixin(FixedDict):
    @final
    @classmethod
    def from_dict(cls, jsn: dict) -> Self:
        parsed_jsn = cls._from_dict(jsn)
        just_known_kwargs = {f.name: parsed_jsn[f.name] for f in fields(cls) if f.init}
        o = cls(**just_known_kwargs)
        return o

    @classmethod
    def _from_dict(cls, jsn: dict) -> dict:
        """
        you are supposed to override this method in your child class
        """
        return jsn

@dataclass
class ToDictCoopMixin(FixedDict):
    @final
    def to_dict(self) -> dict:
        dct = self._to_dict(self)
        return dct

    @classmethod
    def _to_dict(cls) -> dict:
        """
        you are supposed to override this method in your child class
        """
        return {}
