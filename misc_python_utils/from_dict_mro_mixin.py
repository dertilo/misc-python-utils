from abc import abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass, fields, field
from typing import Any, final

from nested_dataclass_serialization.dataclass_serialization import encode_dataclass
from nested_dataclass_serialization.dataclass_serialization_utils import SPECIAL_KEYS
from typing_extensions import Self

from misc_python_utils.dataclass_utils import FixedDict

KeyValue = tuple[str, Any]



@dataclass
class FromDictCoopMixin(FixedDict):

    @final
    @classmethod
    def from_dict(cls, jsn: dict) -> Self:
        parsed_jsn = cls._from_dict_self(jsn)
        just_known_kwargs = {f.name: parsed_jsn[f.name] for f in fields(cls) if f.init}
        o = cls(**just_known_kwargs)
        return o

    @classmethod
    def _from_dict_self(cls, jsn: dict) -> dict:
        """
        you are supposed to override this method in your child class
        """
        return jsn

