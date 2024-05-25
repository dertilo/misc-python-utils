from typing import Annotated

from beartype.vale import Is
from slugify import slugify

from misc_python_utils.beartypes import NeStr


def slugify_with_underscores(s: str) -> str:
    regex_pattern_to_allow_underscores = r"[^-a-z0-9_]+"
    return slugify(s, regex_pattern=regex_pattern_to_allow_underscores)


def slugify_en_only(s: str) -> str:
    return slugify(s, regex_pattern=r"[^-a-z0-9]+")


def slugify_cased_en_only(s: str) -> str:
    return slugify(s, regex_pattern=r"[^-a-zA-Z0-9]+", lowercase=False)


SlugStr = Annotated[NeStr, Is[lambda s: slugify_with_underscores(s) == s]]
NameSlug = Annotated[NeStr, Is[lambda s: slugify_en_only(s) == s]]
CasedNameSlug = Annotated[NeStr, Is[lambda s: slugify_cased_en_only(s) == s]]
