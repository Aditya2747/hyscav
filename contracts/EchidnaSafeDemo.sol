// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title EchidnaSafeDemo
 * @notice SECURE version where all Echidna properties PASS.
 * 
 * Run Echidna on this contract:
 *   python analyzers/echidna_runner_docker.py contracts/EchidnaSafeDemo.sol
 * 
 * Expected: All properties PASS (no violations found).
 */
contract EchidnaSafeDemo {
    uint256 public threshold = 100;
    uint256 public value = 50;
    address public owner;
    bool public enabled;

    constructor() {
        owner = msg.sender;
        enabled = true;
    }

    /// @notice SAFE: has bounds check — value can never exceed threshold
    function increaseValue(uint256 amount) public {
        require(value + amount <= threshold, "Would exceed threshold");
        value += amount;
    }

    /// @notice SAFE: only owner can disable
    function disable() public {
        require(msg.sender == owner, "Not owner");
        enabled = false;
    }

    /// @notice SAFE: only owner can change owner
    function transferOwner(address newOwner) public {
        require(msg.sender == owner, "Not owner");
        require(newOwner != address(0), "Invalid address");
        owner = newOwner;
    }

    /// @notice Echidna property: value must stay <= threshold
    /// WILL PASS because increaseValue has bounds check
    function echidna_value_bounded() public view returns (bool) {
        return value <= threshold;
    }

    /// @notice Echidna property: owner must never be zero address
    /// WILL PASS because transferOwner prevents zero address
    function echidna_owner_nonzero() public view returns (bool) {
        return owner != address(0);
    }

    /// @notice Echidna property: threshold is always positive
    /// WILL PASS because no function modifies threshold
    function echidna_threshold_positive() public view returns (bool) {
        return threshold > 0;
    }
}
