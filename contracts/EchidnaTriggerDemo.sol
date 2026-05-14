// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title EchidnaTriggerDemo
 * @notice Contract with 3 vulnerabilities designed to trigger Echidna property failures.
 * 
 * Run Echidna on this contract:
 *   python analyzers/echidna_runner_docker.py contracts/EchidnaTriggerDemo.sol
 * 
 * Expected: 3 property violations found by fuzzing.
 */
contract EchidnaTriggerDemo {
    uint256 public threshold = 100;
    uint256 public value = 50;
    address public owner;
    bool public enabled;

    constructor() {
        owner = msg.sender;
        enabled = true;
    }

    /// @notice VULNERABILITY 1: No bounds check — value can exceed threshold
    function increaseValue(uint256 amount) public {
        value += amount;
    }

    /// @notice VULNERABILITY 2: No access control — anyone can disable the contract
    function disable() public {
        enabled = false;
    }

    /// @notice VULNERABILITY 3: No access control — anyone can zero out owner
    function resetOwner() public {
        owner = address(0);
    }

    /// @notice Echidna property: value must stay <= threshold
    /// WILL FAIL after increaseValue(100) or more
    function echidna_value_bounded() public view returns (bool) {
        return value <= threshold;
    }

    /// @notice Echidna property: contract must stay enabled
    /// WILL FAIL after disable()
    function echidna_always_enabled() public view returns (bool) {
        return enabled;
    }

    /// @notice Echidna property: owner must never be zero address
    /// WILL FAIL after resetOwner()
    function echidna_owner_nonzero() public view returns (bool) {
        return owner != address(0);
    }
}
