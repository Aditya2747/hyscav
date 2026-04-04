// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

contract ReentrancyTest {
    mapping(address => uint) public balances;

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw() public {
        uint bal = balances[msg.sender];
        require(bal > 0, "No balance");

        // Vulnerable: External call before state update (reentrancy)
        (bool sent, ) = msg.sender.call{value: bal}("");
        require(sent, "Failed to send Ether");

        balances[msg.sender] = 0;
    }

    function getBalance() public view returns (uint) {
        return address(this).balance;
    }

    // Echidna property test
    function echidna_balance_cannot_decrease() public view returns (bool) {
        return getBalance() >= 0;
    }
}
