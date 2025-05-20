# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#      http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from collections.abc import Mapping
from typing import Callable, cast

import numpy as np
import scaluq

from quri_parts.circuit import (
    LinearMappedParametricQuantumCircuit,
    ParametricQuantumCircuit,
    QuantumCircuit,
    QuantumGate,
    ParametricQuantumGate,
    gates,
)

from quri_parts.circuit.gate_names import (
    MultiQubitGateNameType,
    SingleQubitGateNameType,
    ThreeQubitGateNameType,
    TwoQubitGateNameType,
    ParametricGateNameType,
    is_gate_name,
    is_multi_qubit_gate_name,
    is_parametric_gate_name,
    is_single_qubit_gate_name,
    is_three_qubit_gate_name,
    is_two_qubit_gate_name,
    is_unitary_matrix_gate_name,
)

from quri_parts.circuit.transpile import (
    SingleQubitUnitaryMatrix2RYRZTranspiler,
    TwoQubitUnitaryMatrixKAKTranspiler,
)

import sys
import os


# 現在の作業ディレクトリを取得
script_dir = os.getcwd()
script_dir = script_dir.replace("/jikken", "")
target_path =  script_dir + "/packages/scaluq"
# sys.path に追加
#sys.path.append(target_path)
sys.path.insert(0, target_path)
print(sys.path)
#sys.path.append("/home/rest/baito/quri-parts/packages/scaluq")
#import

from quri_parts.scaluq.circuit import (
    scaluq_circuit_helper_function,
    convert_circuit_f32,
    convert_parametric_circuit_f32,
    convert_gate_f32,
    convert_parametric_gate_f32,
    dense_matrix_gate_scaluq_f32
)

def a():
    scaluq_circuit_helper_function()

#a()

def helper():
    print("helper: test_convert_circuit.py")

def gates_equal_f32(g1: scaluq.f32.Gate, g2: scaluq.f32.Gate) -> bool:
    def gate_info(
            g: scaluq.f32.Gate,
    ) -> tuple[str,list[int],list[int]]:
        return (
            g.gate_type(),
            g.target_qubit_list(),
            g.control_qubit_list(),
        )
    
    return (gate_info(g1) == gate_info(g2)) and cast(
        bool, np.all(g1.get_matrix() == g2.get_matrix())
    )

#TODO gate type error bindingが問題?

def param_gates_equal_f32(g1: scaluq.f32.ParamGate, g2: scaluq.f32.ParamGate) -> bool:
    def gate_info(
            g: scaluq.f32.ParamGate,
    ) -> tuple[list[int],list[int]]:
        return (

            g.target_qubit_list(),
            g.control_qubit_list(),
        )
    #TODO get matrix
    return (gate_info(g1) == gate_info(g2))


single_qubit_gate_mapping_f32: Mapping[
    Callable[[int], QuantumGate], Callable[[int], scaluq.f32.Gate]
] = {
    gates.Identity: scaluq.f32.gate.I,
    gates.X: scaluq.f32.gate.X,
    gates.Y: scaluq.f32.gate.Y,
    gates.Z: scaluq.f32.gate.Z,
    gates.H: scaluq.f32.gate.H,
    gates.S: scaluq.f32.gate.S,
    gates.Sdag: scaluq.f32.gate.Sdag,
    gates.SqrtX: scaluq.f32.gate.SqrtX,
    gates.SqrtXdag: scaluq.f32.gate.SqrtXdag,
    gates.SqrtY: scaluq.f32.gate.SqrtY,
    gates.SqrtYdag: scaluq.f32.gate.SqrtYdag,
    gates.T: scaluq.f32.gate.T,
    gates.Tdag: scaluq.f32.gate.Tdag,
}


def test_convert_single_qubit_gate_f32() -> None:
    for qp_fac, sq_gate in single_qubit_gate_mapping_f32.items():
        #TODO I のみtargetを引数として受け取らないようになっている　確認
        g = qp_fac(7)
        if g.name == "Identity":
            continue
        print("g: ", g)
        converted = convert_gate_f32(g)
        expected = sq_gate(7)
        assert gates_equal_f32(converted, expected)

