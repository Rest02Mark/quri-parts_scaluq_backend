from collections.abc import Mapping, Sequence
from typing import Callable, Union, cast

import os
import importlib
from typing import Any

import numpy as np
from numpy.typing import ArrayLike
from typing_extensions import assert_never

from quri_parts.circuit import (
    ImmutableLinearMappedParametricQuantumCircuit,
    ImmutableParametricQuantumCircuit,
    ImmutableQuantumCircuit,
    ParametricQuantumCircuitProtocol,
    QuantumGate,
    ParametricQuantumGate,
    gate_names,
)

from quri_parts.rust.circuit.noise import NoiseModel

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

from .. import cast_to_list


# 1. 環境変数 'SCALUQ_PRECISION' を読み取る
#    設定されていなければ、デフォルトで 'f64' (倍精度) を使用する
_precision = os.environ.get('SCALUQ_PRECISION', 'f64').lower()

# 不正な値が指定された場合はエラーを出す
if _precision not in ['f32', 'f64']:
    raise ImportError(
        f"環境変数 SCALUQ_PRECISION に不正な値 '{_precision}' が指定されました。"
        " 'f32' または 'f64' を選択してください。"
    )

# 2. `importlib` を使ってモジュールを動的にインポートする
_module_name = f"scaluq.default.{_precision}"
try:
    # インポートしたモジュールを、このスコープ内でのみ有効な変数 `_backend` に格納する
    _backend: Any = importlib.import_module(_module_name)
    # 動作確認のために、どちらが使われているか表示する（任意）
    print(f"[Info] Library 'a' is using backend: {_module_name}")
except ImportError as e:
    raise ImportError(f"指定されたscaluqバックエンド '{_module_name}' のインポートに失敗しました。") from e



def scaluq_circuit_helper_function():
    print("helper function from scaluq/circuit")

_single_qubit_gate_scaluq: Mapping[
    SingleQubitGateNameType, Callable[[int], _backend.Gate]
] = {
    gate_names.Identity: _backend.gate.I,
    gate_names.X: _backend.gate.X,
    gate_names.Y: _backend.gate.Y,
    gate_names.Z: _backend.gate.Z,
    gate_names.H: _backend.gate.H,
    gate_names.S: _backend.gate.S,
    gate_names.Sdag: _backend.gate.Sdag,
    gate_names.SqrtX: _backend.gate.SqrtX,
    gate_names.SqrtXdag: _backend.gate.SqrtXdag,
    gate_names.SqrtY: _backend.gate.SqrtY,
    gate_names.SqrtYdag: _backend.gate.SqrtYdag,
    gate_names.T: _backend.gate.T,
    gate_names.Tdag: _backend.gate.Tdag,
}


#TODO 
#contorolsいらないはず、確認
def _u1_gate_scaluq(gate: QuantumGate) -> _backend.Gate:
    return cast(
        _backend.Gate,
        _backend.gate.U1(*gate.target_indices, *gate.params),
    )


def _u2_gate_scaluq(gate: QuantumGate) -> _backend.Gate:
    return cast(
        _backend.Gate,
        _backend.gate.U2(*gate.target_indices, *gate.params),
    )

def _u3_gate_scaluq(gate: QuantumGate) -> _backend.Gate:
    return cast(
        _backend.Gate,
        _backend.gate.U3(*gate.target_indices, *gate.params),
    )



_single_qubit_reverse_rotation_gate_scaluq: Mapping[
    SingleQubitGateNameType, Callable[[int, float], _backend.Gate]
] = {
    gate_names.RX: _backend.gate.RX,
    gate_names.RY: _backend.gate.RY,
    gate_names.RZ: _backend.gate.RZ,
}



_two_qubit_gate_scaluq: Mapping[
    TwoQubitGateNameType, Callable[[int, int], _backend.Gate]
] = {
    gate_names.CNOT: _backend.gate.CX,
    gate_names.CZ: _backend.gate.CZ,
    gate_names.SWAP: _backend.gate.Swap,
}



