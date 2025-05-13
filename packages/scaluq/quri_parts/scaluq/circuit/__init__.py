from collections.abc import Mapping, Sequence
from typing import Callable, Union, cast

import scaluq
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

def scaluq_circuit_helper_function():
    print("helper function from scaluq/circuit")

_single_qubit_gate_scaluq_f32: Mapping[
    SingleQubitGateNameType, Callable[[int], scaluq.f32.Gate]
] = {
    gate_names.Identity: scaluq.f32.gate.I,
    gate_names.X: scaluq.f32.gate.X,
    gate_names.Y: scaluq.f32.gate.Y,
    gate_names.Z: scaluq.f32.gate.Z,
    gate_names.H: scaluq.f32.gate.H,
    gate_names.S: scaluq.f32.gate.S,
    gate_names.Sdag: scaluq.f32.gate.Sdag,
    gate_names.SqrtX: scaluq.f32.gate.SqrtX,
    gate_names.SqrtXdag: scaluq.f32.gate.SqrtXdag,
    gate_names.SqrtY: scaluq.f32.gate.SqrtY,
    gate_names.SqrtYdag: scaluq.f32.gate.SqrtYdag,
    gate_names.T: scaluq.f32.gate.T,
    gate_names.Tdag: scaluq.f32.gate.Tdag,
}

_single_qubit_gate_scaluq_f64: Mapping[
    SingleQubitGateNameType, Callable[[int], scaluq.f64.Gate]
] = {
    gate_names.Identity: scaluq.f64.gate.I,
    gate_names.X: scaluq.f64.gate.X,
    gate_names.Y: scaluq.f64.gate.Y,
    gate_names.Z: scaluq.f64.gate.Z,
    gate_names.H: scaluq.f64.gate.H,
    gate_names.S: scaluq.f64.gate.S,
    gate_names.Sdag: scaluq.f64.gate.Sdag,
    gate_names.SqrtX: scaluq.f64.gate.SqrtX,
    gate_names.SqrtXdag: scaluq.f64.gate.SqrtXdag,
    gate_names.SqrtY: scaluq.f64.gate.SqrtY,
    gate_names.SqrtYdag: scaluq.f64.gate.SqrtYdag,
    gate_names.T: scaluq.f64.gate.T,
    gate_names.Tdag: scaluq.f64.gate.Tdag,
}



#TODO 
#contorolsいらないはず、確認
def _u1_gate_scaluq_f32(gate: QuantumGate) -> scaluq.f32.Gate:
    return cast(
        scaluq.f32.Gate,
        scaluq.f32.gate.U1(*gate.target_indices, *gate.params),
    )

def _u1_gate_scaluq_f64(gate: QuantumGate) -> scaluq.f64.Gate:
    return cast(
        scaluq.f64.Gate,
        scaluq.f64.gate.U1(*gate.target_indices, *gate.params),
    )

def _u2_gate_scaluq_f32(gate: QuantumGate) -> scaluq.f32.Gate:
    return cast(
        scaluq.f32.Gate,
        scaluq.f32.gate.U2(*gate.target_indices, *gate.params),
    )

def _u2_gate_scaluq_f64(gate: QuantumGate) -> scaluq.f64.Gate:
    return cast(
        scaluq.f64.Gate,
        scaluq.f64.gate.U2(*gate.target_indices, *gate.params),
    )

def _u3_gate_scaluq_f32(gate: QuantumGate) -> scaluq.f32.Gate:
    return cast(
        scaluq.f32.Gate,
        scaluq.f32.gate.U3(*gate.target_indices, *gate.params),
    )

def _u3_gate_scaluq_f64(gate: QuantumGate) -> scaluq.f64.Gate:
    return cast(
        scaluq.f64.Gate,
        scaluq.f64.gate.U3(*gate.target_indices, *gate.params),
    )


_single_qubit_reverse_rotation_gate_scaluq_f32: Mapping[
    SingleQubitGateNameType, Callable[[int, float], scaluq.f32.Gate]
] = {
    gate_names.RX: scaluq.f32.gate.RX,
    gate_names.RY: scaluq.f32.gate.RY,
    gate_names.RZ: scaluq.f32.gate.RZ,
}

_single_qubit_reverse_rotation_gate_scaluq_f64: Mapping[
    SingleQubitGateNameType, Callable[[int, float], scaluq.f64.Gate]
] = {
    gate_names.RX: scaluq.f64.gate.RX,
    gate_names.RY: scaluq.f64.gate.RY,
    gate_names.RZ: scaluq.f64.gate.RZ,
}

