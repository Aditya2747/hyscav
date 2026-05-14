// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

contract Vault {
    mapping(address => uint256) public balances;
    uint256 public totalDeposits;

    function deposit() external payable {
        balances[msg.sender] += msg.value;
        totalDeposits += msg.value;
    }

    function withdraw(uint256 amount) external {
        require(balances[msg.sender] >= amount, "Not enough");

        // ❗ subtle bug: totalDeposits updated AFTER external interaction
        (bool sent, ) = msg.sender.call{value: amount}("");
        require(sent, "Failed");

        balances[msg.sender] -= amount;
        totalDeposits -= amount;
    }

    // Invariant that should ALWAYS hold:
    // sum(balances) == totalDeposits
}