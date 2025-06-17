# test

'pytest -v "テストファイルパス" '
-v : 詳細表示
"test_"から始まるファイルを全て実行
-s : 標準出力あり


20250403

paramcircuitの仕様
scaluqでは、circuitとparamcircuitを区別していない

parametric matrix 対応


update_quantum_stateは回路にparam_gateを含む場合、必ず、引数にparamを含めなければならない


pauli周りで結果が-１倍されるかもしれない

importを重複して行っているため、　binding error import 方法を変える