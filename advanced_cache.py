#!/usr/bin/env python3
"""
Advanced Caching Utility
Implements multiple caching strategies for performance optimization
"""

import asyncio
import json
import time
from typing import Any, Dict, Optional, Callable
from functools import wraps
import hashlib

class AdvancedCache:
    """Advanced caching implementation with TTL and LRU eviction"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.access_times: Dict[str, float] = {}
    
    def _generate_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Generate cache key from function name and arguments"""
        key_data = f"{func_name}:{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _is_expired(self, key: str) -> bool:
        """Check if cache entry is expired"""
        if key not in self.cache:
            return True
        
        entry = self.cache[key]
        return time.time() > entry["expires_at"]
    
    def _evict_lru(self) -> None:
        """Evict least recently used items"""
        if len(self.cache) >= self.max_size:
            # Remove oldest accessed item
            oldest_key = min(self.access_times, key=self.access_times.get)
            del self.cache[oldest_key]
            del self.access_times[oldest_key]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set cache entry"""
        if ttl is None:
            ttl = self.default_ttl
        
        self._evict_lru()
        
        self.cache[key] = {
            "value": value,
            "expires_at": time.time() + ttl,
            "created_at": time.time()
        }
        self.access_times[key] = time.time()
    
    def get(self, key: str) -> Any:
        """Get cache entry"""
        if key not in self.cache or self._is_expired(key):
            return None
        
        self.access_times[key] = time.time()
        return self.cache[key]["value"]
    
    def delete(self, key: str) -> None:
        """Delete cache entry"""
        if key in self.cache:
            del self.cache[key]
            del self.access_times[key]
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self.cache.clear()
        self.access_times.clear()
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hit_ratio": getattr(self, "_hit_ratio", 0),
            "total_requests": getattr(self, "_total_requests", 0)
        }

# Global cache instance
cache = AdvancedCache()

def cached(ttl: int = 3600, key_func: Optional[Callable] = None):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = cache._generate_key(func.__name__, args, kwargs)
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = cache._generate_key(func.__name__, args, kwargs)
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

# Memory-based caching for frequently accessed data
@cached(ttl=1800)  # 30 minutes
async def cached_model_response(model_name: str, prompt: str) -> str:
    """Cached model response to avoid repeated API calls"""
    # This would be implemented by the actual model calling code
    pass

@cached(ttl=3600)  # 1 hour
async def cached_file_analysis(file_path: str) -> Dict[str, Any]:
    """Cached file analysis results"""
    # This would be implemented by the actual analysis code
    pass
