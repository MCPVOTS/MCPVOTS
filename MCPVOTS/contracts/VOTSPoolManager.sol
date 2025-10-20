// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "./VOTSToken.sol";

/**
 * @title VOTSPoolManager
 * @dev Manages VOTS liquidity bootstrapping and fair distribution
 * Works with Uniswap V4 hooks to create initial liquidity
 */
contract VOTSPoolManager is Ownable, ReentrancyGuard {
    using SafeERC20 for IERC20;

    VOTSToken public immutable votsToken;
    address public immutable weth;

    // Bootstrap configuration
    uint256 public constant INITIAL_VOTS_SUPPLY = 1000000 ether; // 1M VOTS
    uint256 public constant INITIAL_ETH_AMOUNT = 1 ether; // 1 ETH
    uint256 public constant FAIR_LAUNCH_DURATION = 7 days;

    // Bootstrap state
    bool public bootstrapped;
    uint256 public bootstrapStartTime;
    uint256 public totalEthContributed;
    uint256 public totalVotsDistributed;

    // Participant tracking
    mapping(address => uint256) public ethContributions;
    mapping(address => bool) public hasClaimed;

    // Events
    event BootstrapStarted(uint256 startTime, uint256 duration);
    event EthContributed(address indexed contributor, uint256 amount);
    event BootstrapCompleted(uint256 totalEth, uint256 totalVots);
    event TokensClaimed(address indexed claimer, uint256 votsAmount);

    constructor(
        address _votsToken,
        address _weth
    ) Ownable(msg.sender) {
        votsToken = VOTSToken(_votsToken);
        weth = _weth;
    }

    /**
     * @dev Start the fair launch bootstrap process
     */
    function startBootstrap() external onlyOwner {
        require(!bootstrapped, "Already bootstrapped");
        require(votsToken.balanceOf(address(this)) >= INITIAL_VOTS_SUPPLY, "Insufficient VOTS tokens");

        bootstrapStartTime = block.timestamp;
        emit BootstrapStarted(bootstrapStartTime, FAIR_LAUNCH_DURATION);
    }

    /**
     * @dev Contribute ETH during fair launch period
     */
    function contributeEth() external payable nonReentrant {
        require(bootstrapStartTime > 0, "Bootstrap not started");
        require(block.timestamp <= bootstrapStartTime + FAIR_LAUNCH_DURATION, "Fair launch ended");
        require(msg.value > 0, "Must send ETH");

        ethContributions[msg.sender] += msg.value;
        totalEthContributed += msg.value;

        emit EthContributed(msg.sender, msg.value);
    }

    /**
     * @dev Complete bootstrap and create Uniswap V4 pool
     */
    function completeBootstrap() external onlyOwner nonReentrant {
        require(bootstrapStartTime > 0, "Bootstrap not started");
        require(block.timestamp > bootstrapStartTime + FAIR_LAUNCH_DURATION, "Fair launch still active");
        require(!bootstrapped, "Already completed");
        require(totalEthContributed >= INITIAL_ETH_AMOUNT, "Insufficient ETH raised");

        bootstrapped = true;

        // Calculate final token distribution
        uint256 finalVotsAmount = INITIAL_VOTS_SUPPLY;
        uint256 finalEthAmount = totalEthContributed;

        // Create the initial Uniswap V4 pool
        _createV4Pool(finalVotsAmount, finalEthAmount);

        emit BootstrapCompleted(finalEthAmount, finalVotsAmount);
    }

    /**
     * @dev Claim VOTS tokens after bootstrap completion
     */
    function claimTokens() external nonReentrant {
        require(bootstrapped, "Bootstrap not completed");
        require(!hasClaimed[msg.sender], "Already claimed");
        require(ethContributions[msg.sender] > 0, "No contribution found");

        hasClaimed[msg.sender] = true;

        // Calculate claim amount based on contribution percentage
        uint256 claimAmount = (ethContributions[msg.sender] * INITIAL_VOTS_SUPPLY) / totalEthContributed;

        // Transfer tokens to claimant
        votsToken.transfer(msg.sender, claimAmount);
        totalVotsDistributed += claimAmount;

        emit TokensClaimed(msg.sender, claimAmount);
    }

    /**
     * @dev Create Uniswap V4 pool with bootstrapped liquidity
     */
    function _createV4Pool(uint256 votsAmount, uint256 ethAmount) internal {
        // Approve tokens for pool creation
        votsToken.approve(address(this), votsAmount);
        IERC20(weth).approve(address(this), ethAmount);

        // Note: Actual V4 pool creation would require the V4 PoolManager contract
        // This is a placeholder for the pool creation logic

        // In practice, this would:
        // 1. Call poolManager.initialize() to create the pool
        // 2. Call poolManager.modifyLiquidity() to add initial liquidity
        // 3. Set up the bootstrap hook

        // For now, we'll just hold the tokens ready for pool creation
    }

    /**
     * @dev Emergency function to recover tokens if bootstrap fails
     */
    function emergencyRecover(address token, uint256 amount) external onlyOwner {
        require(!bootstrapped, "Cannot recover after bootstrap");
        IERC20(token).safeTransfer(owner(), amount);
    }

    /**
     * @dev Get bootstrap status and user contribution info
     */
    function getBootstrapInfo(address user) external view returns (
        bool _bootstrapped,
        uint256 _timeRemaining,
        uint256 _totalEthContributed,
        uint256 _userContribution,
        bool _userClaimed,
        uint256 _userClaimable
    ) {
        uint256 timeRemaining = 0;
        if (bootstrapStartTime > 0 && block.timestamp <= bootstrapStartTime + FAIR_LAUNCH_DURATION) {
            timeRemaining = (bootstrapStartTime + FAIR_LAUNCH_DURATION) - block.timestamp;
        }

        uint256 userClaimable = 0;
        if (bootstrapped && !hasClaimed[user] && ethContributions[user] > 0) {
            userClaimable = (ethContributions[user] * INITIAL_VOTS_SUPPLY) / totalEthContributed;
        }

        return (
            bootstrapped,
            timeRemaining,
            totalEthContributed,
            ethContributions[user],
            hasClaimed[user],
            userClaimable
        );
    }

    /**
     * @dev Receive ETH contributions
     */
    receive() external payable {
        if (msg.value > 0) {
            contributeEth();
        }
    }
}
