contract Bank {
    uint public balance;

    function deposit() public payable {
        balance += msg.value;
    }

    function withdraw(uint amount) public {
        require(balance >= amount);
        balance -= amount;
        payable(msg.sender).transfer(amount);
    }

    // 👇 ECHIDNA PROPERTY
    function echidna_balance_never_negative() public view returns (bool) {
        return balance >= 0;
    }
}
