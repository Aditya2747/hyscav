// Demo for Echidna - trivial property fail

pragma solidity ^0.8.0;

contract EchidnaFailDemo {
    uint public counter = 0;

    function inc() public {
        counter++;
    }

    // Fails immediately
    function echidna_counter_zero() public view returns (bool) {
        return counter == 0;
    }

    // Fails after inc
    function echidna_no_inc() public view returns (bool) {
        return counter == 0;
    }
}
