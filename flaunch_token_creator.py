#!/usr/bin/env python3
"""
Flaunch Token Creator - Create and launch your own Flaunch tokens on Base

This script integrates with the Flaunch protocol to create new memecoins with:
- Royalty NFT ownership (transferable revenue streams)
- Progressive Bid Wall (automatic buyback protection)
- Fair launch mechanics
- Creator revenue sharing

Usage:
    python flaunch_token_creator.py --name "MyToken" --symbol "MTK" --mcap 50000 --creator-fee 50

Requirements:
    - Node.js and npm for Flaunch SDK
    - Web3 wallet with Base network
    - ETH for gas fees (no protocol fees for < $10k market caps)
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import os

class FlaunchTokenCreator:
    """Creates and launches Flaunch tokens using the TypeScript SDK"""

    def __init__(self, wallet_address: Optional[str] = None, private_key: Optional[str] = None):
        self.wallet_address = wallet_address or os.getenv('WALLET_ADDRESS')
        self.private_key = private_key or os.getenv('PRIVATE_KEY')
        self.sdk_path = Path(__file__).parent / 'flaunch_sdk_integration'

        if not self.wallet_address:
            raise ValueError("Wallet address required. Set WALLET_ADDRESS env var or pass --wallet")

    def setup_sdk_integration(self):
        """Set up the Node.js/TypeScript integration for Flaunch SDK"""
        sdk_dir = self.sdk_path
        sdk_dir.mkdir(exist_ok=True)

        # Create package.json for the SDK integration
        package_json = {
            "name": "flaunch-sdk-integration",
            "version": "1.0.0",
            "type": "module",
            "scripts": {
                "create-token": "node create_token.js",
                "install": "npm install"
            },
            "dependencies": {
                "@flaunch/sdk": "^0.1.0",
                "viem": "^2.0.0",
                "dotenv": "^16.0.0"
            }
        }

        with open(sdk_dir / 'package.json', 'w') as f:
            json.dump(package_json, f, indent=2)

        # Create the token creation script
        create_token_js = f'''
import {{ createFlaunch }} from "@flaunch/sdk";
import {{ createPublicClient, createWalletClient, http, parseEther }} from "viem";
import {{ privateKeyToAccount }} from "viem/accounts";
import {{ base }} from "viem/chains";
import {{ readFileSync }} from "fs";

// Load environment variables
const walletAddress = process.env.WALLET_ADDRESS || "{self.wallet_address}";
const privateKey = process.env.PRIVATE_KEY;

if (!privateKey) {{
    console.error("PRIVATE_KEY environment variable required");
    process.exit(1);
}}

const account = privateKeyToAccount(privateKey);

// Set up clients
const publicClient = createPublicClient({{
    chain: base,
    transport: http(process.env.BASE_RPC_URL || "https://mainnet.base.org"),
}});

const walletClient = createWalletClient({{
    account,
    chain: base,
    transport: http(process.env.BASE_RPC_URL || "https://mainnet.base.org"),
}});

// Create Flaunch SDK instance
const flaunch = createFlaunch({{
    publicClient,
    walletClient,
}});

// Read token parameters from stdin (JSON)
const input = readFileSync(0, 'utf-8');
const params = JSON.parse(input);

async function createToken() {{
    try {{
        console.log("🚀 Creating Flaunch token:", params.name);

        // Use flaunchIPFS for automatic metadata handling
        const hash = await flaunch.flaunchIPFS({{
            name: params.name,
            symbol: params.symbol,
            fairLaunchPercent: params.fairLaunchPercent,
            fairLaunchDuration: params.fairLaunchDuration || 30 * 60, // 30 mins default
            initialMarketCapUSD: params.initialMarketCapUSD,
            creatorFeeAllocationPercent: params.creatorFeeAllocationPercent,
            metadata: params.metadata || {{
                description: `Flaunched token: ${{params.name}}`,
                image: params.image || "https://via.placeholder.com/400x400?text=" + params.symbol,
                external_url: params.externalUrl || "",
                attributes: [
                    {{
                        trait_type: "Creator Fee",
                        value: `${{params.creatorFeeAllocationPercent}}%`
                    }},
                    {{
                        trait_type: "Fair Launch",
                        value: `${{params.fairLaunchPercent}}%`
                    }},
                    {{
                        trait_type: "Initial Market Cap",
                        value: `$${params.initialMarketCapUSD.toLocaleString()}`
                    }}
                ]
            }},
            pinataConfig: params.pinataConfig // Optional IPFS pinning
        }});

        console.log("✅ Token created! Transaction hash:", hash);

        // Wait for transaction confirmation
        const receipt = await publicClient.waitForTransactionReceipt({{ hash }});
        console.log("✅ Transaction confirmed in block:", receipt.blockNumber);

        // Extract token address from logs (this would need to be parsed from the event)
        // For now, we'll need to query the contract or use events

        return {{ hash, receipt }};

    }} catch (error) {{
        console.error("❌ Error creating token:", error);
        process.exit(1);
    }}
}}

createToken();
'''

        with open(sdk_dir / 'create_token.js', 'w') as f:
            f.write(create_token_js)

        # Create .env template
        env_template = f'''# Flaunch SDK Environment Variables
WALLET_ADDRESS={self.wallet_address}
PRIVATE_KEY=your_private_key_here
BASE_RPC_URL=https://mainnet.base.org
PINATA_API_KEY=your_pinata_key_here
PINATA_SECRET_KEY=your_pinata_secret_here
'''

        with open(sdk_dir / '.env.example', 'w') as f:
            f.write(env_template)

        print(f"✅ SDK integration setup in {sdk_dir}")
        return sdk_dir

    def create_token(self,
                    name: str,
                    symbol: str,
                    initial_market_cap: float = 10000,
                    fair_launch_percent: float = 60,
                    fair_launch_duration: int = 1800,  # 30 minutes
                    creator_fee_percent: float = 50,
                    description: Optional[str] = None,
                    image_url: Optional[str] = None,
                    external_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new Flaunch token

        Args:
            name: Token name
            symbol: Token symbol (3-8 characters)
            initial_market_cap: Starting market cap in USD (< $10k = no protocol fees)
            fair_launch_percent: Percentage allocated to fair launch (40-80 recommended)
            fair_launch_duration: Fair launch duration in seconds
            creator_fee_percent: Creator's share of trading fees (0-100)
            description: Token description
            image_url: Token image URL
            external_url: External link (website, social media)

        Returns:
            Dict with transaction details and token info
        """

        # Validate inputs
        if len(symbol) > 8:
            raise ValueError("Symbol must be 8 characters or less")
        if not (40 <= fair_launch_percent <= 80):
            print("⚠️ Warning: Fair launch percent outside recommended 40-80% range")
        if initial_market_cap >= 10000:
            print("⚠️ Warning: Market caps >= $10k incur protocol fees")

        # Set up SDK if needed
        sdk_dir = self.setup_sdk_integration()

        # Prepare token parameters
        token_params = {
            "name": name,
            "symbol": symbol.upper(),
            "initialMarketCapUSD": initial_market_cap,
            "fairLaunchPercent": fair_launch_percent,
            "fairLaunchDuration": fair_launch_duration,
            "creatorFeeAllocationPercent": creator_fee_percent,
            "metadata": {
                "description": description or f"Flaunched token: {name}",
                "image": image_url or f"https://via.placeholder.com/400x400?text={symbol}",
                "external_url": external_url or "",
                "attributes": [
                    {
                        "trait_type": "Creator Fee",
                        "value": f"{creator_fee_percent}%"
                    },
                    {
                        "trait_type": "Fair Launch",
                        "value": f"{fair_launch_percent}%"
                    },
                    {
                        "trait_type": "Initial Market Cap",
                        "value": f"${initial_market_cap:,.0f}"
                    }
                ]
            }
        }

        # Install dependencies if needed
        if not (sdk_dir / 'node_modules').exists():
            print("📦 Installing SDK dependencies...")
            subprocess.run(['npm', 'install'], cwd=sdk_dir, check=True)

        # Run the token creation script
        print(f"🚀 Creating Flaunch token: {name} (${symbol})")
        print(f"   Market Cap: ${initial_market_cap:,.0f}")
        print(f"   Fair Launch: {fair_launch_percent}%")
        print(f"   Creator Fee: {creator_fee_percent}%")

        try:
            result = subprocess.run(
                ['node', 'create_token.js'],
                cwd=sdk_dir,
                input=json.dumps(token_params),
                text=True,
                capture_output=True,
                check=True
            )

            # Parse the output (would need to be structured in the JS script)
            print("✅ Token creation initiated!")
            print(result.stdout)

            return {
                "success": True,
                "name": name,
                "symbol": symbol,
                "params": token_params,
                "output": result.stdout
            }

        except subprocess.CalledProcessError as e:
            print(f"❌ Token creation failed: {e}")
            print(f"Error output: {e.stderr}")
            return {
                "success": False,
                "error": str(e),
                "stderr": e.stderr
            }

