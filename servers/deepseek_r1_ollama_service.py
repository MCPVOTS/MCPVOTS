#!/usr/bin/env python3
"""
DeepSeek R1 Ollama HTTP Service for MCPVots
==========================================
Simple HTTP service that provides DeepSeek R1 reasoning capabilities via Ollama
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional

import aiohttp
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="DeepSeek R1 Ollama Service", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ReasoningRequest(BaseModel):
    prompt: str
    model: str = "deepseek-r1:latest"
    max_tokens: int = 1000
    temperature: float = 0.7
    reasoning_type: str = "general"

class DeepSeekR1Service:
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.available_models = {
            "deepseek-r1:1.5b": "1.5B parameter model - fast inference",
            "deepseek-r1:8b": "8B parameter model - balanced performance",
            "deepseek-r1:latest": "Latest model - best reasoning capabilities"
        }
        self.dgm_active = False
        self.request_count = 0
        
    async def generate_reasoning(self, request: ReasoningRequest) -> Dict[str, Any]:
        """Generate reasoning response using DeepSeek R1 via Ollama"""
        self.request_count += 1
        
        try:
            # Prepare reasoning prompt based on type
            enhanced_prompt = self._enhance_prompt(request.prompt, request.reasoning_type)
            
            # Call Ollama API
            async with aiohttp.ClientSession() as session:
                ollama_request = {
                    "model": request.model,
                    "prompt": enhanced_prompt,
                    "options": {
                        "temperature": request.temperature,
                        "num_predict": request.max_tokens
                    }
                }
                
                async with session.post(f"{self.ollama_url}/api/generate", 
                                      json=ollama_request) as response:
                    if response.status != 200:
                        raise HTTPException(status_code=500, detail="Ollama API error")
                    
                    # Read streaming response
                    full_response = ""
                    async for line in response.content:
                        if line:
                            try:
                                chunk = json.loads(line.decode())
                                if 'response' in chunk:
                                    full_response += chunk['response']
                                if chunk.get('done', False):
                                    break
                            except json.JSONDecodeError:
                                continue
                    
                    return {
                        "response": full_response.strip(),
                        "model": request.model,
                        "reasoning_type": request.reasoning_type,
                        "timestamp": datetime.now().isoformat(),
                        "success": True,
                        "dgm_active": self.dgm_active,
                        "request_id": self.request_count
                    }
                    
        except Exception as e:
            logger.error(f"Reasoning generation failed: {e}")
            return {
                "error": str(e),
                "model": request.model,
                "reasoning_type": request.reasoning_type,
                "timestamp": datetime.now().isoformat(),
                "success": False
            }
    
    def _enhance_prompt(self, prompt: str, reasoning_type: str) -> str:
        """Enhance prompt based on reasoning type"""
        enhancements = {
            "mathematical": "Think step by step through this mathematical problem:\n",
            "logical": "Apply logical reasoning to analyze this problem:\n",
            "creative": "Use creative thinking to approach this challenge:\n",
            "analytical": "Provide a detailed analytical breakdown of:\n",
            "code": "Analyze and reason about this code problem:\n",
            "general": "Think carefully about this question:\n"
        }
        
        enhancement = enhancements.get(reasoning_type, enhancements["general"])
        return f"{enhancement}{prompt}"

# Initialize service
deepseek_service = DeepSeekR1Service()

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "DeepSeek R1 Ollama Service",
        "version": "1.0.0",
        "status": "operational",
        "available_models": deepseek_service.available_models,
        "dgm_active": deepseek_service.dgm_active,
        "requests_processed": deepseek_service.request_count,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test Ollama connection
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{deepseek_service.ollama_url}/api/tags") as response:
                ollama_healthy = response.status == 200
        
        return {
            "status": "healthy" if ollama_healthy else "degraded",
            "ollama_connected": ollama_healthy,
            "deepseek_models": deepseek_service.available_models,
            "dgm_active": deepseek_service.dgm_active,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/generate")
async def generate_reasoning(request: ReasoningRequest):
    """Generate reasoning response"""
    return await deepseek_service.generate_reasoning(request)

@app.post("/advanced_reasoning")
async def advanced_reasoning(request: ReasoningRequest):
    """Advanced reasoning endpoint (alias for generate)"""
    return await deepseek_service.generate_reasoning(request)

@app.post("/mathematical_reasoning")
async def mathematical_reasoning(request: ReasoningRequest):
    """Mathematical reasoning endpoint"""
    request.reasoning_type = "mathematical"
    return await deepseek_service.generate_reasoning(request)

@app.get("/dgm_status")
async def dgm_status():
    """Darwin Gödel Machine status"""
    return {
        "dgm_active": deepseek_service.dgm_active,
        "improvement_cycles": 0,  # Placeholder for DGM cycles
        "status": "ready",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/dgm_control")
async def dgm_control(action: Dict[str, Any]):
    """Control DGM activation"""
    if action.get("parameters", {}).get("action") == "start":
        deepseek_service.dgm_active = True
        return {"success": True, "dgm_active": True, "message": "DGM activated"}
    elif action.get("parameters", {}).get("action") == "stop":
        deepseek_service.dgm_active = False
        return {"success": True, "dgm_active": False, "message": "DGM deactivated"}
    else:
        return {"success": False, "message": "Invalid action"}

@app.get("/models")
async def list_models():
    """List available DeepSeek R1 models"""
    return {
        "models": deepseek_service.available_models,
        "default": "deepseek-r1:latest"
    }

@app.get("/metrics")
async def get_metrics():
    """Get service metrics"""
    return {
        "requests_processed": deepseek_service.request_count,
        "models_available": len(deepseek_service.available_models),
        "dgm_active": deepseek_service.dgm_active,
        "uptime": "running",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    logger.info("🚀 Starting DeepSeek R1 Ollama Service on port 8003")
    uvicorn.run(app, host="0.0.0.0", port=8003, log_level="info")
