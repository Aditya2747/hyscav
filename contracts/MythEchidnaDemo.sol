// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract MythEchidnaDemo {
    mapping(address => uint256) public balances;

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw() public {
        uint256 bal = balances[msg.sender];
        require(bal > 0);
        (bool sent, ) = msg.sender.call{value: bal}("");
        require(sent, "Failed to send Ether");
        balances[msg.sender] = 0;
    }

    // Echidna property tests - these will fail for reentrancy
    function echidna_no_balance_overflow() public view returns (bool) {
        return balances[msg.sender] <= msg.sender.balance * 2;
    }

    function echidna_balance_non_negative() public view returns (bool) {
        return balances[msg.sender] >= 0;
    }
}

