// MAXX Micro-Transaction Middleware Contract
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract MAXXMiddleware is Ownable, ReentrancyGuard {
    IERC20 public immutable maxxToken;
    address public treasuryWallet;

    // Service tiers with MAXX costs (in wei)
    uint256 public constant BASIC_ACCESS_COST = 1000000000000000; // 0.001 MAXX
    uint256 public constant PREMIUM_ACCESS_COST = 10000000000000000; // 0.01 MAXX
    uint256 public constant API_CALL_COST = 100000000000000; // 0.0001 MAXX

    // User access tracking
    mapping(address => uint256) public lastAccessTime;
    mapping(address => bool) public hasPremiumAccess;
    mapping(address => uint256) public apiCallCount;

    // Events
    event ServiceAccessed(address indexed user, string serviceType, uint256 cost);
    event PremiumAccessGranted(address indexed user, uint256 expiryTime);
    event TreasuryUpdated(address indexed oldTreasury, address indexed newTreasury);

    constructor(address _maxxToken, address _treasuryWallet) {
        maxxToken = IERC20(_maxxToken);
        treasuryWallet = _treasuryWallet;
    }

    // Basic service access (view dashboard, basic monitoring)
    function accessBasicService() external nonReentrant {
        require(maxxToken.transferFrom(msg.sender, treasuryWallet, BASIC_ACCESS_COST), "Payment failed");
        lastAccessTime[msg.sender] = block.timestamp;
        emit ServiceAccessed(msg.sender, "basic", BASIC_ACCESS_COST);
    }

    // Premium access (advanced features for 30 days)
    function purchasePremiumAccess() external nonReentrant {
        require(maxxToken.transferFrom(msg.sender, treasuryWallet, PREMIUM_ACCESS_COST), "Payment failed");
        hasPremiumAccess[msg.sender] = true;
        emit PremiumAccessGranted(msg.sender, block.timestamp + 30 days);
    }

    // API call tracking (for rate limiting)
    function trackApiCall() external nonReentrant {
        require(maxxToken.transferFrom(msg.sender, treasuryWallet, API_CALL_COST), "Payment failed");
        apiCallCount[msg.sender]++;
        emit ServiceAccessed(msg.sender, "api_call", API_CALL_COST);
    }

    // Check if user has premium access
    function checkPremiumAccess(address user) external view returns (bool) {
        return hasPremiumAccess[user];
    }

    // Get user's API usage
    function getApiUsage(address user) external view returns (uint256) {
        return apiCallCount[user];
    }

    // Update treasury wallet (only owner)
    function updateTreasury(address newTreasury) external onlyOwner {
        address oldTreasury = treasuryWallet;
        treasuryWallet = newTreasury;
        emit TreasuryUpdated(oldTreasury, newTreasury);
    }

    // Emergency withdraw (only owner)
    function emergencyWithdraw(address token, uint256 amount) external onlyOwner {
        IERC20(token).transfer(owner(), amount);
    }
}</content>
<parameter name="filePath">c:\PumpFun_Ecosystem\ECOSYSTEM_UNIFIED\contracts\MAXXMiddleware.sol
