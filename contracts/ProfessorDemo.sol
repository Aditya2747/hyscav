// Professor Demo: Triggers Mythril reentrancy, Echidna property fail

pragma solidity ^0.8.0;

contract ProfessorDemo {
    mapping(address => uint) balances;

    event Transfer(address indexed from, address indexed to, uint value);

    function deposit() public payable {
        balances[msg.sender] += msg.value;
        emit Transfer(address(0), msg.sender, msg.value);
    }

    // Mythril reentrancy detection
    function withdrawAll() public {
        uint bal = balances[msg.sender];
        require(bal > 0);
        (bool success, ) = msg.sender.call{value: bal}("");
        require(success);
        balances[msg.sender] = 0;
    }

    // Echidna property - fails after deposit (balance <=0)
    function echidna_balance_zero() public view returns (bool) {
        return balances[msg.sender] == 0;
    }

    // Another fail property
    function echidna_no_balance() public view returns (bool) {
        return balances[msg.sender] == 0;
    }

    receive() external payable {}
}
