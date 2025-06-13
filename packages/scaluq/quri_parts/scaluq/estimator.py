0# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#      http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from collections.abc import Collection, Iterable, Sequence,Mapping
from typing import TYPE_CHECKING, Any, Callable, NamedTuple, Optional, Union


import os
import importlib
from typing import Any

from quri_parts.circuit.noise import NoiseModel
from quri_parts.core.estimator import (
    ConcurrentParametricQuantumEstimator,
    ConcurrentQuantumEstimator,
    Estimatable,
    Estimate,
    GeneralQuantumEstimator,
    ParametricQuantumEstimator,
    QuantumEstimator,
    create_parametric_estimator,
)
from quri_parts.core.operator import zero
from quri_parts.core.state import ParametricQuantumStateVector, QuantumStateVector
from quri_parts.core.utils.concurrent import execute_concurrently

from quri_parts.scaluq import scaluqStateT, scaluqParametricStateT


_precision = os.environ.get('SCALUQ_PRECISION', 'f64').lower()
if _precision not in ['f32', 'f64']:
    raise ImportError(
        f"環境変数 SCALUQ_PRECISION に不正な値 '{_precision}' が指定されました。"
        " 'f32' または 'f64' を選択してください。"
    )
_module_name = f"scaluq.default.{_precision}"
try:
    _backend: Any = importlib.import_module(_module_name)
    print(f"[Info] Library 'a' is using backend: {_module_name}")
except ImportError as e:
    raise ImportError(f"指定されたscaluqバックエンド '{_module_name}' のインポートに失敗しました。") from e

from . import cast_to_list
from .circuit import convert_circuit, convert_parametric_circuit
from .operator import convert_operator


class _Estimate(NamedTuple):
    value: complex
    error: float = 0.0

def _create_scaluq_initial_state(
        state : scaluqStateT
) -> _backend.StateVector:
    sq_state = _backend.StateVector(state.qubit_count)
    if isinstance(state, (QuantumStateVector, ParametricQuantumStateVector)):
        sq_state.load(cast_to_list(state.vector))
    return sq_state

#TODO compile circuit 
def _estimate(operator: Estimatable, state: scaluqStateT) -> Estimate[complex]:
    if operator == zero():
        return _Estimate(value=0.0)
    
    circuit = convert_circuit(state.circuit)
    sq_state = _create_scaluq_initial_state(state)

    op = convert_operator(operator, state.qubit_count)
    circuit.update_quantum_state(sq_state)
    exp = op.get_expectation_value(sq_state)
    
    return _Estimate(value=exp)


def _sequential_parametric_estimate(
    op_state: tuple[Estimatable, scaluqParametricStateT],
    params: Sequence[Sequence[float]],
) -> Sequence[Estimate[complex]]:
    operator, state = op_state
    n_qubits = state.qubit_count
    op = convert_operator(operator, n_qubits)
    parametric_circuit = state.parametric_circuit

    #TODO
    scaluq_circuit, param_mapper = convert_parametric_circuit(parametric_circuit)

    #print(scaluq_circuit.gate_list)
    estimates = []
    for param in params:
        tmp_params :Mapping[str,float] = {} 
        for i in range(len(param)):
            tmp_params[str(i)] = param[i]
        

        sq_state = _create_scaluq_initial_state(state)
        scaluq_circuit.update_quantum_state(sq_state,tmp_params)
        exp = op.get_expectation_value(sq_state)
        estimates.append(_Estimate(value=exp))

    return estimates


#TODO
"""
def _batched_parametric_estimate(
        op_state:  tuple[Estimatable, scaluqParametricStateT],
        params: Sequence[Sequence[float]],
) -> Sequence[Estimate[complex]],
    
    operator, state = op_state
    n_qubits = state.qubit_count
    op = convert_operator(operator, n_qubits)
    parametric_circuit = state.parametric_circuit

    scaluq_circuit, param_mapper = convert_parametric_circuit(parametric_circuit)

    sq_state_batched = _create_scaluq_initial_state_batched(state)
    scaluq_circuit.update_quantum_state(sq_state,params)
    #TODO 実装街
    exp = op.get_expectation_value_batched(sq_state)
    return exp

"""

def create_scaluq_vector_estimator() -> QuantumEstimator[scaluqStateT]:
    return _estimate

def create_scaluq_vector_parametric_estimator() ->(
        ParametricQuantumEstimator[scaluqParametricStateT]
):
    def estimator(
            operator: Estimatable,state: scaluqParametricStateT, param: Sequence[float]
    ) -> Estimate[complex]:
        ests = _sequential_parametric_estimate((operator, state),[param])
        return ests[0]
    return estimator
"""

#TODO
def create_scaluq_vector_batched_estimator(
        executer
) -> 
    def estimator(
        operator: Estimatable,
        state: scaluqParametricStateT,
        params: Sequence[Sequence[float]],
    ) -> Sequence[Estimate[complex]]:
        return 



    return estimator

    """