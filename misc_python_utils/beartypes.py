import dataclasses
import logging
import warnings
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Any, Protocol, TypeVar

from beartype import BeartypeConf, BeartypeStrategy, beartype
from beartype.roar import BeartypeCallException, BeartypeClawDecorWarning
from beartype.vale import Is, IsAttr, IsEqual

logger = logging.getLogger(
    __name__,
)  # "The name is potentially a period-separated hierarchical", see: https://docs.python.org/3.10/library/logging.html


warnings.simplefilter("error", category=BeartypeClawDecorWarning)
# turns beartype-warning into an error, cause otherwise beartype might be unable to validate function input/output types, if one of thm is invalid

#  pyright: reportUnknownLambdaType=false
#  pyright: reportUnknownMemberType=false
#  pyright: reportUnknownVariableType=false
#  pyright: reportUnknownArgumentType=false


@dataclasses.dataclass
class BearBully:
    ne_string: Annotated[str, Is[lambda s: len(s) > 0]]


# TODO: strange it ignores/overwrites? my -O !!
def bear_does_roar(roar_trigger_fun: Callable) -> bool:
    did_roar = False
    try:
        roar_trigger_fun()
    except BeartypeCallException:
        did_roar = True
    return did_roar


assert bear_does_roar(lambda: BearBully(""))

# if TYPE_CHECKING or not __debug__:
#     logger.warning("you disabled beartype!")

#     def nobeartype(  # type: ignore[no-redef]
#         obj: BeartypeableT,
#         *,
#         conf: BeartypeConf = BEARTYPE_CONF_DEFAULT,  # noqa: ARG001
#     ) -> BeartypeReturn:
#         return obj

# else:
nobeartype = beartype(conf=BeartypeConf(strategy=BeartypeStrategy.O0))

File = Annotated[
    str,
    Is[lambda f: Path(f).is_file() or Path(f"{Path.cwd()}/{f}").is_file()],
]
ExistingFile = File  # TODO: rename
Directory = Annotated[str, Is[lambda f: Path(f).is_dir()]]
# -------------------------------------------------------------------------------------
# ----              NUMPY TYPES
# -------------------------------------------------------------------------------------

NDIM = "ndim"
is_1_dimensional = IsAttr[NDIM, IsEqual[1]]


class HasShapeP(Protocol):
    shape: tuple[int, ...]


try:  # noqa: WPS229
    # see: https://beartype.readthedocs.io/en/latest/api_vale/#api-numpy
    from numpy import float32, floating, int16, int32, integer, number
    from numpy.typing import NDArray

    firstdim_nonempty = lambda x: x.shape[0] > 0
    seconddim_nonempty = lambda x: x.shape[1] > 0

    if TYPE_CHECKING:
        # otherwise pyright complains about missing type arguments!
        NpFloat = floating[Any]
        NpInt = integer[Any]
        NpNumber = number[Any]
    else:
        # beartype does not like Any in type-argument of annotation
        NpFloat = floating
        NpInt = integer
        NpNumber = number

    # 1 Dimensional
    NpNumberDim1 = Annotated[NDArray[NpNumber], is_1_dimensional]
    NeNpNumberDim1 = Annotated[NpNumberDim1, Is[firstdim_nonempty]]

    NpFloatDim1 = Annotated[NDArray[NpFloat], is_1_dimensional]

    NpFloat32Dim1 = Annotated[NDArray[float32], is_1_dimensional]
    NpInt16Dim1 = Annotated[NDArray[int16], is_1_dimensional]

    NpIntDim1 = Annotated[NDArray[NpInt], IsAttr[NDIM, IsEqual[1]]]
    NeNpIntDim1 = Annotated[NpIntDim1, Is[firstdim_nonempty]]
    NeNpInt16Dim1 = Annotated[NpInt16Dim1, Is[firstdim_nonempty]]

    NeNpFloatDim1 = Annotated[NpFloatDim1, Is[firstdim_nonempty]]
    NeNpFloat32Dim1 = Annotated[NpFloat32Dim1, Is[firstdim_nonempty]]

    # 2 Dimensional
    # NumpyArray = NDArray[number]
    NumpyFloat2DArray = Annotated[NDArray[NpFloat], IsAttr[NDIM, IsEqual[2]]]
    # brackets around multi-line conjunction, see:  https://github.com/beartype/beartype#validator-syntax

    NeNumpyFloat2DArray = Annotated[
        NDArray[NpFloat],
        (IsAttr[NDIM, IsEqual[2]] & Is[firstdim_nonempty] & Is[seconddim_nonempty]),
    ]
    # "Delimiting two or or more validators with commas at the top level ... is an alternate syntax for and-ing those validators with the & operator", see: https://github.com/beartype/beartype#validator-syntax

    NumpyFloat32_1D = Annotated[
        NDArray[float32],
        is_1_dimensional,
        Is[firstdim_nonempty],
    ]

    NumpyFloat2D = NeNumpyFloat2DArray

    NumpyInt16Dim1 = Annotated[NDArray[int16], is_1_dimensional]
    NumpyInt32Dim1 = Annotated[NDArray[int32], is_1_dimensional]

except ImportError as e:
    logger.warning(f"{e}")
T = TypeVar("T")

NeStr = Annotated[str, Is[lambda s: len(s) > 0]]
Dataclass = Annotated[object, Is[dataclasses.is_dataclass]]
# StrOrBytesInstance = Annotated[object, IsInstance[str]]

T2 = TypeVar("T2")

NeSequence = Annotated[Sequence[T], Is[lambda x: len(x) > 0]]
NeList = Annotated[list[T], Is[lambda lst: len(lst) > 0]]
NeDict = Annotated[dict[T, T2], Is[lambda d: len(d.keys()) > 0]]
NeTuple = Annotated[
    tuple[T, ...], Is[lambda tpl: len(tpl) > 0]  # noqa: COM812
]  # typing.TypeAlias currently unsupported by @beartype
# NotNone = Annotated[Any, Is[lambda x:x is None]] # TODO: not working!


# -------------------------------------------------------------------------------------
# ----              TORCH TYPES
# -------------------------------------------------------------------------------------

try:  # noqa: WPS229
    import torch

    TorchTensor3D = Annotated[torch.Tensor, IsAttr[NDIM, IsEqual[3]]]
    TorchTensor2D = Annotated[torch.Tensor, IsAttr[NDIM, IsEqual[2]]]
    TorchTensor1D = Annotated[torch.Tensor, is_1_dimensional]

    # https://github.com/beartype/beartype/issues/98
    # PEP-compliant type hint matching only a floating-point PyTorch tensor.
    TorchTensorFloat = Annotated[
        torch.Tensor,
        Is[lambda tens: torch.is_floating_point(tens)],
    ]

    TorchTensorFloat2D = Annotated[
        torch.Tensor,
        IsAttr[NDIM, IsEqual[2]] & Is[lambda tens: torch.is_floating_point(tens)],
    ]

    # see: https://stackoverflow.com/questions/72253473/how-to-judge-a-torch-tensor-dtype-is-int-or-not -> TODO: sure?
    TorchTensorInt = Annotated[
        torch.Tensor,
        Is[lambda tens: not torch.is_floating_point(tens)],
    ]

    # where is this from ?
    TorchTensorFirstDimAsTwo = Annotated[
        torch.Tensor,
        IsAttr["shape", Is[lambda shape: shape[0] == 2]],  # noqa: PLR2004
    ]

except ImportError:
    pass
