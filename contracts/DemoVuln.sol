// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DemoVuln {
    mapping (address => uint) public balances;

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw(uint _amount) public {
        require(balances[msg.sender] >= _amount);
        (bool success, ) = msg.sender.call{value:_amount}('');
        require(success, 'transfer failed');
        balances[msg.sender] -= _amount;
    }

    // Echidna property: balance always less than some value? Fails on deposit
    function echidna_balance_bound() public view returns (bool) {
        return balances[msg.sender] <= 0;
    }

    function echidna_no_empty_balance() public view returns (bool) {
        return balances[msg.sender] > 0;
    }
}