def main():
    parser = argparse.ArgumentParser(description="Create Flaunch tokens on Base")
    parser.add_argument("--name", required=True, help="Token name")
    parser.add_argument("--symbol", required=True, help="Token symbol (max 8 chars)")
    parser.add_argument("--mcap", type=float, default=10000, help="Initial market cap in USD")
    parser.add_argument("--fair-launch", type=float, default=60, help="Fair launch percentage (40-80)")
    parser.add_argument("--duration", type=int, default=1800, help="Fair launch duration in seconds")
    parser.add_argument("--creator-fee", type=float, default=50, help="Creator fee percentage (0-100)")
    parser.add_argument("--description", help="Token description")
    parser.add_argument("--image", help="Token image URL")
    parser.add_argument("--external-url", help="External URL (website/social)")
    parser.add_argument("--wallet", help="Wallet address (or set WALLET_ADDRESS env var)")

    args = parser.parse_args()

    # Check for private key
    if not os.getenv('PRIVATE_KEY'):
        print("❌ PRIVATE_KEY environment variable required")
        print("Set it with: export PRIVATE_KEY=your_private_key")
        sys.exit(1)

    creator = FlaunchTokenCreator(wallet_address=args.wallet)

    result = creator.create_token(
        name=args.name,
        symbol=args.symbol,
        initial_market_cap=args.mcap,
        fair_launch_percent=args.fair_launch,
        fair_launch_duration=args.duration,
        creator_fee_percent=args.creator_fee,
        description=args.description,
        image_url=args.image,
        external_url=args.external_url
    )

    if result["success"]:
        print("\n🎉 Token creation successful!")
        print(f"Name: {result['name']}")
        print(f"Symbol: {result['symbol']}")
        print("\n💡 Your Royalty NFT gives you ownership of future revenue streams!")
        print("💡 Progressive Bid Wall will provide automatic buyback protection!")
    else:
        print("\n❌ Token creation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
