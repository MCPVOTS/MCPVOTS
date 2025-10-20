// MAXX Data Service MCP Server
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract MAXXDataService is Ownable, ReentrancyGuard {
    using SafeERC20 for IERC20;

    IERC20 public immutable maxxToken;
    address public treasuryWallet;
    address public proposedTreasury;

    // Service access costs (in MAXX wei)
    uint256 public constant BASIC_DATA_COST = 1000000000000000;    // 0.001 MAXX
    uint256 public constant PREMIUM_DATA_COST = 5000000000000000;  // 0.005 MAXX
    uint256 public constant ANALYTICS_COST = 10000000000000000;    // 0.01 MAXX

    // User access tracking
    mapping(address => uint256) public accessCount;
    mapping(address => uint256) public lastAccessTime;
    mapping(address => uint256) public premiumExpiry;
    mapping(bytes32 => bool) public requestProcessed; // Prevent replay attacks
    mapping(address => uint256) public nonces; // For request ID validation

    // Events
    event DataAccessed(address indexed user, string serviceType, uint256 cost, bytes32 requestId);
    event PremiumGranted(address indexed user, uint256 expiryTime);

    constructor(address _maxxToken, address _treasuryWallet) Ownable(msg.sender) {
        require(_maxxToken != address(0), "Invalid MAXX token address");
        require(_treasuryWallet != address(0), "Invalid treasury address");
        maxxToken = IERC20(_maxxToken);
        treasuryWallet = _treasuryWallet;
    }

    // Fee percentage (50% goes to treasury, 50% burned)
    uint256 public constant FEE_PERCENTAGE = 50;

    // Precomputed fees and burns
    uint256 public constant BASIC_FEE = (BASIC_DATA_COST * FEE_PERCENTAGE) / 100;
    uint256 public constant BASIC_BURN = BASIC_DATA_COST - BASIC_FEE;
    uint256 public constant PREMIUM_FEE = (PREMIUM_DATA_COST * FEE_PERCENTAGE) / 100;
    uint256 public constant PREMIUM_BURN = PREMIUM_DATA_COST - PREMIUM_FEE;
    uint256 public constant ANALYTICS_FEE = (ANALYTICS_COST * FEE_PERCENTAGE) / 100;
    uint256 public constant ANALYTICS_BURN = ANALYTICS_COST - ANALYTICS_FEE;

    // Time constants
    uint256 public constant PREMIUM_DURATION = 30 days;

    /// @notice Grants access to basic data by burning 50% and sending 50% to treasury.
    /// @dev Emits {DataAccessed} event.
    /// @param requestId Unique ID to prevent replay attacks.
    /// @return success True if access was granted.
    function accessBasicData(bytes32 requestId) external nonReentrant returns (bool) {
        require(!requestProcessed[requestId], "Request already processed");
        require(requestId == keccak256(abi.encode(msg.sender, nonces[msg.sender]++)), "Invalid request ID");

        // Transfer fee to treasury
        maxxToken.safeTransferFrom(msg.sender, treasuryWallet, BASIC_FEE);
        // Burn the rest to dead address
        maxxToken.safeTransferFrom(msg.sender, 0x000000000000000000000000000000000000dEaD, BASIC_BURN);

        unchecked { accessCount[msg.sender]++; }
        lastAccessTime[msg.sender] = block.timestamp;
        requestProcessed[requestId] = true;

        emit DataAccessed(msg.sender, "basic_data", BASIC_DATA_COST, requestId);
        return true;
    }

    /// @notice Grants access to premium data for 30 days by burning 50% and sending 50% to treasury.
    /// @dev Emits {DataAccessed} and {PremiumGranted} events.
    /// @param requestId Unique ID to prevent replay attacks.
    /// @return success True if access was granted.
    function accessPremiumData(bytes32 requestId) external nonReentrant returns (bool) {
        require(!requestProcessed[requestId], "Request already processed");
        require(requestId == keccak256(abi.encode(msg.sender, nonces[msg.sender]++)), "Invalid request ID");

        // Transfer fee to treasury
        maxxToken.safeTransferFrom(msg.sender, treasuryWallet, PREMIUM_FEE);
        // Burn the rest to dead address
        maxxToken.safeTransferFrom(msg.sender, 0x000000000000000000000000000000000000dEaD, PREMIUM_BURN);

        unchecked { accessCount[msg.sender]++; }
        lastAccessTime[msg.sender] = block.timestamp;
        premiumExpiry[msg.sender] = block.timestamp + PREMIUM_DURATION;
        requestProcessed[requestId] = true;

        emit DataAccessed(msg.sender, "premium_data", PREMIUM_DATA_COST, requestId);
        emit PremiumGranted(msg.sender, premiumExpiry[msg.sender]);
        return true;
    }

    /// @notice Grants access to analytics data by burning 50% and sending 50% to treasury.
    /// @dev Emits {DataAccessed} event.
    /// @param requestId Unique ID to prevent replay attacks.
    /// @return success True if access was granted.
    function accessAnalytics(bytes32 requestId) external nonReentrant returns (bool) {
        require(!requestProcessed[requestId], "Request already processed");
        require(requestId == keccak256(abi.encode(msg.sender, nonces[msg.sender]++)), "Invalid request ID");

        // Transfer fee to treasury
        maxxToken.safeTransferFrom(msg.sender, treasuryWallet, ANALYTICS_FEE);
        // Burn the rest to dead address
        maxxToken.safeTransferFrom(msg.sender, 0x000000000000000000000000000000000000dEaD, ANALYTICS_BURN);

        unchecked { accessCount[msg.sender]++; }
        lastAccessTime[msg.sender] = block.timestamp;
        requestProcessed[requestId] = true;

        emit DataAccessed(msg.sender, "analytics", ANALYTICS_COST, requestId);
        return true;
    }

    /// @notice Checks user's access statistics and premium status.
    /// @param user Address to check.
    /// @return count Number of accesses, lastTime Last access timestamp, premium Whether premium is active.
    function checkAccess(address user) external view returns (uint256 count, uint256 lastTime, bool premium) {
        return (accessCount[user], lastAccessTime[user], premiumExpiry[user] > block.timestamp);
    }

    /// @notice Checks if a request ID has been processed.
    /// @param requestId Request ID to check.
    /// @return processed True if already processed.
    function isRequestProcessed(bytes32 requestId) external view returns (bool) {
        return requestProcessed[requestId];
    }

    /// @notice Updates the treasury wallet address (owner only).
    /// @param newTreasury New treasury address.
    function updateTreasury(address newTreasury) external onlyOwner {
        require(newTreasury != address(0), "Invalid treasury address");
        treasuryWallet = newTreasury;
    }

    /// @notice Proposes a new treasury wallet address (owner only).
    /// @param newTreasury Proposed treasury address.
    function proposeTreasury(address newTreasury) external onlyOwner {
        require(newTreasury != address(0), "Invalid treasury address");
        proposedTreasury = newTreasury;
    }

    /// @notice Confirms the proposed treasury wallet address (owner only).
    function confirmTreasury() external onlyOwner {
        require(proposedTreasury != address(0), "No treasury proposed");
        treasuryWallet = proposedTreasury;
        proposedTreasury = address(0);
    }

    /// @notice Emergency withdrawal of tokens (owner only).
    /// @dev Cannot withdraw MAXX tokens.
    /// @param token Token address to withdraw.
    /// @param amount Amount to withdraw.
    function emergencyWithdraw(address token, uint256 amount) external onlyOwner nonReentrant {
        require(token != address(0), "Invalid token");
        require(token != address(maxxToken), "Cannot withdraw MAXX token");
        IERC20(token).safeTransfer(owner(), amount);
    }
}
