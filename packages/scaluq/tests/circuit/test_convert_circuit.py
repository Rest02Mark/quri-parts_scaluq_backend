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
import os
import importlib
from typing import Any
import numpy as np


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

#TODO delete
script_dir = os.getcwd()
script_dir = script_dir.replace("/jikken", "")
target_path =  script_dir + "/packages/scaluq"
sys.path.insert(0, target_path)
print(sys.path)

from quri_parts.scaluq.circuit import (
    convert_circuit,
    convert_parametric_circuit,
    convert_gate,
    convert_parametric_gate,
    dense_matrix_gate_scaluq
)

def gates_equal(g1: _backend.Gate, g2: _backend.Gate) -> bool:
    def gate_info(
            g: _backend.Gate,
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
def param_gates_equal(g1: _backend.ParamGate, g2: _backend.ParamGate) -> bool:
    def gate_info(
            g: _backend.ParamGate,
    ) -> tuple[list[int],list[int]]:
        return (

            g.target_qubit_list(),
            g.control_qubit_list(),
        )
    #TODO get matrix
    return (gate_info(g1) == gate_info(g2))


single_qubit_gate_mapping: Mapping[
    Callable[[int], QuantumGate], Callable[[int], _backend.Gate]
] = {
    gates.Identity: _backend.gate.I,
    gates.X: _backend.gate.X,
    gates.Y: _backend.gate.Y,
    gates.Z: _backend.gate.Z,
    gates.H: _backend.gate.H,
    gates.S: _backend.gate.S,
    gates.Sdag: _backend.gate.Sdag,
    gates.SqrtX: _backend.gate.SqrtX,
    gates.SqrtXdag: _backend.gate.SqrtXdag,
    gates.SqrtY: _backend.gate.SqrtY,
    gates.SqrtYdag: _backend.gate.SqrtYdag,
    gates.T: _backend.gate.T,
    gates.Tdag: _backend.gate.Tdag,
}


def test_convert_single_qubit_gate() -> None:
    for qp_fac, sq_gate in single_qubit_gate_mapping.items():
        #TODO I のみtargetを引数として受け取らないようになっている　確認
        g = qp_fac(7)
        if g.name == "Identity":
            continue
        print("g: ", g)
        converted = convert_gate(g)
        expected = sq_gate(7)
        assert gates_equal(converted, expected)

two_qubit_gate_mapping: Mapping[
    Callable[[int,int],QuantumGate],Callable[[int,int],_backend.Gate]
] = {
    gates.CNOT: _backend.gate.CX,
    gates.SWAP: _backend.gate.Swap,
    gates.CZ: _backend.gate.CZ,
}

def test_convert_two_qubit_gate() -> None:
    for qp_fac, sq_gate in two_qubit_gate_mapping.items():
        g = qp_fac(11, 7)
        print("g: ", g)
        converted = convert_gate(g)
        expected = sq_gate(11, 7)
        assert gates_equal(converted, expected)

three_qubit_gate_mapping: Mapping[
    Callable[[int,int,int],QuantumGate],
    Callable[[int,int,int],_backend.Gate]
] = {
    gates.TOFFOLI: _backend.gate.Toffoli,
}

def test_convert_three_qubit_gate() -> None:
    for qp_fac, sq_gate in three_qubit_gate_mapping.items():
        g = qp_fac(11, 7, 5)
        print("g: ", g)
        converted = convert_gate(g)
        expected = sq_gate(11, 7, 5)
        assert gates_equal(converted, expected)

rotation_gate_mapping: Mapping[
    Callable[[int,float],QuantumGate],Callable[[int,float],_backend.Gate]
] = {
    gates.RX: _backend.gate.RX,
    gates.RY: _backend.gate.RY,
    gates.RZ: _backend.gate.RZ,
}

def test_convert_rotation_gate() -> None:
    print("test_convert_rotation_gate")
    for qp_fac, sq_gate in rotation_gate_mapping.items():
        g = qp_fac(7, 0.125)
        converted = convert_gate(g)
        expercted = sq_gate(7, 0.125)
        assert gates_equal(converted, expercted)   

def test_convert_unitary_matrix_gate() -> None:
    print("test_convert_unitary_matrix_gate")
    umat = ((1, 0), (0, np.cos(np.pi / 4) + 1j * np.sin(np.pi / 4)))
    expected = dense_matrix_gate_scaluq(7, umat)
    converted = convert_gate(gates.UnitaryMatrix((7,), umat))
    print("converted: ", converted.gate_type())
    print("expected: ", expected.gate_type())
    assert gates_equal(converted, expected)

def test_convert_u_gate() -> None:
    for g, expected in [
        (gates.U1(7, 0.125), _backend.gate.U1(7, 0.125)),
        (gates.U2(7, 0.125, -0.125), _backend.gate.U2(7, 0.125, -0.125)),
        (gates.U3(7, 0.125, -0.125, 0.625), _backend.gate.U3(7, 0.125, -0.125, 0.625)),
    ]:
        converted = convert_gate(g)
        assert gates_equal(converted, expected)

def test_convert_pauli_gate() -> None:
    print("test_convert_unitary_pauli_gate")
    g = gates.Pauli((11, 7, 13), (2, 3, 1))
    converted = convert_gate(g)
    pauli_ope = _backend.PauliOperator([11,7,13],[2,3,1])
    expected = _backend.gate.Pauli(pauli_ope)
    assert gates_equal(converted, expected)

def test_convert_pauli_rotation_gate() -> None:
    print("test_convert_pauli_rotation_gate")
    g = gates.PauliRotation((11, 7, 13), (2, 3, 1), 0.125)
    converted = convert_gate(g)
    pauli_ope = _backend.PauliOperator([11,7,13],[2,3,1])
    expected = _backend.gate.PauliRotation(pauli_ope, 0.125)
    assert gates_equal(converted, expected)


_single_parametric_gate_mapping: Mapping[
    Callable[[int,float],ParametricQuantumGate],Callable[[int,float],_backend.Gate]
] = {
    gates.ParametricRX: _backend.gate.ParamRX,
    gates.ParametricRY: _backend.gate.ParamRY,
    gates.ParametricRZ: _backend.gate.ParamRZ,
}

def test_convert_parametric_gate() -> None:
    print("test_convert_parametric_gate")
    for qp_fac, sq_gate in _single_parametric_gate_mapping.items():
        g = qp_fac(7)
        converted = convert_parametric_gate(g)
        expected = sq_gate(7)
        assert param_gates_equal(converted, expected)


def test_convert_circuit() -> None:
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

    converted = convert_circuit(circuit)
    assert converted.n_qubits() == 3

    expected_gates = [
        _backend.gate.X(1),
        _backend.gate.H(2),
        _backend.gate.CX(0, 2),
        _backend.gate.RX(0, 0.125),
        _backend.gate.Toffoli(2, 0, 1),
    ]

    assert converted.n_gates() == len(expected_gates)
    for i, expected in enumerate(expected_gates):
        assert gates_equal(converted.get_gate_at(i), expected)


param_gate_mapping: Mapping[
    Callable[[int,float],QuantumGate],Callable[[int,float],_backend.Gate]
] = {
    gates.ParametricRX: _backend.gate.ParamRX,
    gates.ParametricRY: _backend.gate.ParamRY,
    gates.ParametricRZ: _backend.gate.ParamRZ,
    gates.ParametricPauliRotation: _backend.gate.ParamPauliRotation,
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


    converted, param_mapper = convert_parametric_circuit(circuit)
    print("param_mapper ",param_mapper)
    print("converted: ", converted)
    print("set",converted.key_set())
    print(converted.get_gate_at(1))
    print(converted.get_gate_at(3))
    print(converted.get_gate_at(5))

    assert converted.n_qubits() == 3

    expected_gates = [
        _backend.gate.X(0),
        _backend.gate.ParamRX(0),
        _backend.gate.H(2),
        _backend.gate.ParamRY(1),
        _backend.gate.CX(0, 2),
        _backend.gate.ParamRZ(2),
        _backend.gate.RX(0, 0.125),
        _backend.gate.ParamPauliRotation(
            _backend.PauliOperator([0, 1, 2], [1, 2, 3]),
            0,
        ),
    ]

    assert converted.n_gates() == len(expected_gates)

    for i, expected in enumerate(expected_gates):
        if isinstance(expected, _backend.ParamGate):
            tmp = converted.get_gate_at(i)
            assert param_gates_equal(tmp[0], expected)
        else:
            assert gates_equal(converted.get_gate_at(i), expected)


