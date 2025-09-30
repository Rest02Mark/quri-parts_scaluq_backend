import math
from typing import Union

import numpy as np
import pytest
import sys
import os

from quri_parts.circuit import ParametricQuantumCircuit, QuantumCircuit
from quri_parts.circuit.noise import BitFlipNoise, NoiseModel
from quri_parts.core.estimator import GeneralQuantumEstimator
from quri_parts.core.operator import Operator, PauliLabel, pauli_label
from quri_parts.core.state import (
    ComputationalBasisState,
    GeneralCircuitQuantumState,
    ParametricCircuitQuantumState,
    ParametricQuantumStateVector,
    QuantumStateVector,
    StateVectorType,
)

# 現在の作業ディレクトリを取得
script_dir = os.getcwd()
script_dir = script_dir.replace("/jikken", "")
target_path =  script_dir + "/packages/scaluq"
sys.path.insert(0, target_path)


from quri_parts.scaluq import scaluqParametricStateT
from quri_parts.scaluq.estimator import(
    _Estimate,
    create_scaluq_vector_estimator,
    create_scaluq_vector_parametric_estimator,
    create_scaluq_vector_batched_parametric_estimator
)

def create_vector(qubit_count: int, bits: int) -> StateVectorType:
    vector: StateVectorType = np.zeros(2**qubit_count, dtype=np.complex128)
    vector[bits] = 1.0
    return vector


def create_vector_state(qubit_count: int, bits: int) -> QuantumStateVector:
    return QuantumStateVector(qubit_count, create_vector(qubit_count, bits))

class TestVectorEstimator:
    def test_estimate_pauli_label(self) -> None:
        pauli = pauli_label("Z0 Z2 Z5")
        state = ComputationalBasisState(6, bits=0b110010)
        estimator = create_scaluq_vector_estimator()
        estimate = estimator(pauli, state)

        #print("estimate.value:",estimate.value)
        #print("estimate.error:",estimate.error)
        assert estimate.value == -1
        assert estimate.error == 0

    def test_estimate_operator(self) -> None:
        operator = Operator(
            {
                pauli_label("Z0 Z2 Z5"): 0.25,
                pauli_label("Z1 Z2 Z4"): 0.5j,
            }
        )
        state = ComputationalBasisState(6, bits=0b110010)
        estimator = create_scaluq_vector_estimator()
        estimate = estimator(operator, state)
        assert estimate.value == -0.25 + 0.5j
        assert estimate.error == 0

    def test_estimate_vector(self) -> None:
        pauli = pauli_label("Z0 Z2 Z5")
        state = create_vector_state(6, 0b110010)
        estimator = create_scaluq_vector_estimator()
        estimate = estimator(pauli, state)
        assert estimate.value == -1
        assert estimate.error == 0

#TODO

def parametric_circuit() -> ParametricQuantumCircuit:
    circuit = ParametricQuantumCircuit(6)

    circuit.add_RX_gate(0, -math.pi / 4)
    circuit.add_ParametricRX_gate(0)

    circuit.add_RY_gate(2, -math.pi / 4)
    circuit.add_ParametricRY_gate(2)

    circuit.add_H_gate(5)
    circuit.add_RZ_gate(5, -math.pi / 4)
    circuit.add_ParametricRZ_gate(5)

    circuit.add_ParametricPauliRotation_gate((0, 2, 5), (1, 2, 3))

    return circuit


def create_parametric_vector_state(
    qubit_count: int,
    circuit: ParametricQuantumCircuit,
    bits: int,
) -> ParametricQuantumStateVector:
    return ParametricQuantumStateVector(
        qubit_count, circuit, create_vector(qubit_count, bits)
    )

