#qulacs の initのコピー
from typing import Sequence, Union, cast

from numpy.typing import ArrayLike
from typing_extensions import TypeAlias, TypeVar

from quri_parts.core.state import (
    CircuitQuantumState,
    ParametricCircuitQuantumState,
    ParametricQuantumStateVector,
    QuantumStateVector,
)


scaluqStateT : TypeAlias = Union[CircuitQuantumState, QuantumStateVector]
scaluqParametricStateT : TypeAlias = Union[
    ParametricCircuitQuantumState, ParametricQuantumStateVector
]

Numerics = TypeVar("Numerics", int, float, complex)

def cast_to_list(int_sequence: Union[Sequence[Numerics], ArrayLike]) -> list[Numerics]:

    return cast(list[Numerics], int_sequence)

def helper_function():
    print("helper function from quri_parts")