_two_qubit_gate_scaluq_f32: Mapping[
    TwoQubitGateNameType, Callable[[int, int], scaluq.f32.Gate]
] = {
    gate_names.CNOT: scaluq.f32.gate.CX,
    gate_names.CZ: scaluq.f32.gate.CZ,
    gate_names.SWAP: scaluq.f32.gate.Swap,
}

_two_qubit_gate_scaluq_f64: Mapping[
    TwoQubitGateNameType, Callable[[int, int], scaluq.f64.Gate]
] = {
    gate_names.CNOT: scaluq.f64.gate.CX,
    gate_names.CZ: scaluq.f64.gate.CZ,
    gate_names.SWAP: scaluq.f64.gate.Swap,
}

_three_qubit_gate_scaluq_f32: Mapping[
    ThreeQubitGateNameType, Callable[[int, int, int], scaluq.f32.Gate]
] = {
    gate_names.TOFFOLI: scaluq.f32.gate.Toffoli,
}

_three_qubit_gate_scaluq_f64: Mapping[
    ThreeQubitGateNameType, Callable[[int, int, int], scaluq.f64.Gate]
] = {
    gate_names.TOFFOLI: scaluq.f64.gate.Toffoli,
}

_multi_pauli_gate_scaluq_f32: Mapping[
    #MultiQubitGateNameType, Callable[[list[int], list[int]], scaluq.f32.Gate]
    MultiQubitGateNameType, Callable[[scaluq.f32.PauliOperator], scaluq.f32.Gate]
] = {
    gate_names.Pauli: scaluq.f32.gate.Pauli,
}

_multi_pauli_gate_scaluq_f64: Mapping[
    #MultiQubitGateNameType, Callable[[list[int], list[int]], scaluq.f64.Gate]
    MultiQubitGateNameType, Callable[[scaluq.f64.PauliOperator], scaluq.f64.Gate]
] = {
    gate_names.Pauli: scaluq.f64.gate.Pauli,
}

_multi_pauli_rotation_gate_scaluq_f32: Mapping[
    MultiQubitGateNameType, Callable[[scaluq.f32.PauliOperator, float], scaluq.f32.Gate]
] = {
    gate_names.PauliRotation: scaluq.f32.gate.PauliRotation,
}

_multi_pauli_rotation_gate_scaluq_f64: Mapping[
    MultiQubitGateNameType, Callable[[list[int], list[int], float], scaluq.f64.Gate]
] = {
    gate_names.PauliRotation: scaluq.f64.gate.PauliRotation,
}

_single_param_gate_scaluq_f32: Mapping[
    ParametricGateNameType, Callable[[int,float], scaluq.f32.Gate]
] = {
    gate_names.ParametricRX: scaluq.f32.gate.ParamRX,
    gate_names.ParametricRY: scaluq.f32.gate.ParamRY,
    gate_names.ParametricRZ: scaluq.f32.gate.ParamRZ,
}


def dense_matrix_gate_scaluq_f32(
        targets: Union[int, Sequence[int]], unitary_matrix: ArrayLike
) -> scaluq.f32.Gate:
    if isinstance(targets, int):
        targets = [targets]
    unitary_matrix = np.array(unitary_matrix, dtype=np.complex64)
    return scaluq.f32.gate.DenseMatrix(targets,unitary_matrix)


def convert_gate_f32(
        gate: QuantumGate,
) -> scaluq.f32.Gate:
    print("in convert_gate_f32 and gate.name is ", gate.name)
    if not is_gate_name(gate.name):
        raise ValueError(f"Unknown gate name: {gate.name}")
    
    if is_single_qubit_gate_name(gate.name):
        if gate.name in _single_qubit_gate_scaluq_f32:
            return _single_qubit_gate_scaluq_f32[gate.name](
                *gate.target_indices, *gate.params
            )
        elif gate.name == gate_names.U1:
            return _u1_gate_scaluq_f32(gate)
        elif gate.name == gate_names.U2:
            return _u2_gate_scaluq_f32(gate)
        elif gate.name == gate_names.U3:
            return _u3_gate_scaluq_f32(gate)
        elif gate.name in _single_qubit_reverse_rotation_gate_scaluq_f32:
            return _single_qubit_reverse_rotation_gate_scaluq_f32[gate.name](
                *gate.target_indices, *gate.params
            )
        else:
            assert False, "Unreachable"
    elif is_two_qubit_gate_name(gate.name):
        return _two_qubit_gate_scaluq_f32[gate.name](
            *gate.control_indices, *gate.target_indices
        )
    elif is_three_qubit_gate_name(gate.name):
        return _three_qubit_gate_scaluq_f32[gate.name](
            *gate.control_indices,*gate.target_indices
        )
    elif is_multi_qubit_gate_name(gate.name):
        target_indices = cast_to_list(gate.target_indices)
        pauli_ids = cast_to_list(gate.pauli_ids)
        if gate.name in _multi_pauli_gate_scaluq_f32:
            pauli = scaluq.f32.PauliOperator(target_indices, pauli_ids)
            return _multi_pauli_gate_scaluq_f32[gate.name](pauli)
        elif gate.name in _multi_pauli_rotation_gate_scaluq_f32:
            #print(gate.params)
            #memo
            #angle: float
            #controls sequence[int]
            #pauli:PauliOperato
            pauli = scaluq.f32.PauliOperator(target_indices, pauli_ids)
            angle = gate.params[0]
            #print("angle: ", angle)
            return _multi_pauli_rotation_gate_scaluq_f32[gate.name](
                pauli, angle
            )
    elif is_unitary_matrix_gate_name(gate.name):
        return dense_matrix_gate_scaluq_f32(gate.target_indices, gate.unitary_matrix)
    #TODO
    elif is_parametric_gate_name(gate.name):
        raise ValueError("Parametric gates are not supported")
    else:
        assert False, "Unreachable"

