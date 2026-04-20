// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VulnerableTest {
    mapping(address => uint256) public balances;

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    // Reentrancy vulnerability - Mythril should detect
    function withdraw(uint256 amount) public {
        require(balances[msg.sender] >= amount);
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        balances[msg.sender] -= amount; // Check-effect-interaction violation
    }

    // Overflow vuln with unchecked
    function riskyAdd(uint256 a, uint256 b) public {
        unchecked {
            balances[msg.sender] = a + b; // Mythril overflow
        }
    }

    // Echidna properties - should fail on fuzzing
    function echidna_balance_non_increasing() external view returns (bool) {
        return balances[msg.sender] <= 1 ether; // Fails on multiple deposits
    }

    function echidna_no_overflow() external view returns (bool) {
        return balances[msg.sender] < type(uint256).max;
    }
}