_three_qubit_gate_scaluq: Mapping[
    ThreeQubitGateNameType, Callable[[int, int, int], _backend.Gate]
] = {
    gate_names.TOFFOLI: _backend.gate.Toffoli,
}


_multi_pauli_gate_scaluq: Mapping[
    #MultiQubitGateNameType, Callable[[list[int], list[int]], _backend.Gate]
    MultiQubitGateNameType, Callable[[_backend.PauliOperator], _backend.Gate]
] = {
    gate_names.Pauli: _backend.gate.Pauli,
}


_multi_pauli_rotation_gate_scaluq: Mapping[
    MultiQubitGateNameType, Callable[[_backend.PauliOperator, float], _backend.Gate]
] = {
    gate_names.PauliRotation: _backend.gate.PauliRotation,
}


_single_param_gate_scaluq: Mapping[
    ParametricGateNameType, Callable[[int,float], _backend.Gate]
] = {
    gate_names.ParametricRX: _backend.gate.ParamRX,
    gate_names.ParametricRY: _backend.gate.ParamRY,
    gate_names.ParametricRZ: _backend.gate.ParamRZ,
}


def dense_matrix_gate_scaluq(
        targets: Union[int, Sequence[int]], unitary_matrix: ArrayLike
) -> _backend.Gate:
    if isinstance(targets, int):
        targets = [targets]
    unitary_matrix = np.array(unitary_matrix, dtype=np.complex64)
    return _backend.gate.DenseMatrix(targets,unitary_matrix)


def convert_gate(
        gate: QuantumGate,
) -> _backend.Gate:
    #print("in convert_gate and gate.name is ", gate.name)
    if not is_gate_name(gate.name):
        raise ValueError(f"Unknown gate name: {gate.name}")
    
    if is_single_qubit_gate_name(gate.name):
        if gate.name in _single_qubit_gate_scaluq:
            return _single_qubit_gate_scaluq[gate.name](
                *gate.target_indices, *gate.params
            )
        elif gate.name == gate_names.U1:
            return _u1_gate_scaluq(gate)
        elif gate.name == gate_names.U2:
            return _u2_gate_scaluq(gate)
        elif gate.name == gate_names.U3:
            return _u3_gate_scaluq(gate)
        elif gate.name in _single_qubit_reverse_rotation_gate_scaluq:
            return _single_qubit_reverse_rotation_gate_scaluq[gate.name](
                *gate.target_indices, *gate.params
            )
        else:
            assert False, "Unreachable"
    elif is_two_qubit_gate_name(gate.name):
        return _two_qubit_gate_scaluq[gate.name](
            *gate.control_indices, *gate.target_indices
        )
    elif is_three_qubit_gate_name(gate.name):
        return _three_qubit_gate_scaluq[gate.name](
            *gate.control_indices,*gate.target_indices
        )
    elif is_multi_qubit_gate_name(gate.name):
        target_indices = cast_to_list(gate.target_indices)
        pauli_ids = cast_to_list(gate.pauli_ids)
        if gate.name in _multi_pauli_gate_scaluq:
            pauli = _backend.PauliOperator(target_indices, pauli_ids)
            return _multi_pauli_gate_scaluq[gate.name](pauli)
        elif gate.name in _multi_pauli_rotation_gate_scaluq:
            #print(gate.params)
            #memo
            #angle: float
            #controls sequence[int]
            #pauli:PauliOperato
            pauli = _backend.PauliOperator(target_indices, pauli_ids)
            angle = gate.params[0]
            #print("angle: ", angle)
            return _multi_pauli_rotation_gate_scaluq[gate.name](
                pauli, angle
            )
    elif is_unitary_matrix_gate_name(gate.name):
        return dense_matrix_gate_scaluq(gate.target_indices, gate.unitary_matrix)
    #TODO
    elif is_parametric_gate_name(gate.name):
        raise ValueError("Parametric gates are not supported")
    else:
        assert False, "Unreachable"