def convert_parametric_gate_f32(
        gate: ParametricQuantumGate,
) -> scaluq.f32.Gate:
    
    if gate.name not in _single_param_gate_scaluq_f32:
        raise ValueError(f"Unknown parametric gate name: {gate.name}")
    
    if gate.name != gate_names.ParametricPauliRotation:
        return _single_param_gate_scaluq_f32[gate.name](
            *gate.target_indices,1.0
        )
    
    elif gate.name == gate_names.ParametricPauliRotation:
        target_indices = cast_to_list(gate.target_indices)
        pauli_ids = cast_to_list(gate.pauli_ids)
        pauli = scaluq.f32.PauliOperator(target_indices, pauli_ids)
        return scaluq.f32.gate.ParamPauliRotation(
            pauli
        )
    assert False, "Unreachable"
    

    



def convert_circuit_f32(
        circuit: ImmutableQuantumCircuit
        ) -> scaluq.f32.Circuit:
    scaluq_f32_circuit = scaluq.f32.Circuit(circuit.qubit_count)

    for gate in circuit.gates:
        #print(convert_gate_f32(gate))
        scaluq_f32_circuit.add_gate(convert_gate_f32(gate))

    print("convert end f32.")
        
    return scaluq_f32_circuit

#TODO
def convert_parametric_circuit_f32(
        circuit : ParametricQuantumCircuitProtocol,
) -> tuple[
    scaluq.f32.Circuit,Callable[[Sequence[float]],Sequence[float]]
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
    
    scaluq_f32_circuit = scaluq.f32.Circuit(circuit.qubit_count)
    #TODO rotatetion　ゲートと扱い同じで良いのか？
    param_count = 0
    for gate, _ in param_circuit._gates:

        if is_parametric_gate_name(gate.name):
            print("param_count: ", param_count)
            if gate.name == gate_names.ParametricRX:
                #TODO arg 1?
                scaluq_f32_circuit.add_param_gate(
                    scaluq.f32.gate.ParamRX(*gate.target_indices),str(param_count)
                )#arg1 paramgate , arg2 str
            elif gate.name == gate_names.ParametricRY:
                scaluq_f32_circuit.add_param_gate(
                    scaluq.f32.gate.ParamRY(*gate.target_indices),str(param_count)
                )
            elif gate.name == gate_names.ParametricRZ:
                scaluq_f32_circuit.add_param_gate(
                    scaluq.f32.gate.ParamRZ(*gate.target_indices),str(param_count)
                )
            #TODO　仕様確認 テストまだ
            elif gate.name == gate_names.ParametricPauliRotation:
                target_indices = cast_to_list(gate.target_indices)
                pauli_ids = cast_to_list(gate.pauli_ids)
                scaluq_f32_circuit.add_param_gate(
                    scaluq.f32.gate.ParamPauliRotation(
                        scaluq.f32.PauliOperator(target_indices, pauli_ids)
                    ),str(param_count)
                )
            else:
                assert_never(gate.name)

            param_count += 1

        #パラメトリックゲート以外
        else:
            scaluq_f32_circuit.add_gate(convert_gate_f32(gate))

    return scaluq_f32_circuit, param_mapper
    


def kakunin(circuit: ImmutableQuantumCircuit) -> None:
    print("qubit: ",circuit.qubit_count)
    print("gate: ",circuit.gates)
    print("depth: ",circuit.depth)
    print("cbit", circuit.cbit_count)



#TODO
#__all__ = []
        
