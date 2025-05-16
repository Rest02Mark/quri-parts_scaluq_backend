# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#      http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from collections.abc import Iterable
from typing import Union

from typing_extensions import TypeAlias
import scaluq
from quri_parts.core.operator import Operator, PauliLabel, pauli_name

_OperatorKey: TypeAlias = Union[PauliLabel, frozenset[tuple[PauliLabel, complex]]]
_operator_cache: dict[tuple[_OperatorKey, int], scaluq.f32.Operator] = {}

#TODO

def convert_operator(
        operator: Union[Operator, PauliLabel], n_qubits: int 
) ->  scaluq.f32.Operator:
    
    op_key : _OperatorKey
    if isinstance(operator, PauliLabel):
        op_key = frozenset({(operator, 1.0)})
    else:
        op_key = frozenset(operator.items())
     
    if (op_key, n_qubits)