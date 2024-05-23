from slugify import slugify


def slugify_with_underscores(s: str) -> str:
    regex_pattern_to_allow_underscores = r"[^-a-z0-9_]+"
    return slugify(s, regex_pattern=regex_pattern_to_allow_underscores)


def slugify_en_only(s: str) -> str:
    return slugify(s, regex_pattern=r"[^-a-z0-9]+")


def slugify_cased_en_only(s: str) -> str:
    return slugify(s, regex_pattern=r"[^-a-zA-Z0-9]+", lowercase=False)
