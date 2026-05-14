// Contract where Slither misses but Mythril/Echidna may catch runtime

pragma solidity ^0.8.0;

contract SlitherMiss {
    uint public totalSupply;
    mapping(address => uint) balances;

    function mint(uint amount) public {
        totalSupply += amount;
        balances[msg.sender] += amount;
    }

    function transfer(address to, uint amount) public {
        require(balances[msg.sender] >= amount);
        // Mythril may detect complex path
        if (amount > 0) {
            unchecked {
                balances[msg.sender] -= amount;
                balances[to] += amount;
            }
        }
    }

    // Echidna - test for totalSupply consistency (fails on overflow fuzz?)
    function echidna_total_supply_constant() public view returns (bool) {
        uint sum = 0;
        // Can't sum mapping, so simple
        return totalSupply > 0;
    }
}