def convert_parametric_gate(
        gate: ParametricQuantumGate,
) -> _backend.Gate:
    
    if gate.name not in _single_param_gate_scaluq:
        raise ValueError(f"Unknown parametric gate name: {gate.name}")
    
    if gate.name != gate_names.ParametricPauliRotation:
        return _single_param_gate_scaluq[gate.name](
            *gate.target_indices,1.0
        )
    
    elif gate.name == gate_names.ParametricPauliRotation:
        target_indices = cast_to_list(gate.target_indices)
        pauli_ids = cast_to_list(gate.pauli_ids)
        pauli = _backend.PauliOperator(target_indices, pauli_ids)
        return _backend.gate.ParamPauliRotation(
            pauli
        )
    assert False, "Unreachable"


def convert_circuit(
        circuit: ImmutableQuantumCircuit
        ) -> _backend.Circuit:
    scaluq_circuit = _backend.Circuit(circuit.qubit_count)

    for gate in circuit.gates:
        #print(convert_gate(gate))
        scaluq_circuit.add_gate(convert_gate(gate))
        
    return scaluq_circuit

#TODO param?
def convert_parametric_circuit(
        circuit : ParametricQuantumCircuitProtocol,
) -> tuple[
    _backend.Circuit,Callable[[Sequence[float]],Sequence[float]]
]:
    param_circuit : ImmutableParametricQuantumCircuit
    param_mapper : Callable[[Sequence[float]],Sequence[float]]
    if isinstance(circuit, ImmutableLinearMappedParametricQuantumCircuit):
        param_mapping = circuit.param_mapping
        param_circuit = circuit.primitive_circuit()
        orig_param_mapper = param_mapping.seq_mapper

        def param_mapper(s: Sequence[float]) -> Sequence[float]:
            return tuple(p for p in orig_param_mapper(s))
        
    elif isinstance(circuit, ImmutableParametricQuantumCircuit):
        param_circuit = circuit

        def param_mapper(s: Sequence[float]) -> Sequence[float]:
            return tuple(p for p in s)
        
    else:
        raise ValueError(f"Unsupported parametric circuit type: {type(circuit)}")
    
    
    scaluq_circuit = _backend.Circuit(circuit.qubit_count)
    #TODO rotatetion　ゲートと扱い同じで良いのか？
    param_count = 0
    for gate, _ in param_circuit._gates:

        if is_parametric_gate_name(gate.name):
            #print("param_count: ", param_count)
            if gate.name == gate_names.ParametricRX:
                #TODO arg 1?
                scaluq_circuit.add_param_gate(
                    _backend.gate.ParamRX(*gate.target_indices),str(param_count)
                )#arg1 paramgate , arg2 str
            elif gate.name == gate_names.ParametricRY:
                scaluq_circuit.add_param_gate(
                    _backend.gate.ParamRY(*gate.target_indices),str(param_count)
                )
            elif gate.name == gate_names.ParametricRZ:
                scaluq_circuit.add_param_gate(
                    _backend.gate.ParamRZ(*gate.target_indices),str(param_count)
                )
            #TODO　仕様確認 テストまだ
            elif gate.name == gate_names.ParametricPauliRotation:
                target_indices = cast_to_list(gate.target_indices)
                pauli_ids = cast_to_list(gate.pauli_ids)
                scaluq_circuit.add_param_gate(
                    _backend.gate.ParamPauliRotation(
                        _backend.PauliOperator(target_indices, pauli_ids)
                    ),str(param_count)
                )
            else:
                assert_never(gate.name)

            param_count += 1

        #パラメトリックゲート以外
        else:
            scaluq_circuit.add_gate(convert_gate(gate))

    return scaluq_circuit, param_mapper
    

#TODO delete
def kakunin(circuit: ImmutableQuantumCircuit) -> None:
    print("qubit: ",circuit.qubit_count)
    print("gate: ",circuit.gates)
    print("depth: ",circuit.depth)
    print("control bit", circuit.cbit_count)

