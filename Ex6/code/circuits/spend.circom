include "./mimc.circom";

/*
 * IfThenElse sets `out` to `true_value` if `condition` is 1 and `out` to
 * `false_value` if `condition` is 0.
 *
 * It enforces that `condition` is 0 or 1.
 *
 */
template IfThenElse() {
    signal input condition;
    signal input true_value;
    signal input false_value;
    signal output out;

    // 辅助信号：构建线性约束，符合hint要求
    signal helper;
    // 约束condition只能是0或1
    condition * (1 - condition) === 0;
    // 线性组合实现条件选择
    helper <== condition * (true_value - false_value);
    out <== false_value + helper;
}

/*
 * SelectiveSwitch takes two data inputs (`in0`, `in1`) and produces two ouputs.
 * If the "select" (`s`) input is 1, then it inverts the order of the inputs
 * in the ouput. If `s` is 0, then it preserves the order.
 *
 * It enforces that `s` is 0 or 1.
 */
template SelectiveSwitch() {
    signal input in0;
    signal input in1;
    signal input s;
    signal output out0;
    signal output out1;

    // 约束s只能是0或1
    s * (1 - s) === 0;
    // 线性约束实现开关逻辑
    signal diff;
    diff <== in1 - in0;
    out0 <== in0 + s * diff;
    out1 <== in1 - s * diff;
}

/*
 * Verifies the presence of H(`nullifier`, `nonce`) in the tree of depth
 * `depth`, summarized by `digest`.
 * This presence is witnessed by a Merle proof provided as
 * the additional inputs `sibling` and `direction`, 
 * which have the following meaning:
 *   sibling[i]: the sibling of the node on the path to this coin
 *               at the i'th level from the bottom.
 *   direction[i]: "0" or "1" indicating whether that sibling is on the left.
 *       The "sibling" hashes correspond directly to the siblings in the
 *       SparseMerkleTree path.
 *       The "direction" keys the boolean directions from the SparseMerkleTree
 *       path, casted to string-represented integers ("0" or "1").
 */
template Spend(depth) {
    signal input digest;
    signal input nullifier;
    signal private input nonce;
    signal private input sibling[depth];
    signal private input direction[depth];

    component computed_hash[depth + 1];
    computed_hash[0] = Mimc2();
    computed_hash[0].in0 <== nullifier;
    computed_hash[0].in1 <== nonce;

    component switches[depth];
    for(var i = 0; i < depth; ++i){
        switches[i] = SelectiveSwitch();
        switches[i].in0 <== computed_hash[i].out;
        switches[i].in1 <== sibling[i];
        switches[i].s <== direction[i];

        computed_hash[i+1] = Mimc2();
        computed_hash[i+1].in0 <== switches[i].out0;
        computed_hash[i+1].in1 <== switches[i].out1;
    }
    computed_hash[depth].out === digest;
}