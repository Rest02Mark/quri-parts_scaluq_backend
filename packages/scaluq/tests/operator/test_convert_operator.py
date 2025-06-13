# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#      http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
from pytest import approx
import importlib
from typing import Any

from quri_parts.core.operator import PAULI_IDENTITY, Operator, SinglePauli, pauli_label

#TODO
# 現在の作業ディレクトリを取得
script_dir = os.getcwd()
script_dir = script_dir.replace("/jikken", "")
target_path =  script_dir + "/packages/scaluq"
sys.path.insert(0, target_path)
#print(sys.path)

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


from quri_parts.scaluq.operator import(
    convert_operator
)


class TestConvertOperator:

    def test_convert_pauli_label(self) ->None:

        pauli = pauli_label("X5 Y9 Z17")
        sq_op = convert_operator(pauli, n_qubits=18)

        assert isinstance(sq_op, _backend.Operator)
        assert len(sq_op.terms()) == 1
        sq_pauli = sq_op.terms()[0]
        converted_paulis = set(
            zip(sq_pauli.pauli_id_list(), sq_pauli.target_qubit_list())
        )
        #print("converted_paulis",converted_paulis)
        assert converted_paulis == {
            (SinglePauli.X, 5),
            (SinglePauli.Y, 9),
            (SinglePauli.Z, 17),
        }
        assert sq_pauli.coef() == 1.0



    def test_convert_pauli_identity(self) -> None:
        #print("PAULI_IDENTITY",PAULI_IDENTITY,3)
        sq_op = convert_operator(PAULI_IDENTITY,n_qubits=3)

        #print("sq_op",sq_op)
        assert isinstance(sq_op, _backend.Operator)
        assert len(sq_op.terms()) == 1
        sq_pauli = sq_op.terms()[0]
        #print(sq_pauli)
        #print(sq_pauli.pauli_id_list)
        #print(sq_pauli.coef)
        assert sq_pauli.pauli_id_list() == []
        assert sq_pauli.coef() == 1


    def test_convert_operator(self) -> None:
        op = Operator(
            {
                pauli_label("X5 Y9 Z17"): 0.1,
                pauli_label("X3 Y8 Y12"): 0.2j,
                pauli_label("Z3 Y4 X10"): 0.3 + 0.4j,
                PAULI_IDENTITY: 0.5,
            }
        )
        sq_op= convert_operator(op, n_qubits=18)

        assert isinstance(sq_op, _backend.Operator)
        assert len(sq_op.terms()) == 4
        terms = [sq_op.terms()[i] for i in range(4)]
        converted_paulis = [
            (set(zip(t.pauli_id_list(), t.target_qubit_list())), t.coef())
            for t in terms
        ]
        assert converted_paulis == [
            ({(SinglePauli.X, 5), (SinglePauli.Y, 9), (SinglePauli.Z, 17)}, approx(0.1)),
            ({(SinglePauli.X, 3), (SinglePauli.Y, 8), (SinglePauli.Y, 12)}, approx(0.2j)),
            ({(SinglePauli.Z, 3), (SinglePauli.Y, 4), (SinglePauli.X, 10)}, approx(0.3 + 0.4j)),
            (set(), 0.5),
        ]

