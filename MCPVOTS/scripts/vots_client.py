#!/usr/bin/env python3
"""
VOTS Agent Client Library

Simple client library for AI agents and LLMs to interact with the VOTS
ecosystem. Provides easy-to-use methods for registration, payments,
and service discovery.

Usage:
    from vots_client import VOTSClient

    client = VOTSClient()
    agent_id = client.register_agent({"name": "MyBot", "type": "trading"})
    client.make_payment({"to_agent": agent_id, "amount_vots": 0.0001})
"""

import requests
import json
import time
from typing import Dict, List, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VOTSClient:
    """Client for interacting with VOTS Agent MCP Server"""

    def __init__(self, server_url: str = "http://localhost:3001", timeout: int = 30):
        self.server_url = server_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.agent_id: Optional[str] = None

    def _post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make POST request to server"""
        url = f"{self.server_url}{endpoint}"
        try:
            response = self.session.post(url, json=data, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make GET request to server"""
        url = f"{self.server_url}{endpoint}"
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise

    def register_agent(self, agent_data: Dict[str, Any]) -> str:
        """
        Register an agent with the VOTS ecosystem

        Args:
            agent_data: Agent registration data

        Returns:
            Agent ID string
        """
        required_fields = ["name", "agent_type", "capabilities", "payment_address"]
        for field in required_fields:
            if field not in agent_data:
                raise ValueError(f"Missing required field: {field}")

        # Validate agent type
        valid_types = ["trading", "analysis", "utility", "service", "oracle"]
        if agent_data["agent_type"] not in valid_types:
            raise ValueError(f"Invalid agent type. Must be one of: {valid_types}")

        response = self._post("/agents/register", agent_data)
        agent_id = response["agent_id"]
        self.agent_id = agent_id

        logger.info(f"Agent registered successfully: {agent_id}")
        return agent_id

    def get_agent_info(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about an agent

        Args:
            agent_id: Agent ID (uses self.agent_id if not provided)

        Returns:
            Agent information dictionary
        """
        target_id = agent_id or self.agent_id
        if not target_id:
            raise ValueError("No agent ID provided and not registered")

        return self._get(f"/agents/{target_id}")

    def list_agents(self, agent_type: Optional[str] = None, capability: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all registered agents with optional filtering

        Args:
            agent_type: Filter by agent type
            capability: Filter by capability

        Returns:
            List of agent dictionaries
        """
        params = {}
        if agent_type:
            params["agent_type"] = agent_type
        if capability:
            params["capability"] = capability

        response = self._get("/agents", params)
        return response["agents"]

    def make_payment(self, payment_data: Dict[str, Any]) -> str:
        """
        Send a VOTS micro-payment

        Args:
            payment_data: Payment details

        Returns:
            Transaction ID string
        """
        required_fields = ["to_agent", "amount_vots", "service_type"]
        for field in required_fields:
            if field not in payment_data:
                raise ValueError(f"Missing required field: {field}")

        # Validate amount
        amount = payment_data["amount_vots"]
        if amount <= 0 or amount > 1.0:
            raise ValueError("Payment amount must be between 0 and 1 VOTS")

        # Add from_agent to metadata if not present
        if "metadata" not in payment_data:
            payment_data["metadata"] = {}
        if "from_agent" not in payment_data["metadata"] and self.agent_id:
            payment_data["metadata"]["from_agent"] = self.agent_id

        response = self._post("/payments/send", payment_data)

        logger.info(f"Payment initiated: {response['transaction_id']}")
        return response["transaction_id"]

    def get_payment_history(self, agent_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get payment history

        Args:
            agent_id: Agent ID to get history for (uses self.agent_id if not provided)
            limit: Maximum number of transactions to return

        Returns:
            List of transaction dictionaries
        """
        target_id = agent_id or self.agent_id
        params = {"limit": limit}
        if target_id:
            params["agent_id"] = target_id

        response = self._get("/payments/history", params)
        return response["transactions"]

    def list_services(self, service_type: Optional[str] = None, capability: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List available services in the marketplace

        Args:
            service_type: Filter by service type
            capability: Filter by capability

        Returns:
            List of service dictionaries
        """
        params = {}
        if service_type:
            params["service_type"] = service_type
        if capability:
            params["capability"] = capability

        response = self._get("/market/services", params)
        return response["services"]

    def list_service(self, service_data: Dict[str, Any], agent_id: Optional[str] = None) -> str:
        """
        List a service in the marketplace

        Args:
            service_data: Service listing data
            agent_id: Agent ID offering the service (uses self.agent_id if not provided)

        Returns:
            Service ID string
        """
        target_id = agent_id or self.agent_id
        if not target_id:
            raise ValueError("No agent ID provided and not registered")

        required_fields = ["name", "description", "price_vots", "service_type", "capabilities"]
        for field in required_fields:
            if field not in service_data:
                raise ValueError(f"Missing required field: {field}")

        # Add agent_id to the request
        service_data["agent_id"] = target_id

        response = self._post("/market/services", service_data)

        logger.info(f"Service listed: {response['service_id']}")
        return response["service_id"]

    def request_service(self, service_id: str, parameters: Dict[str, Any], from_agent: Optional[str] = None) -> str:
        """
        Request a service from the marketplace

        Args:
            service_id: Service to request
            parameters: Service parameters
            from_agent: Requesting agent ID (uses self.agent_id if not provided)

        Returns:
            Request ID string
        """
        target_id = from_agent or self.agent_id
        if not target_id:
            raise ValueError("No agent ID provided and not registered")

        # Add from_agent to parameters
        parameters["from_agent"] = target_id

        response = self._post(f"/market/request/{service_id}", parameters)

        logger.info(f"Service requested: {response['request_id']}")
        return response["request_id"]

    def get_ecosystem_stats(self) -> Dict[str, Any]:
        """
        Get ecosystem-wide statistics

        Returns:
            Statistics dictionary
        """
        return self._get("/stats/ecosystem")

    def health_check(self) -> Dict[str, Any]:
        """
        Check server health

        Returns:
            Health status dictionary
        """
        return self._get("/health")

    def wait_for_payment(self, transaction_id: str, timeout: int = 60) -> Dict[str, Any]:
        """
        Wait for a payment to complete

        Args:
            transaction_id: Transaction to wait for
            timeout: Maximum wait time in seconds

        Returns:
            Final transaction status
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            history = self.get_payment_history()
            for tx in history:
                if tx["id"] == transaction_id:
                    if tx["status"] in ["completed", "failed"]:
                        return tx

            time.sleep(2)  # Wait 2 seconds before checking again

        raise TimeoutError(f"Payment {transaction_id} did not complete within {timeout} seconds")

# Convenience functions for common use cases

def quick_register(name: str, agent_type: str, capabilities: List[str], payment_address: str) -> VOTSClient:
    """
    Quick agent registration helper

    Args:
        name: Agent name
        agent_type: Type of agent
        capabilities: List of capabilities
        payment_address: Payment address

    Returns:
        Configured VOTSClient instance
    """
    client = VOTSClient()
    client.register_agent({
        "name": name,
        "agent_type": agent_type,
        "capabilities": capabilities,
        "payment_address": payment_address
    })
    return client

def quick_payment(client: VOTSClient, to_agent: str, amount: float, service_type: str, memo: str = "") -> str:
    """
    Quick payment helper

    Args:
        client: VOTSClient instance
        to_agent: Recipient agent ID
        amount: Amount in VOTS
        service_type: Type of service
        memo: Optional memo

    Returns:
        Transaction ID
    """
    return client.make_payment({
        "to_agent": to_agent,
        "amount_vots": amount,
        "service_type": service_type,
        "memo": memo
    })

# Example usage
if __name__ == "__main__":
    # Example: Register a trading bot
    client = quick_register(
        name="Example Trading Bot",
        agent_type="trading",
        capabilities=["spot", "futures", "arbitrage"],
        payment_address="0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
    )

    print(f"Registered agent: {client.agent_id}")

    # Example: Make a micro-payment
    tx_id = quick_payment(
        client=client,
        to_agent="some-other-agent-id",
        amount=0.0001,
        service_type="data_analysis",
        memo="Market analysis fee"
    )

    print(f"Payment sent: {tx_id}")

    # Example: List available services
    services = client.list_services()
    print(f"Available services: {len(services)}")

    # Example: Get ecosystem stats
    stats = client.get_ecosystem_stats()
    print(f"Ecosystem: {stats['total_agents']} agents, {stats['daily_volume_vots']} VOTS daily volume")
