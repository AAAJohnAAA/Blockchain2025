const { docopt } = require("docopt");
const { mimc2 } = require("./mimc.js");
const { SparseMerkleTree } = require("./sparse_merkle_tree.js");
const fs = require("fs");
const doc = `Usage:
  compute_spend_inputs.js [options] <depth> <transcript> <nullifier>
  compute_spend_inputs.js -h | --help

Options:
  -o <file>     name of the created witness file [default: input.json]
  -h --help     Print this message

Arguments:
   <depth>       The number of non-root layers in the merkle tree.
   <transcript>  The file containing transcript of all coins.
                 A file with a line for each coin.
                 Each coin is either a single number (the coin
                 itself) or it can be two space-separated number, which are, in
                 order, the nullifier and the nonce for the coin.

                 Example:

                     1839475893
                     1984375234 2983475298
                     3489725451 9834572345
                     3452345234

   <nullifier>   The nullifier to print a witness of validity for.
                 Must be present in the transcript.
`

/*
 * Computes inputs to the Spend circuit.
 *
 * Inputs:
 *   depth: the depth of the merkle tree being used.
 *   transcript: A list of all coins added to the tree.
 *               Each item is an array.
 *               If the array hash one element, then that element is the coin.
 *               Otherwise the array will have two elements, which are, in order:
 *                 the nullifier and
 *                 the nonce
 *               This list will contain **no** duplicate nullifiers or coins.
 *   nullifier: The nullifier to print inputs to validity verifier for.
 *              This nullifier will be one of the nullifiers in the transcript.
 *
 * Return:
 *   an object of the form:
 * {
 *   "digest"            : ...,
 *   "nullifier"         : ...,
 *   "nonce"             : ...,
 *   "sibling[0]"        : ...,
 *   "sibling[1]"        : ...,
 *      ...
 *   "sibling[depth-1]"  : ...,
 *   "direction[0]"      : ...,
 *   "direction[1]"      : ...,
 *      ...
 *   "direction[depth-1]": ...,
 * }
 * where each ... is a string-represented field element (number)
 * notes about each:
 *   "digest": the digest for the whole tree after the transcript is
 *                  applied.
 *   "nullifier": the nullifier for the coin being spent.
 *   "nonce": the nonce for that coin
 *   "sibling[i]": the sibling of the node on the path to this coin
 *                 at the i'th level from the bottom.
 *   "direction[i]": "0" or "1" indicating whether that sibling is on the left.
 *       The "sibling" hashes correspond directly to the siblings in the
 *       SparseMerkleTree path.
 *       The "direction" keys the boolean directions from the SparseMerkleTree
 *       path, casted to string-represented integers ("0" or "1").
 */
function computeInput(depth, transcript, nullifier) {
    // 1. 初始化稀疏Merkle树和核心变量
    const merkleTree = new SparseMerkleTree(depth);
    let targetNonce = null;
    let targetCommitment = null;

    // 2. 遍历交易转录列表，处理每个硬币并插入Merkle树
    for (const coinItem of transcript) {
        let currentCommitment;

        // 处理两种硬币格式：单元素（直接是硬币）、双元素（nullifier+nonce，需计算哈希）
        if (coinItem.length === 1) {
            currentCommitment = BigInt(coinItem[0]).toString(); // 转为大数字符串，避免精度丢失
        } else if (coinItem.length === 2) {
            const [currNullif, currNonce] = coinItem;
            // 计算MIMC2哈希作为硬币承诺
            currentCommitment = mimc2(BigInt(currNullif), BigInt(currNonce)).toString();
            
            // 匹配目标nullifier，记录对应的nonce和承诺
            if (currNullif === nullifier) {
                targetNonce = currNonce;
                targetCommitment = currentCommitment;
            }
        } else {
            throw new Error(`无效的硬币格式：${coinItem.join(" ")}，仅支持1个或2个元素`);
        }

        // 将当前承诺插入Merkle树
        merkleTree.insert(BigInt(currentCommitment));
    }

    // 3. 校验目标nullifier是否找到
    if (!targetCommitment || !targetNonce) {
        throw new Error(`在转录文件中未找到目标nullifier：${nullifier}`);
    }

    // 4. 获取目标承诺在Merkle树中的路径（兄弟节点+方向）
    const merklePath = merkleTree.path(BigInt(targetCommitment));

    // 5. 构造电路输入结果对象
    const spendInput = {
        "digest": merkleTree.digest.toString(),
        "nullifier": nullifier,
        "nonce": targetNonce
    };

    // 6. 补充sibling和direction数组（适配电路输入格式）
    for (let i = 0; i < depth; i++) {
        const [siblingNode, isLeftSibling] = merklePath[i];
        spendInput[`sibling[${i}]`] = siblingNode.toString();
        spendInput[`direction[${i}]`] = isLeftSibling ? "1" : "0"; // 布尔值转字符串数字
    }

    return spendInput;
}

module.exports = { computeInput };

// If we're not being imported
if (!module.parent) {
    const args = docopt(doc);
    const transcript =
        fs.readFileSync(args['<transcript>'], { encoding: 'utf8' } )
        .split(/\r?\n/)
        .filter(l => l.length > 0)
        .map(l => l.split(/\s+/));
    const depth = parseInt(args['<depth>']);
    const nullifier = args['<nullifier>'];
    const input = computeInput(depth, transcript, nullifier);
    fs.writeFileSync(args['-o'], JSON.stringify(input) + "\n");
}