import os  # noqa: F401
import shutil
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import ClassVar

from nested_dataclass_serialization.dataclass_hashing import hash_dataclass
from nested_dataclass_serialization.dataclass_serialization import (
    deserialize_dataclass,
    encode_dataclass,
)

from misc_python_utils.beartypes import Dataclass
from misc_python_utils.buildable_dataclasses.buildable import Buildable
from misc_python_utils.dataclass_utils import UNDEFINED, all_undefined_must_be_filled
from misc_python_utils.file_utils.readwrite_files import read_file, write_json
from misc_python_utils.prefix_suffix import PrefixSuffix
from misc_python_utils.utils import Singleton


@dataclass(frozen=True, slots=True)
class _CREATE_CACHE_DIR_IN_BASE_DIR(metaclass=Singleton):  # noqa: N801
    pass


CREATE_CACHE_DIR_IN_BASE_DIR = _CREATE_CACHE_DIR_IN_BASE_DIR()


def remove_if_exists(path: str) -> None:
    if Path(path).exists():
        if Path(path).is_file():
            Path(path).unlink()
        else:
            shutil.rmtree(path)


def _check_that_loading_went_well(dc: Dataclass, loaded_dc: Dataclass) -> None:
    """
    currently only checks that hashes match, hashes ignore "state-fields"!!
    """
    if hash_dataclass(dc) != hash_dataclass(loaded_dc):
        write_json("loaded_dc.json", encode_dataclass(loaded_dc))
        write_json("self_dc.json", encode_dataclass(dc))
        msg = (
            "icdiff <(cat loaded_dc.json | jq . ) <(cat self_dc.json | jq . ) | less -r"
        )
        raise AssertionError(
            msg,
        )


def create_cache_dir_with_hash_suffix(
    self: Dataclass,
    cache_base: PrefixSuffix,
) -> PrefixSuffix:
    all_undefined_must_be_filled(self, extra_field_names=["name"])
    return PrefixSuffix(
        prefix_key=cache_base.prefix_key,
        suffix=f"{cache_base.suffix}/{type(self).__name__}-{self.name.replace('/', '_')}{hash_dataclass(self)}",
    )


@dataclass
class HashCachedData(Buildable, ABC):
    """
    based on "CachedData": https://github.com/dertilo/misc-utils/blob/1609ac8c166ef4c6757d2d5daedb90062d81d75e/misc_utils/cached_data.py#L66
      but without any locking!
    use this for short-lived "cache" only!
    for long-lived data better simply use Buildable + is_ready for checking validity of data
    long-lived data: you don't want/need different versions, use_hash_suffix=False!
    """

    # str for backward compatibility
    cache_base: PrefixSuffix = UNDEFINED
    cache_dir: PrefixSuffix = field(
        init=False,
        repr=True,
        default=CREATE_CACHE_DIR_IN_BASE_DIR,
    )
    # use_hash_suffix: bool = field(init=True, repr=True, default=True) # wtf why did I want to disable the hash-suffix! its all about hashing here!
    overwrite_cache: bool = field(init=True, repr=False, default=False)
    _json_file_name: ClassVar[str] = "dataclass.json"
    __exclude_from_hash__: ClassVar[list[str]] = []
    clean_on_fail: bool = field(default=True, repr=False)

    @property
    def dataclass_json(self) -> str:
        return f"{self.cache_dir}/{self._json_file_name}"

    @property
    def _is_ready(self) -> bool:
        """
        looks somehow ugly, but necessary in order to prevent build of dependencies when actually already cached
        if is_ready is True does prevent complete build: not building cache not even loading caches (of nodes further up in the graph)!!
        # TODO: could enforce here that all runtime-dependencies are ready, concepts of build-time vs. runtime not yet implemented!!!
        """
        is_ready = self._was_built
        if not is_ready:
            is_ready = self._found_and_loaded_from_cache()
        return is_ready

    def _found_and_loaded_from_cache(self) -> bool:
        self.cache_dir = create_cache_dir_with_hash_suffix(self, self.cache_base)
        if self.overwrite_cache:
            remove_if_exists(str(self.cache_dir))
            successfully_loaded_cached = False
        elif self._check_cached_data():
            self._load_cached_data()
            self._post_build_setup()
            successfully_loaded_cached = True
        else:
            successfully_loaded_cached = False

        return successfully_loaded_cached

    @property
    @abstractmethod
    def name(self) -> str:
        """
        just to increase cached-data "readability", this is no id! no need to be "unique"
        enforcing this! readability is user-friendly!
        """
        raise NotImplementedError

    @abstractmethod
    def _build_cache(self) -> None:
        raise NotImplementedError

    def _build_self(self) -> None:
        all_undefined_must_be_filled(self)
        assert self.cache_dir is not CREATE_CACHE_DIR_IN_BASE_DIR

        cadi = str(self.cache_dir)
        shutil.rmtree(cadi, ignore_errors=True)
        Path(cadi).mkdir(parents=True)
        try:
            self._build_cache()
            write_json(self.dataclass_json, encode_dataclass(self), do_flush=True)
        except Exception:
            if self.clean_on_fail:
                shutil.rmtree(cadi, ignore_errors=True)  # should not raise an error
            raise

        self._post_build_setup()

    def _check_cached_data(self) -> bool:
        """
        default is to assume that valid data is found when there is a dataclass.json file
        you can override this method to implement whatever logic to check whether data is cached already
        """
        return Path(self.dataclass_json).is_file()

    def _post_build_setup(self) -> None:
        """
        use this to prepare stuff, last step in build_or_load, called after build_cache and _load_cached_data
        might be building children even though loaded from cache, cannot enforce that all laoded children are "ready"
        might be that some are only "build-time" dependencies
        """

    def _load_cached_data(self) -> None:
        cache_data_json = read_file(self.dataclass_json)
        loaded_dc = deserialize_dataclass(cache_data_json)
        repr_fields = [f for f in fields(self) if hasattr(loaded_dc, f.name)]
        for f in repr_fields:
            setattr(self, f.name, getattr(loaded_dc, f.name))
        _check_that_loading_went_well(self, loaded_dc)
