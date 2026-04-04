// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

contract TxOriginTest {
    mapping(address => uint256) public balances;
    
    // Vulnerable: Uses tx.origin for authorization (phishing attack vector)
    modifier onlyOwner() {
        require(tx.origin == owner, "Not owner via tx.origin");
        _;
    }
    
    address public owner;
    
    constructor() {
        owner = msg.sender;
    }
    
    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }
    
    function transfer(address to, uint256 amount) public onlyOwner {
        require(balances[msg.sender] >= amount);
        balances[msg.sender] -= amount;
        balances[to] += amount;
    }
    
    // Malicious fallback for phishing attack
    fallback() external payable {
        // Attacker contract can re-use victim's tx.origin
    }
    
    function getBalance() public view returns (uint256) {
        return balances[msg.sender];
    }
    
    // Owner can change
    function changeOwner(address newOwner) public onlyOwner {
        owner = newOwner;
    }
    
    // Echidna property
    function echidna_owner_unchanged() public view returns (bool) {
        return owner != address(0);
    }
}
