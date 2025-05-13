# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#      http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from collections.abc import Collection, Iterable, Sequence
from typing import TYPE_CHECKING, Any, Callable, NamedTuple, Optional, Union

import scaluq

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

class _Estimate(NamedTuple):
    value: complex
    error: float = 0.0



def _create_scaluq_initial_state(
        state : scaluqStateT
) -> scaluq.f64.StateVector:
    sq_state = scaluq.f64.StateVector(state.qubit_count)
    if isinstance(state, (QuantumStateVector, ParametricQuantumStateVector)):
        sq_state.load

    return sq_state

def _estimate(operator: Estimatable, state: scaluq.f64.StateVector) -> Estimate[complex]:
    if operator == zero():
        return _Estimate(value=0.0)
    # is insatanse

    sq_state = _create_scaluq_initial_state(state)
    op = convert_operator(operator, state.qubit_count)
    circuit.update_quantum_state(sq_state)
    exp = op.get_expectation_value(sq_state)
    return _Estimate(value=exp)

def create_scaluq_vector_estimator() ->:
    return _estimate


def _concurrent_estimate(
        
)
    
def create_scaluq_vector_concurrent_estimator(
               
):
    def estimator(
            operators: Collection[Estimatable],
            steates: Collection[scaluq.f64.StateVector],

    )
    
    return estimator