// =============================================================================
//                                  Config 
// =============================================================================

// sets up web3.js
if (typeof web3 !== 'undefined')  {
    web3 = new Web3(web3.currentProvider);
} else {
    web3 = new Web3(new Web3.providers.HttpProvider("http://localhost:8545"));
}

// Default account is the first one
web3.eth.defaultAccount = web3.eth.accounts[0];
// Constant we use later
var GENESIS = '0x0000000000000000000000000000000000000000000000000000000000000000';

// This is the ABI for your contract
var abi = [
    {
        "constant": false,
        "inputs": [
            { "internalType": "address", "name": "creditor", "type": "address" },
            { "internalType": "uint32", "name": "amount", "type": "uint32" },
            { "internalType": "address[]", "name": "cyclePath", "type": "address[]" },
            { "internalType": "uint32", "name": "cycleMin", "type": "uint32" }
        ],
        "name": "recordDebt",
        "outputs": [],
        "payable": false,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [
            { "internalType": "address", "name": "debtor", "type": "address" },
            { "internalType": "address", "name": "creditor", "type": "address" }
        ],
        "name": "getDebt",
        "outputs": [
            { "internalType": "uint32", "name": "", "type": "uint32" }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    }
];

// ============================================================
abiDecoder.addABI(abi);
var BlockchainSplitwiseContractSpec = web3.eth.contract(abi);
var contractAddress = '0x15b73A34011f1d8FBe53432b392327b695F840bb'; // 修改为你的合约地址
var BlockchainSplitwise = BlockchainSplitwiseContractSpec.at(contractAddress);

// =============================================================================
//                            Functions
// =============================================================================

// Helper to scan call data
function getCallData(extractor_fn, early_stop_fn = null) {
    const results = new Set();
    const all_calls = getAllFunctionCalls(contractAddress, 'recordDebt', early_stop_fn);
    all_calls.forEach(call => {
        extractor_fn(call).forEach(value => results.add(value));
    });
    return Array.from(results);
}

// Get all creditors
function getCreditors() {
    return getCallData(call => [call.args[0]]);
}

// Get creditors for a specific user
function getCreditorsForUser(user) {
    return getCreditors().filter(creditor => BlockchainSplitwise.getDebt(user, creditor).toNumber() > 0);
}

// Find minimum debt on a path
function findMinOnPath(path) {
    return path.slice(1).reduce((minOwed, debtor, i) => {
        const creditor = path[i];
        const amountOwed = BlockchainSplitwise.getDebt(debtor, creditor).toNumber();
        return minOwed == null || minOwed > amountOwed ? amountOwed : minOwed;
    }, null);
}

// Get all users (debtors + creditors)
function getUsers() {
    return getCallData(call => [call.from, call.args[0]]);
}

// Get total owed by user
function getTotalOwed(user) {
    return getCreditors().reduce((total, creditor) =>
        total + BlockchainSplitwise.getDebt(user, creditor).toNumber(), 0);
}

// Get last activity timestamp for a user
function getLastActive(user) {
    const all_timestamps = getCallData(call =>
        (call.from === user || call.args[0] === user) ? [call.timestamp] : []
    );
    return all_timestamps.length ? Math.max(...all_timestamps) : null;
}

// Add an IOU
function add_IOU(creditor, amount) {
    const debtor = web3.eth.defaultAccount;
    const path = doBFS(creditor, debtor, getCreditorsForUser);

    if (path) {
        const min_on_cycle = Math.min(findMinOnPath(path), amount);
        return BlockchainSplitwise.recordDebt(creditor, amount, path, min_on_cycle, { from: debtor });
    }
    return BlockchainSplitwise.recordDebt(creditor, amount, [], 0, { from: debtor });
}

// =============================================================================
// Provided utility functions
// =============================================================================
function getAllFunctionCalls(addressOfContract, functionName, earlyStopFn) {
    var curBlock = web3.eth.blockNumber;
    var function_calls = [];
    while (curBlock !== GENESIS) {
        var b = web3.eth.getBlock(curBlock, true);
        var txns = b.transactions;
        for (var j = 0; j < txns.length; j++) {
            var txn = txns[j];
            if (txn.to === addressOfContract.toLowerCase()) {
                var func_call = abiDecoder.decodeMethod(txn.input);
                if (func_call && func_call.name === functionName) {
                    var args = func_call.params.map(x => x.value);
                    function_calls.push({ from: txn.from, args: args, timestamp: b.timestamp });
                    if (earlyStopFn && earlyStopFn(function_calls[function_calls.length - 1])) {
                        return function_calls;
                    }
                }
            }
        }
        curBlock = b.parentHash;
    }
    return function_calls;
}

function doBFS(start, end, getNeighbors) {
    var queue = [[start]];
    while (queue.length > 0) {
        var cur = queue.shift();
        var lastNode = cur[cur.length - 1];
        if (lastNode === end) {
            return cur;
        } else {
            var neighbors = getNeighbors(lastNode);
            for (var i = 0; i < neighbors.length; i++) {
                queue.push(cur.concat([neighbors[i]]));
            }
        }
    }
    return null;
}

// =============================================================================
// UI
// =============================================================================
$("#total_owed").html("$"+getTotalOwed(web3.eth.defaultAccount));
$("#last_active").html(timeConverter(getLastActive(web3.eth.defaultAccount)));

$("#myaccount").change(function() {
    web3.eth.defaultAccount = $(this).val();
    $("#total_owed").html("$"+getTotalOwed(web3.eth.defaultAccount));
    $("#last_active").html(timeConverter(getLastActive(web3.eth.defaultAccount)))
});

var opts = web3.eth.accounts.map(a => '<option value="'+a+'">'+a+'</option>');
$(".account").html(opts);
$(".wallet_addresses").html(web3.eth.accounts.map(a => '<li>'+a+'</li>'));
$("#all_users").html(getUsers().map((u,i) => "<li>"+u+"</li>"));

// Button click
$("#addiou").click(function() {
    add_IOU($("#creditor").val(), Number($("#amount").val()));
    window.location.reload(false);
});

// Log function
function log(description, obj) {
    $("#log").html($("#log").html() + description + ": " + JSON.stringify(obj, null, 2) + "\n\n");
}
