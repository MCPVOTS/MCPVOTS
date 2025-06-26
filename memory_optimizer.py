#!/usr/bin/env python3
"""
Memory Optimization Utility
Implements memory-efficient patterns and monitoring
"""

import gc
import psutil
import sys
from typing import Any, Generator, Iterator, Optional
from collections import deque
import weakref
import logging

logger = logging.getLogger(__name__)

class MemoryOptimizer:
    """Memory optimization utilities"""
    
    @staticmethod
    def get_memory_usage() -> Dict[str, float]:
        """Get current memory usage statistics"""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            "rss_mb": memory_info.rss / 1024 / 1024,
            "vms_mb": memory_info.vms / 1024 / 1024,
            "percent": process.memory_percent(),
            "system_available_mb": psutil.virtual_memory().available / 1024 / 1024
        }
    
    @staticmethod
    def force_garbage_collection() -> Dict[str, int]:
        """Force garbage collection and return statistics"""
        before = len(gc.get_objects())
        collected = gc.collect()
        after = len(gc.get_objects())
        
        return {
            "objects_before": before,
            "objects_after": after,
            "collected": collected,
            "freed": before - after
        }

class MemoryEfficientDataProcessor:
    """Memory-efficient data processing patterns"""
    
    @staticmethod
    def batch_process(data: Iterator[Any], batch_size: int = 1000) -> Generator[List[Any], None, None]:
        """Process data in batches to reduce memory usage"""
        batch = []
        for item in data:
            batch.append(item)
            if len(batch) >= batch_size:
                yield batch
                batch = []
        
        if batch:
            yield batch
    
    @staticmethod
    def lazy_file_reader(file_path: str, chunk_size: int = 8192) -> Generator[str, None, None]:
        """Read file lazily to reduce memory usage"""
        with open(file_path, 'r', encoding='utf-8') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                yield chunk
    
    @staticmethod
    def memory_efficient_json_processor(file_path: str) -> Generator[Dict[str, Any], None, None]:
        """Process large JSON files efficiently"""
        import json
        
        with open(file_path, 'r', encoding='utf-8') as f:
            # For large JSON arrays, we'd need a streaming JSON parser
            # This is a simplified version
            for line in f:
                try:
                    yield json.loads(line.strip())
                except json.JSONDecodeError:
                    continue

class ObjectPool:
    """Object pool for reusing expensive objects"""
    
    def __init__(self, factory_func, max_size: int = 100):
        self.factory_func = factory_func
        self.pool = deque(maxlen=max_size)
        self.max_size = max_size
    
    def get(self):
        """Get object from pool or create new one"""
        if self.pool:
            return self.pool.popleft()
        return self.factory_func()
    
    def return_object(self, obj):
        """Return object to pool"""
        if len(self.pool) < self.max_size:
            self.pool.append(obj)

class WeakRefCache:
    """Cache using weak references to avoid memory leaks"""
    
    def __init__(self):
        self._cache = weakref.WeakValueDictionary()
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached object"""
        return self._cache.get(key)
    
    def set(self, key: str, value: Any) -> None:
        """Set cached object"""
        self._cache[key] = value
    
    def size(self) -> int:
        """Get cache size"""
        return len(self._cache)

# Global instances
memory_optimizer = MemoryOptimizer()
data_processor = MemoryEfficientDataProcessor()

# Decorators for memory optimization
def memory_profile(func):
    """Decorator to profile memory usage of functions"""
    def wrapper(*args, **kwargs):
        before = memory_optimizer.get_memory_usage()
        result = func(*args, **kwargs)
        after = memory_optimizer.get_memory_usage()
        
        memory_delta = after["rss_mb"] - before["rss_mb"]
        if memory_delta > 10:  # Log if memory usage increased by more than 10MB
            logger.warning(f"Function {func.__name__} increased memory usage by {memory_delta:.2f} MB")
        
        return result
    return wrapper

def auto_gc(threshold_mb: float = 100):
    """Decorator to automatically trigger GC when memory usage is high"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            before = memory_optimizer.get_memory_usage()
            result = func(*args, **kwargs)
            after = memory_optimizer.get_memory_usage()
            
            if after["rss_mb"] > threshold_mb:
                gc_stats = memory_optimizer.force_garbage_collection()
                logger.info(f"Auto GC triggered, freed {gc_stats['freed']} objects")
            
            return result
        return wrapper
    return decorator
