from abc import abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass, fields
from typing import Any, final

from nested_dataclass_serialization.dataclass_serialization import encode_dataclass
from nested_dataclass_serialization.dataclass_serialization_utils import SPECIAL_KEYS
from typing_extensions import Self

from misc_python_utils.dataclass_utils import FixedDict

KeyValue = tuple[str, Any]


@dataclass
class FromDictMROMixin(FixedDict):
    """
    customized decoding (from dict to dataclass)
    """

    @final
    @classmethod
    def from_dict(cls, jsn: dict) -> Self:
        parsed_jsn = dict(cls._loop_over_mro(jsn))
        just_known_kwargs = {f.name: parsed_jsn[f.name] for f in fields(cls) if f.init}
        o = cls(**just_known_kwargs)
        return o

    @classmethod
    def _loop_over_mro(cls, jsn: dict) -> Iterator[KeyValue]:
        for clazz in cls.__mro__:
            if issubclass(clazz, FromDictMROMixin) and clazz != FromDictMROMixin:
                yield from clazz._from_dict_self(jsn)
            else:
                assert clazz == FromDictMROMixin, f"unexpected class: {clazz}"
                break

    @classmethod
    @abstractmethod
    def _from_dict_self(cls, jsn: dict) -> Iterator[KeyValue]:
        """
        you are supposed to override this method in your subclass and call super()._from_dict_self(jsn) at the end!
        """
        ...

    def to_dict(self) -> dict:
        return encode_dataclass(self, skip_keys=SPECIAL_KEYS)