two_qubit_gate_mapping_f32: Mapping[
    Callable[[int,int],QuantumGate],Callable[[int,int],scaluq.f32.Gate]
] = {
    gates.CNOT: scaluq.f32.gate.CX,
    gates.SWAP: scaluq.f32.gate.Swap,
    gates.CZ: scaluq.f32.gate.CZ,
}

def test_convert_two_qubit_gate_f32() -> None:
    for qp_fac, sq_gate in two_qubit_gate_mapping_f32.items():
        g = qp_fac(11, 7)
        print("g: ", g)
        converted = convert_gate_f32(g)
        expected = sq_gate(11, 7)
        assert gates_equal_f32(converted, expected)

three_qubit_gate_mapping_f32: Mapping[
    Callable[[int,int,int],QuantumGate],
    Callable[[int,int,int],scaluq.f32.Gate]
] = {
    gates.TOFFOLI: scaluq.f32.gate.Toffoli,
}

def test_convert_three_qubit_gate_f32() -> None:
    for qp_fac, sq_gate in three_qubit_gate_mapping_f32.items():
        g = qp_fac(11, 7, 5)
        print("g: ", g)
        converted = convert_gate_f32(g)
        expected = sq_gate(11, 7, 5)
        assert gates_equal_f32(converted, expected)

rotation_gate_mapping_f32: Mapping[
    Callable[[int,float],QuantumGate],Callable[[int,float],scaluq.f32.Gate]
] = {
    gates.RX: scaluq.f32.gate.RX,
    gates.RY: scaluq.f32.gate.RY,
    gates.RZ: scaluq.f32.gate.RZ,
}

def test_convert_rotation_gate_f32() -> None:
    print("test_convert_rotation_gate_f32")
    for qp_fac, sq_gate in rotation_gate_mapping_f32.items():
        g = qp_fac(7, 0.125)
        converted = convert_gate_f32(g)
        expercted = sq_gate(7, 0.125)
        assert gates_equal_f32(converted, expercted)   

def test_convert_unitary_matrix_gate_f32() -> None:
    print("test_convert_unitary_matrix_gate")
    umat = ((1, 0), (0, np.cos(np.pi / 4) + 1j * np.sin(np.pi / 4)))
    expected = dense_matrix_gate_scaluq_f32(7, umat)
    converted = convert_gate_f32(gates.UnitaryMatrix((7,), umat))
    print("converted: ", converted.gate_type())
    print("expected: ", expected.gate_type())
    assert gates_equal_f32(converted, expected)

def test_convert_u_gate_f32() -> None:
    for g, expected in [
        (gates.U1(7, 0.125), scaluq.f32.gate.U1(7, 0.125)),
        (gates.U2(7, 0.125, -0.125), scaluq.f32.gate.U2(7, 0.125, -0.125)),
        (gates.U3(7, 0.125, -0.125, 0.625), scaluq.f32.gate.U3(7, 0.125, -0.125, 0.625)),
    ]:
        converted = convert_gate_f32(g)
        assert gates_equal_f32(converted, expected)

def test_convert_pauli_gate_f32() -> None:
    print("test_convert_unitary_pauli_gate")
    g = gates.Pauli((11, 7, 13), (2, 3, 1))
    converted = convert_gate_f32(g)
    pauli_ope = scaluq.f32.PauliOperator([11,7,13],[2,3,1])
    expected = scaluq.f32.gate.Pauli(pauli_ope)
    assert gates_equal_f32(converted, expected)

def test_convert_pauli_rotation_gate_f32() -> None:
    print("test_convert_pauli_rotation_gate")
    g = gates.PauliRotation((11, 7, 13), (2, 3, 1), 0.125)
    converted = convert_gate_f32(g)
    pauli_ope = scaluq.f32.PauliOperator([11,7,13],[2,3,1])
    expected = scaluq.f32.gate.PauliRotation(pauli_ope, 0.125)
    assert gates_equal_f32(converted, expected)

