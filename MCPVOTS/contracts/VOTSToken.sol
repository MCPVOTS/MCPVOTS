// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title VOTSToken
 * @dev VOTS token with burn mechanisms for bot ecosystem micro-payments
 * Compatible with Uniswap V4 for automated liquidity bootstrapping
 */
contract VOTSToken is ERC20, ERC20Burnable, Ownable, ReentrancyGuard {
    // Burn tracking
    uint256 public totalBurned;
    uint256 public burnRate; // Basis points (0.01% = 1)

    // Bot ecosystem tracking
    mapping(address => bool) public registeredBots;
    mapping(address => uint256) public botRewards;

    // Events
    event BotRegistered(address indexed bot, string serviceType);
    event MicroPayment(address indexed from, address indexed to, uint256 amount, string memo);
    event BurnExecuted(address indexed burner, uint256 amount, string reason);
    event BurnRateUpdated(uint256 oldRate, uint256 newRate);

    constructor(
        string memory name,
        string memory symbol,
        uint256 initialSupply,
        uint256 _burnRate
    ) ERC20(name, symbol) Ownable(msg.sender) {
        require(_burnRate <= 10000, "Burn rate cannot exceed 100%");
        burnRate = _burnRate;

        // Mint initial supply to owner for liquidity bootstrapping
        _mint(msg.sender, initialSupply);
    }

    /**
     * @dev Register a bot in the ecosystem
     */
    function registerBot(address bot, string calldata serviceType) external onlyOwner {
        require(!registeredBots[bot], "Bot already registered");
        registeredBots[bot] = true;
        emit BotRegistered(bot, serviceType);
    }

    /**
     * @dev Micro-payment between bots with automatic burn
     */
    function microPayment(
        address to,
        uint256 amount,
        string calldata memo
    ) external nonReentrant {
        require(amount > 0, "Amount must be positive");
        require(balanceOf(msg.sender) >= amount, "Insufficient balance");

        // Calculate burn amount (0.01% default)
        uint256 burnAmount = (amount * burnRate) / 10000;
        uint256 netAmount = amount - burnAmount;

        // Execute transfers
        _transfer(msg.sender, to, netAmount);
        if (burnAmount > 0) {
            _burn(msg.sender, burnAmount);
            totalBurned += burnAmount;
            emit BurnExecuted(msg.sender, burnAmount, "Micro-payment burn");
        }

        // Track bot rewards if recipient is registered bot
        if (registeredBots[to]) {
            botRewards[to] += netAmount;
        }

        emit MicroPayment(msg.sender, to, netAmount, memo);
    }

    /**
     * @dev Update burn rate (only owner)
     */
    function updateBurnRate(uint256 newRate) external onlyOwner {
        require(newRate <= 10000, "Burn rate cannot exceed 100%");
        uint256 oldRate = burnRate;
        burnRate = newRate;
        emit BurnRateUpdated(oldRate, newRate);
    }

    /**
     * @dev Get burn statistics
     */
    function getBurnStats() external view returns (
        uint256 _totalBurned,
        uint256 _burnRate,
        uint256 circulatingSupply
    ) {
        return (
            totalBurned,
            burnRate,
            totalSupply() - totalBurned
        );
    }

    /**
     * @dev Override transfer to include burn mechanism
     */
    function transfer(address to, uint256 amount) public override returns (bool) {
        // For regular transfers, apply burn rate
        if (burnRate > 0 && amount > 0) {
            uint256 burnAmount = (amount * burnRate) / 10000;
            uint256 netAmount = amount - burnAmount;

            _transfer(msg.sender, to, netAmount);
            if (burnAmount > 0) {
                _burn(msg.sender, burnAmount);
                totalBurned += burnAmount;
                emit BurnExecuted(msg.sender, burnAmount, "Transfer burn");
            }
            return true;
        }
        return super.transfer(to, amount);
    }

    /**
     * @dev Override transferFrom to include burn mechanism
     */
    function transferFrom(address from, address to, uint256 amount) public override returns (bool) {
        // For regular transfers, apply burn rate
        if (burnRate > 0 && amount > 0) {
            uint256 burnAmount = (amount * burnRate) / 10000;
            uint256 netAmount = amount - burnAmount;

            _transfer(from, to, netAmount);
            if (burnAmount > 0) {
                _burn(from, burnAmount);
                totalBurned += burnAmount;
                emit BurnExecuted(from, burnAmount, "TransferFrom burn");
            }

            // Update allowance
            uint256 currentAllowance = allowance(from, msg.sender);
            require(currentAllowance >= amount, "ERC20: transfer amount exceeds allowance");
            _approve(from, msg.sender, currentAllowance - amount);

            return true;
        }
        return super.transferFrom(from, to, amount);
    }
}
