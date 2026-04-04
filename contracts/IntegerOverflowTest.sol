// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

contract IntegerOverflowTest {
    mapping(address => uint256) public balances;
    uint256 public totalSupply;

    function deposit() public payable {
        balances[msg.sender] += msg.value;
        totalSupply += msg.value;
    }

    // Vulnerable: Integer overflow in calculation (pre-Solidity 0.8 safe math)
    function multiplyReward(uint256 amount) public {
        uint256 reward = amount * 100; // Vulnerable if amount > type(uint256).max / 100
        balances[msg.sender] += reward;
        totalSupply += reward;
    }

    // Vulnerable: Addition overflow
    function addUsers(uint256 numUsers) public {
        totalSupply += numUsers * 1 ether; // Overflow if numUsers large
    }

    function withdraw() public {
        uint256 bal = balances[msg.sender];
        require(bal > 0, "No balance");
        balances[msg.sender] = 0;
        totalSupply -= bal;
        payable(msg.sender).transfer(bal);
    }

    function getBalance() public view returns (uint256) {
        return balances[msg.sender];
    }

    // Echidna property: balance cannot exceed totalSupply
    function echidna_total_supply_positive() public view returns (bool) {
        return totalSupply > 0;
    }

    function echidna_no_overflow() public view returns (bool) {
        return totalSupply <= type(uint256).max / 2;
    }
}
