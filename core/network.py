"""
Advanced Network and API System for MAXX Ecosystem
Provides HTTP client, WebSocket connections, and API management with retry logic
"""
import asyncio
import aiohttp
import websockets
import json
import time
import ssl
from typing import Dict, List, Any, Optional, Union, Callable, AsyncGenerator
from dataclasses import dataclass, asdict
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import hmac
import base64
from urllib.parse import urljoin, urlparse

from .config import get_network_config
from .logging import get_logger, log_performance


class NetworkError(Exception):
    """Network operation error"""
    pass


class APIError(NetworkError):
    """API request error"""
    pass


class WebSocketError(NetworkError):
    """WebSocket connection error"""
    pass


class RateLimitError(NetworkError):
    """Rate limit exceeded error"""
    pass


class HTTPMethod(Enum):
    """HTTP methods"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


@dataclass
class APIResponse:
    """API response wrapper"""
    status_code: int
    headers: Dict[str, str]
    data: Any
    response_time: float
    success: bool
    error_message: Optional[str] = None
    request_id: Optional[str] = None


@dataclass
class RequestConfig:
    """Request configuration"""
    timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0
    backoff_factor: float = 2.0
    headers: Optional[Dict[str, str]] = None
    params: Optional[Dict[str, Any]] = None
    auth: Optional[Dict[str, str]] = None
    verify_ssl: bool = True


@dataclass
class WebSocketMessage:
    """WebSocket message wrapper"""
    message_type: str
    data: Any
    timestamp: float
    message_id: Optional[str] = None
    correlation_id: Optional[str] = None


class RateLimiter:
    """Rate limiter for API requests"""

    def __init__(self, max_requests: int, time_window: float):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: List[float] = []
        self._lock = asyncio.Lock()

    async def acquire(self) -> bool:
        """Acquire a request slot"""
        async with self._lock:
            current_time = time.time()

            # Remove old requests outside the time window
            self.requests = [req_time for req_time in self.requests
                           if current_time - req_time < self.time_window]

            # Check if we can make a request
            if len(self.requests) < self.max_requests:
                self.requests.append(current_time)
                return True

            return False

    async def wait_for_slot(self) -> float:
        """Wait for an available request slot"""
        while not await self.acquire():
            await asyncio.sleep(0.1)

        return time.time()


class AuthManager:
    """Authentication manager for API requests"""

    def __init__(self):
        self.api_keys: Dict[str, str] = {}
        self.auth_tokens: Dict[str, Dict[str, Any]] = {}
        self.logger = get_logger(self.__class__.__name__)

    def set_api_key(self, service: str, api_key: str):
        """Set API key for a service"""
        self.api_keys[service] = api_key
        self.logger.debug(f"Set API key for service: {service}")

    def set_auth_token(self, service: str, token: Dict[str, Any]):
        """Set authentication token for a service"""
        self.auth_tokens[service] = token
        self.logger.debug(f"Set auth token for service: {service}")

    def get_auth_headers(self, service: str) -> Dict[str, str]:
        """Get authentication headers for a service"""
        headers = {}

        if service in self.api_keys:
            headers['Authorization'] = f"Bearer {self.api_keys[service]}"

        if service in self.auth_tokens:
            token = self.auth_tokens[service]
            if 'access_token' in token:
                headers['Authorization'] = f"Bearer {token['access_token']}"
            elif 'api_key' in token:
                headers['X-API-Key'] = token['api_key']

        return headers

    def sign_request(self, method: str, url: str, params: Dict[str, Any],
                    secret_key: str) -> Dict[str, str]:
        """Sign request with HMAC"""
        # Create signature string
        timestamp = str(int(time.time()))
        query_string = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
        signature_string = f"{method.upper()}\n{url}\n{timestamp}\n{query_string}"

        # Create signature
        signature = hmac.new(
            secret_key.encode(),
            signature_string.encode(),
            hashlib.sha256
        ).hexdigest()

        return {
            'X-Signature': signature,
            'X-Timestamp': timestamp
        }


class HTTPClient:
    """Advanced HTTP client with retry logic and rate limiting"""

    def __init__(self, base_url: Optional[str] = None):
        self.config = get_network_config()
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limiters: Dict[str, RateLimiter] = {}
        self.auth_manager = AuthManager()
        self.logger = get_logger(self.__class__.__name__)
        self.request_metrics: List[Dict[str, Any]] = []

        # Setup default rate limiters
        self._setup_default_rate_limiters()

    def _setup_default_rate_limiters(self):
        """Setup default rate limiters for common APIs"""
        self.rate_limiters['default'] = RateLimiter(100, 60)  # 100 requests per minute
        self.rate_limiters['solana'] = RateLimiter(100, 10)   # 100 requests per 10 seconds
        self.rate_limiters['ethereum'] = RateLimiter(30, 1)    # 30 requests per second

    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    async def initialize(self):
        """Initialize HTTP client session"""
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=self.config.request_timeout)

            connector = aiohttp.TCPConnector(
                limit=self.config.max_connections,
                limit_per_host=self.config.max_connections_per_host,
                ssl=self.config.verify_ssl,
                enable_cleanup_closed=True
            )

            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={'User-Agent': self.config.user_agent}
            )

            self.logger.info("HTTP client initialized")

    async def close(self):
        """Close HTTP client session"""
        if self.session:
            await self.session.close()
            self.session = None
            self.logger.info("HTTP client closed")

    def _get_rate_limiter(self, service: str) -> RateLimiter:
        """Get rate limiter for a service"""
        return self.rate_limiters.get(service, self.rate_limiters['default'])

    @log_performance("http.request")
    async def request(self,
                     method: Union[str, HTTPMethod],
                     endpoint: str,
                     config: Optional[RequestConfig] = None,
                     service: str = 'default',
                     **kwargs) -> APIResponse:
        """Make HTTP request with retry logic"""
        if not self.session:
            await self.initialize()

        config = config or RequestConfig()
        method = HTTPMethod(method.upper()) if isinstance(method, str) else method

        # Build URL
        url = endpoint if urlparse(endpoint).scheme else urljoin(self.base_url or '', endpoint)

        # Rate limiting
        rate_limiter = self._get_rate_limiter(service)
        await rate_limiter.wait_for_slot()

        # Prepare headers
        headers = config.headers or {}
        headers.update(self.auth_manager.get_auth_headers(service))

        # Merge request config
        request_kwargs = {
            'headers': headers,
            'params': config.params,
            'ssl': config.verify_ssl,
            'timeout': aiohttp.ClientTimeout(total=config.timeout)
        }
        request_kwargs.update(kwargs)

        # Retry logic
        last_exception = None
        for attempt in range(config.max_retries + 1):
            start_time = time.time()

            try:
                async with self.session.request(method.value, url, **request_kwargs) as response:
                    response_time = time.time() - start_time
                    content_type = response.headers.get('content-type', '')

                    # Parse response
                    if 'application/json' in content_type:
                        data = await response.json()
                    else:
                        data = await response.text()

                    api_response = APIResponse(
                        status_code=response.status,
                        headers=dict(response.headers),
                        data=data,
                        response_time=response_time,
                        success=200 <= response.status < 300,
                        request_id=response.headers.get('x-request-id')
                    )

                    # Record metrics
                    self._record_request_metrics(method.value, url, response_time,
                                               response.status, attempt + 1)

                    # Check for rate limiting
                    if response.status == 429:
                        retry_after = int(response.headers.get('retry-after', config.retry_delay))
                        await asyncio.sleep(retry_after)
                        continue

                    # Return response if successful
                    if api_response.success:
                        return api_response
                    else:
                        raise APIError(f"HTTP {response.status}: {data}")

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                last_exception = e
                self.logger.warning(f"Request attempt {attempt + 1} failed: {e}")

                if attempt < config.max_retries:
                    delay = config.retry_delay * (config.backoff_factor ** attempt)
                    await asyncio.sleep(delay)
                else:
                    raise NetworkError(f"Request failed after {config.max_retries + 1} attempts: {e}")

        # This should never be reached
        raise NetworkError("Unexpected error in request method")

    async def get(self, endpoint: str, **kwargs) -> APIResponse:
        """Make GET request"""
        return await self.request(HTTPMethod.GET, endpoint, **kwargs)

    async def post(self, endpoint: str, **kwargs) -> APIResponse:
        """Make POST request"""
        return await self.request(HTTPMethod.POST, endpoint, **kwargs)

    async def put(self, endpoint: str, **kwargs) -> APIResponse:
        """Make PUT request"""
        return await self.request(HTTPMethod.PUT, endpoint, **kwargs)

    async def delete(self, endpoint: str, **kwargs) -> APIResponse:
        """Make DELETE request"""
        return await self.request(HTTPMethod.DELETE, endpoint, **kwargs)

    def _record_request_metrics(self, method: str, url: str, response_time: float,
                               status_code: int, attempt: int):
        """Record request metrics"""
        metric = {
            'method': method,
            'url': url,
            'response_time': response_time,
            'status_code': status_code,
            'attempt': attempt,
            'timestamp': time.time()
        }

        self.request_metrics.append(metric)

        # Keep only last 1000 metrics
        if len(self.request_metrics) > 1000:
            self.request_metrics = self.request_metrics[-1000:]

    def get_metrics(self) -> List[Dict[str, Any]]:
        """Get request metrics"""
        return self.request_metrics.copy()


class WebSocketManager:
    """WebSocket connection manager"""

    def __init__(self):
        self.connections: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.clients: Dict[str, websockets.WebSocketClientProtocol] = {}
        self.message_handlers: Dict[str, Callable] = {}
        self.logger = get_logger(self.__class__.__name__)
        self._running = False

    async def start_server(self, host: str = "localhost", port: int = 8765):
        """Start WebSocket server"""
        async def handler(websocket, path):
            connection_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}:{int(time.time())}"
            self.connections[connection_id] = websocket

            try:
                self.logger.info(f"WebSocket connection established: {connection_id}")

                async for message in websocket:
                    await self._handle_message(connection_id, message)

            except websockets.exceptions.ConnectionClosed:
                self.logger.info(f"WebSocket connection closed: {connection_id}")
            finally:
                self.connections.pop(connection_id, None)

        self._running = True
        self.server = await websockets.serve(handler, host, port)
        self.logger.info(f"WebSocket server started on {host}:{port}")

    async def stop_server(self):
        """Stop WebSocket server"""
        self._running = False
        if hasattr(self, 'server'):
            self.server.close()
            await self.server.wait_closed()
            self.logger.info("WebSocket server stopped")

    async def connect_client(self, url: str, connection_id: Optional[str] = None) -> str:
        """Connect to WebSocket server as client"""
        if not connection_id:
            connection_id = f"client_{int(time.time())}"

        try:
            websocket = await websockets.connect(url)
            self.clients[connection_id] = websocket

            # Start message handler
            asyncio.create_task(self._client_message_handler(connection_id))

            self.logger.info(f"WebSocket client connected: {connection_id} -> {url}")
            return connection_id

        except Exception as e:
            raise WebSocketError(f"Failed to connect to {url}: {e}")

    async def disconnect_client(self, connection_id: str):
        """Disconnect WebSocket client"""
        if connection_id in self.clients:
            await self.clients[connection_id].close()
            del self.clients[connection_id]
            self.logger.info(f"WebSocket client disconnected: {connection_id}")

    async def send_message(self, connection_id: str, message: WebSocketMessage):
        """Send message to WebSocket connection"""
        websocket = self.connections.get(connection_id) or self.clients.get(connection_id)

        if not websocket:
            raise WebSocketError(f"Connection not found: {connection_id}")

        try:
            message_data = {
                'type': message.message_type,
                'data': message.data,
                'timestamp': message.timestamp,
                'message_id': message.message_id,
                'correlation_id': message.correlation_id
            }

            await websocket.send(json.dumps(message_data))

        except Exception as e:
            raise WebSocketError(f"Failed to send message to {connection_id}: {e}")

    async def broadcast_message(self, message: WebSocketMessage,
                              connection_type: str = 'all'):
        """Broadcast message to all connections"""
        targets = []

        if connection_type in ['all', 'server']:
            targets.extend(self.connections.values())

        if connection_type in ['all', 'client']:
            targets.extend(self.clients.values())

        message_data = json.dumps({
            'type': message.message_type,
            'data': message.data,
            'timestamp': message.timestamp,
            'message_id': message.message_id,
            'correlation_id': message.correlation_id
        })

        # Send to all targets concurrently
        tasks = []
        for websocket in targets:
            try:
                tasks.append(websocket.send(message_data))
            except Exception:
                pass  # Skip failed connections

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _handle_message(self, connection_id: str, raw_message: str):
        """Handle incoming message"""
        try:
            message_data = json.loads(raw_message)
            message = WebSocketMessage(
                message_type=message_data.get('type', 'unknown'),
                data=message_data.get('data'),
                timestamp=message_data.get('timestamp', time.time()),
                message_id=message_data.get('message_id'),
                correlation_id=message_data.get('correlation_id')
            )

            # Call registered handler
            handler = self.message_handlers.get(message.message_type)
            if handler:
                await handler(connection_id, message)
            else:
                self.logger.warning(f"No handler for message type: {message.message_type}")

        except Exception as e:
            self.logger.error(f"Failed to handle message from {connection_id}: {e}")

    async def _client_message_handler(self, connection_id: str):
        """Handle messages for client connection"""
        websocket = self.clients[connection_id]

        try:
            async for message in websocket:
                await self._handle_message(connection_id, message)

        except websockets.exceptions.ConnectionClosed:
            self.logger.info(f"Client connection closed: {connection_id}")
        finally:
            self.clients.pop(connection_id, None)

    def register_handler(self, message_type: str, handler: Callable):
        """Register message handler"""
        self.message_handlers[message_type] = handler
        self.logger.debug(f"Registered handler for message type: {message_type}")

    def unregister_handler(self, message_type: str):
        """Unregister message handler"""
        self.message_handlers.pop(message_type, None)
        self.logger.debug(f"Unregistered handler for message type: {message_type}")


class NetworkManager:
    """Unified network manager"""

    def __init__(self):
        self.http_client = HTTPClient()
        self.websocket_manager = WebSocketManager()
        self.logger = get_logger(self.__class__.__name__)

    async def initialize(self):
        """Initialize network manager"""
        await self.http_client.initialize()
        self.logger.info("Network manager initialized")

    async def close(self):
        """Close network manager"""
        await self.http_client.close()
        await self.websocket_manager.stop_server()
        self.logger.info("Network manager closed")

    def get_http_client(self, base_url: Optional[str] = None) -> HTTPClient:
        """Get HTTP client instance"""
        if base_url:
            return HTTPClient(base_url)
        return self.http_client

    def get_websocket_manager(self) -> WebSocketManager:
        """Get WebSocket manager instance"""
        return self.websocket_manager


# Global network manager
_network_manager: Optional[NetworkManager] = None


async def get_network_manager() -> NetworkManager:
    """Get global network manager instance"""
    global _network_manager

    if _network_manager is None:
        _network_manager = NetworkManager()
        await _network_manager.initialize()

    return _network_manager


async def close_network():
    """Close global network manager"""
    global _network_manager

    if _network_manager:
        await _network_manager.close()
        _network_manager = None