#TODO 
_single_parametric_gate_mapping_f32: Mapping[
    Callable[[int,float],ParametricQuantumGate],Callable[[int,float],scaluq.f32.Gate]
] = {
    gates.ParametricRX: scaluq.f32.gate.ParamRX,
    gates.ParametricRY: scaluq.f32.gate.ParamRY,
    gates.ParametricRZ: scaluq.f32.gate.ParamRZ,
}

def test_convert_parametric_gate_f32() -> None:
    print("test_convert_parametric_gate_f32")
    for qp_fac, sq_gate in _single_parametric_gate_mapping_f32.items():
        g = qp_fac(7)
        converted = convert_parametric_gate_f32(g)
        expected = sq_gate(7)
        assert param_gates_equal_f32(converted, expected)


def test_convert_circuit_f32() -> None:
    circuit = QuantumCircuit(3)
    original_gates = [
        gates.X(1),
        gates.H(2),
        gates.CNOT(0, 2),
        gates.RX(0, 0.125),
        gates.TOFFOLI(2, 0, 1),
    ]

    for g in original_gates:
        circuit.add_gate(g)

    converted = convert_circuit_f32(circuit)
    assert converted.n_qubits() == 3

    expected_gates = [
        scaluq.f32.gate.X(1),
        scaluq.f32.gate.H(2),
        scaluq.f32.gate.CX(0, 2),
        scaluq.f32.gate.RX(0, 0.125),
        scaluq.f32.gate.Toffoli(2, 0, 1),
    ]

    assert converted.n_gates() == len(expected_gates)
    for i, expected in enumerate(expected_gates):
        assert gates_equal_f32(converted.get_gate_at(i), expected)


param_gate_mapping_f32: Mapping[
    Callable[[int,float],QuantumGate],Callable[[int,float],scaluq.f32.Gate]
] = {
    gates.ParametricRX: scaluq.f32.gate.ParamRX,
    gates.ParametricRY: scaluq.f32.gate.ParamRY,
    gates.ParametricRZ: scaluq.f32.gate.ParamRZ,
    gates.ParametricPauliRotation: scaluq.f32.gate.ParamPauliRotation,
}

#TODO 多分ok
def test_convert_parametric_circuit() -> None:
    circuit = ParametricQuantumCircuit(3)
    circuit.add_X_gate(0)
    circuit.add_ParametricRX_gate(0)
    circuit.add_H_gate(2)
    circuit.add_ParametricRY_gate(1)
    circuit.add_CNOT_gate(0, 2)
    circuit.add_ParametricRZ_gate(2)
    circuit.add_RX_gate(0, 0.125)
    #TODO
    circuit.add_ParametricPauliRotation_gate((0, 1, 2), (1, 2, 3))


    converted, param_mapper = convert_parametric_circuit_f32(circuit)
    print("param_mapper ",param_mapper)
    print("converted: ", converted)
    print("set",converted.key_set())
    print(converted.get_gate_at(1))
    print(converted.get_gate_at(3))
    print(converted.get_gate_at(5))

    assert converted.n_qubits() == 3

    expected_gates = [
        scaluq.f32.gate.X(0),
        scaluq.f32.gate.ParamRX(0),
        scaluq.f32.gate.H(2),
        scaluq.f32.gate.ParamRY(1),
        scaluq.f32.gate.CX(0, 2),
        scaluq.f32.gate.ParamRZ(2),
        scaluq.f32.gate.RX(0, 0.125),
        scaluq.f32.gate.ParamPauliRotation(
            scaluq.f32.PauliOperator([0, 1, 2], [1, 2, 3]),
            0,
        ),
    ]

    assert converted.n_gates() == len(expected_gates)

    for i, expected in enumerate(expected_gates):
        if isinstance(expected, scaluq.f32.ParamGate):
            tmp = converted.get_gate_at(i)
            assert param_gates_equal_f32(tmp[0], expected)
        else:
            assert gates_equal_f32(converted.get_gate_at(i), expected)


