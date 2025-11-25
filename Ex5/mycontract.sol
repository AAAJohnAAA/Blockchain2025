pragma solidity >=0.4.22 <0.6.0;

contract BlockchainDebtManager {
    struct Debt {
        uint32 balance;
    }

    mapping(address => mapping(address => Debt)) internal debts;

    function getDebt(address debtor, address creditor) public view returns (uint32) {
        return debts[debtor][creditor].balance;
    }

    function recordDebt(address creditor, uint32 amount, address[] memory cyclePath, uint32 cycleMin) public {
        address debtor = msg.sender;
        require(debtor != creditor, "Debtor and creditor cannot be the same.");
        require(amount > 0, "Debt amount must be positive.");

        Debt storage currentDebt = debts[debtor][creditor];

        if (cycleMin == 0) {
            currentDebt.balance = safeAdd(currentDebt.balance, amount);
            return;
        }

        require(cycleMin <= currentDebt.balance + amount, "Cycle minimum exceeds allowable debt.");
        require(validateAndAdjustCycle(creditor, debtor, cyclePath, cycleMin), "Invalid cycle path.");

        currentDebt.balance = safeAdd(currentDebt.balance, amount - cycleMin);
    }

    function validateAndAdjustCycle(address start, address end, address[] memory path, uint32 cycleMin) private returns (bool) {
        if (start != path[0] || end != path[path.length - 1]) {
            return false;
        }

        if (path.length > 12) {
            return false;
        }

        for (uint i = 1; i < path.length; i++) {
            Debt storage edgeDebt = debts[path[i - 1]][path[i]];
            if (edgeDebt.balance == 0 || edgeDebt.balance < cycleMin) {
                return false;
            }
            edgeDebt.balance -= cycleMin;
        }
        return true;
    }

    function safeAdd(uint32 a, uint32 b) internal pure returns (uint32) {
        uint32 sum = a + b;
        require(sum >= a, "Addition overflow.");
        return sum;
    }
}
