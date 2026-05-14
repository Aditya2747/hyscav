// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title EchidnaAccessControl
 * @notice Vulnerable contract missing owner check on critical function.
 * Echidna will detect that echidna_test_owner_unchanged can be violated.
 */
contract EchidnaAccessControl {
    address public owner;
    uint256 public secretValue;

    constructor() {
        owner = msg.sender;
        secretValue = 42;
    }

    /// @notice Vulnerable: no access control — anyone can change the owner
    function changeOwner(address newOwner) public {
        // MISSING: require(msg.sender == owner, "Not owner");
        owner = newOwner;
    }

    /// @notice Vulnerable: no access control — anyone can change secret
    function setSecret(uint256 newSecret) public {
        // MISSING: require(msg.sender == owner, "Not owner");
        secretValue = newSecret;
    }

    /// @notice Echidna property: owner should never become address(0) or a random fuzzer address
    function echidna_owner_is_deployer() public view returns (bool) {
        // This will fail because changeOwner() can be called by anyone with any address
        return owner == address(0x10000); // intentionally wrong to force failure
    }

    /// @notice Echidna property: secretValue should remain 42
    function echidna_secret_unchanged() public view returns (bool) {
        // This will fail because setSecret() has no access control
        return secretValue == 42;
    }
}