class TestVectorParametricEstimator:
    def test_estimate_pauli_label(self) -> None:
        pauli = pauli_label("Y0 X2 Y5")
        state = ParametricCircuitQuantumState(6, parametric_circuit())
        estimator = create_scaluq_vector_parametric_estimator()

        params = [0.0, 0.0, 0.0, 0.0]
        estimate = estimator(pauli, state, params)
        assert estimate.value == pytest.approx((1 / math.sqrt(2)) ** 3)
        assert estimate.error == 0

        params = [-math.pi / 4, 0, 0, 0]
        estimate = estimator(pauli, state, params)
        assert estimate.value == pytest.approx(0.5)
        assert estimate.error == 0

        params = [0, -math.pi / 4, 0, 0]
        estimate = estimator(pauli, state, params)
        assert estimate.value == pytest.approx(0.5)
        assert estimate.error == 0

        params = [0, 0, -math.pi / 4, 0]
        estimate = estimator(pauli, state, params)
        assert estimate.value == pytest.approx(0.5)
        assert estimate.error == 0

        #TODO abs外すとエラー
        params = [0, 0, 0, -math.pi / 4]
        estimate = estimator(pauli, state, params)
        assert estimate.value == pytest.approx(0,abs=1e-7)
        assert estimate.error == 0


    def test_estimate_operator(self) -> None:
        operator = Operator(
            {
                pauli_label("Y0 X2 Y5"): 0.25,
                pauli_label("Z1 X2 Z4"): 0.5j,
            }
        )
        state = ParametricCircuitQuantumState(6, parametric_circuit())
        estimator = create_scaluq_vector_parametric_estimator()

        params = [0.0, 0.0, 0.0, 0.0]
        estimate = estimator(operator, state, params)
        assert estimate.value == pytest.approx(
            0.25 * ((1 / math.sqrt(2)) ** 3) + 0.5j * (-1 / math.sqrt(2))
        )
        assert estimate.error == 0

        params = [-math.pi / 4, 0, 0, 0]
        estimate = estimator(operator, state, params)
        assert estimate.value == pytest.approx(0.25 * 0.5 + 0.5j * (-1 / math.sqrt(2)))
        assert estimate.error == 0

        params = [0, -math.pi / 4, 0, 0]
        estimate = estimator(operator, state, params)
        assert estimate.value == pytest.approx(0.25 * 0.5 + 0.5j * (-1))
        assert estimate.error == 0

        params = [0, 0, -math.pi / 4, 0]
        estimate = estimator(operator, state, params)
        assert estimate.value == pytest.approx(0.25 * 0.5 + 0.5j * (-1 / math.sqrt(2)))
        assert estimate.error == 0

        params = [0, 0, 0, -math.pi / 4]
        estimate = estimator(operator, state, params)
        assert estimate.value == pytest.approx(0 + 0.5j * (-0.5))
        assert estimate.error == 0


    def test_estimate_vector(self) -> None:
        pauli = pauli_label("Y0 X2 Y5")
        state = create_parametric_vector_state(6, parametric_circuit(), 0b100000)
        estimator = create_scaluq_vector_parametric_estimator()

        params = [0.0, 0.0, 0.0, 0.0]
        estimate = estimator(pauli, state, params)

        assert estimate.value == pytest.approx(-((1 / math.sqrt(2)) ** 3))
        assert estimate.error == 0

        params = [-math.pi / 4, 0, 0, 0]
        estimate = estimator(pauli, state, params)
        assert estimate.value == pytest.approx(-0.5)
        assert estimate.error == 0

        params = [0, -math.pi / 4, 0, 0]
        estimate = estimator(pauli, state, params)
        assert estimate.value == pytest.approx(-0.5)
        assert estimate.error == 0

        params = [0, 0, -math.pi / 4, 0]
        estimate = estimator(pauli, state, params)
        assert estimate.value == pytest.approx(-0.5)
        assert estimate.error == 0

        params = [0, 0, 0, -math.pi / 4]
        estimate = estimator(pauli, state, params)
        assert estimate.value == pytest.approx(0,abs=1e-7)
        assert estimate.error == 0

    #TODO
    def test_estimate_batched(self) -> None:
        pauli = pauli_label("Y0 X2 Y5")
        state = create_parametric_vector_state(6, parametric_circuit(), 0b100000)
        estimator = create_scaluq_vector_batched_parametric_estimator()

        params_list = [
            [0.0, 0.0, 0.0, 0.0],
            [-math.pi / 4, 0, 0, 0],
            [0, -math.pi / 4, 0, 0],
            [0, 0, -math.pi / 4, 0],
            [0, 0, 0, -math.pi / 4]
        ]

        estimate = estimator(pauli, state, params_list)

        assert estimate[0].value== pytest.approx(-((1 / math.sqrt(2)) ** 3))
        assert estimate[1].value== pytest.approx(-0.5)
        assert estimate[2].value== pytest.approx(-0.5)
        assert estimate[3].value== pytest.approx(-0.5)
        assert estimate[4].value== pytest.approx(0,abs=1e-7)

