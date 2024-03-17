# https://askubuntu.com/questions/528928/how-to-do-underline-bold-italic-strikethrough-color-background-and-size-i
# TODO: probably
from collections.abc import Callable

SE = "\033"
# colors: curl -s https://gist.githubusercontent.com/HaleTom/89ffe32783f89f403bba96bd7bcd1263/raw/ | bash
CMDLINE_STYLES = {
    "bold": lambda s: f"{SE}[1m{s}{SE}[0m",
    "striked": lambda s: f"{SE}[9m{s}{SE}[0m",
    "None": lambda s: s,
    "red": lambda s: f"{SE}[31m{s}{SE}[0m",
    "bg-red": lambda s: f"{SE}[48;5;196m{s}{SE}[49m",
    "bg-green": lambda s: f"{SE}[48;5;42m{s}{SE}[49m",
    "bg-yellow": lambda s: f"{SE}[48;5;226m{s}{SE}[49m",
}


def build_bg_color(k: int) -> Callable[[str], str]:
    return lambda s: f"{SE}[48;5;{k}m{s}{SE}[49m"


CMDLINE_BACKGROUND_COLORS = {
    f"bg-{kk}": build_bg_color(kk) for kk in [187, 255, 181, 136, 252, 138, 195, 231]
}


if __name__ == "__main__":
    s = "Hello World"
    for n, fun in CMDLINE_BACKGROUND_COLORS.items():
        print(f"{n}:{fun(s)}")  # noqa: T201
