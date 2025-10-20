#!/usr/bin/env python3
"""
ETHERMAX Intelligence System API
RESTful API endpoints for external access to trading intelligence
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pathlib import Path
import uuid

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import uvicorn

# Import intelligence system
from ethermax_intelligence import (
    EthermaxIntelligence,
    get_intelligence_instance,
    analyze_wallet_intelligence,
    generate_intelligence_report,
    start_monitoring,
    detect_ethermax_patterns
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ETHERMAX Intelligence API",
    description="Advanced trading pattern detection and analysis API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Global intelligence instance
intelligence_instance = None

# API Key management (in production, use proper secure storage)
API_KEYS = {
    "ethermax_admin": "admin_key_123456",
    "ethermax_analyst": "analyst_key_789012",
    "ethermax_monitor": "monitor_key_345678"
}

# Pydantic models for request/response
class WalletAnalysisRequest(BaseModel):
    wallet_address: str = Field(..., description="Wallet address to analyze")
    include_patterns: bool = Field(True, description="Include pattern analysis")
    include_performance: bool = Field(True, description="Include performance metrics")
    include_risk: bool = Field(True, description="Include risk assessment")
    include_opportunities: bool = Field(True, description="Include opportunity detection")
    time_range_days: int = Field(30, description="Time range for analysis in days")

class BatchAnalysisRequest(BaseModel):
    wallet_addresses: List[str] = Field(..., description="List of wallet addresses to analyze")
    analysis_type: str = Field("comprehensive", description="Type of analysis: comprehensive, patterns_only, risk_only")
    priority: str = Field("normal", description="Priority: low, normal, high, critical")

class MonitoringRequest(BaseModel):
    wallet_addresses: List[str] = Field(..., description="Wallet addresses to monitor")
    alert_thresholds: Dict[str, float] = Field(default_factory=dict, description="Custom alert thresholds")
    notification_channels: List[str] = Field(default_factory=list, description="Notification channels")

class ReportRequest(BaseModel):
    wallet_address: str = Field(..., description="Wallet address for report")
    report_type: str = Field("comprehensive", description="Report type: comprehensive, summary, detailed")
    format: str = Field("json", description="Report format: json, pdf, html")
    include_visualizations: bool = Field(True, description="Include charts and graphs")

class PatternSearchRequest(BaseModel):
    pattern_types: List[str] = Field(default_factory=list, description="Pattern types to search for")
    confidence_threshold: float = Field(0.5, description="Minimum confidence score")
    risk_levels: List[str] = Field(default_factory=list, description="Risk levels to filter")
    time_range_days: int = Field(30, description="Time range for search")

class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

class AnalysisResponse(APIResponse):
    analysis_id: str
    wallet_address: str
    analysis_type: str
    completion_time: Optional[str] = None

class MonitoringResponse(APIResponse):
    monitoring_id: str
    wallet_addresses: List[str]
    status: str
    alert_count: int = 0

# Background task management
background_tasks = {}

# Dependency for API key authentication
async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if token not in API_KEYS.values():
        raise HTTPException(status_code=403, detail="Invalid API key")
    return token

# Dependency for getting intelligence instance
async def get_intelligence():
    global intelligence_instance
    if intelligence_instance is None:
        intelligence_instance = await get_intelligence_instance()
    return intelligence_instance

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize the intelligence system on API startup"""
    global intelligence_instance
    try:
        logger.info("Initializing ETHERMAX Intelligence System...")
        intelligence_instance = await get_intelligence_instance()
        logger.info("Intelligence system initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize intelligence system: {e}")
        # Continue without intelligence - some endpoints may still work

# Health check endpoint
@app.get("/health", response_model=APIResponse)
async def health_check():
    """Check API health status"""
    return APIResponse(
        success=True,
        message="ETHERMAX Intelligence API is running",
        data={
            "status": "healthy",
            "version": "1.0.0",
            "intelligence_initialized": intelligence_instance is not None
        }
    )

# System status endpoint
@app.get("/status", response_model=APIResponse)
async def system_status(api_key: str = Depends(verify_api_key)):
    """Get detailed system status"""
    global intelligence_instance

    status_data = {
        "api_status": "running",
        "intelligence_status": "initialized" if intelligence_instance else "not_initialized",
        "active_monitoring_sessions": len(background_tasks),
        "cache_directory": str(intelligence_instance.cache_dir) if intelligence_instance else None,
        "supported_endpoints": [
            "/analyze/wallet",
            "/analyze/batch",
            "/monitoring/start",
            "/reports/generate",
            "/patterns/search",
            "/intelligence/ethermax",
            "/system/status"
        ]
    }

    if intelligence_instance:
        try:
            # Get additional status from intelligence system
            status_data["intelligence_details"] = {
                "is_initialized": intelligence_instance.is_initialized,
                "chromadb_connected": intelligence_instance.chromadb is not None,
                "analysis_config": intelligence_instance.analysis_config
            }
        except Exception as e:
            logger.warning(f"Could not get intelligence details: {e}")

    return APIResponse(
        success=True,
        message="System status retrieved successfully",
        data=status_data
    )

# Wallet analysis endpoint
@app.post("/analyze/wallet", response_model=AnalysisResponse)
async def analyze_wallet(
    request: WalletAnalysisRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key),
    intelligence: EthermaxIntelligence = Depends(get_intelligence)
):
    """Analyze a single wallet for trading patterns and intelligence"""
    try:
        analysis_id = str(uuid.uuid4())

        # Validate wallet address
        if not request.wallet_address.startswith("0x") or len(request.wallet_address) != 42:
            raise HTTPException(status_code=400, detail="Invalid wallet address format")

        # Start analysis in background
        async def run_analysis():
            try:
                logger.info(f"Starting wallet analysis for {request.wallet_address}")

                # Perform comprehensive analysis
                analysis_result = await intelligence.analyze_trading_patterns(
                    wallet_address=request.wallet_address,
                    time_range_days=request.time_range_days
                )

                # Filter results based on request
                filtered_result = {}
                if request.include_patterns:
                    filtered_result["patterns"] = analysis_result.get("patterns", [])
                if request.include_performance:
                    filtered_result["performance_metrics"] = analysis_result.get("performance_metrics", {})
                if request.include_risk:
                    filtered_result["risk_assessment"] = analysis_result.get("risk_assessment", {})
                if request.include_opportunities:
                    filtered_result["opportunities"] = analysis_result.get("opportunities", {})

                # Store result
                result_file = intelligence.cache_dir / f"analysis_{analysis_id}.json"
                with open(result_file, 'w') as f:
                    json.dump({
                        "wallet_address": request.wallet_address,
                        "analysis_id": analysis_id,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "result": filtered_result
                    }, f, indent=2, default=str)

                logger.info(f"Wallet analysis completed for {request.wallet_address}")

            except Exception as e:
                logger.error(f"Wallet analysis failed for {request.wallet_address}: {e}")
                # Store error result
                result_file = intelligence.cache_dir / f"analysis_{analysis_id}.json"
                with open(result_file, 'w') as f:
                    json.dump({
                        "wallet_address": request.wallet_address,
                        "analysis_id": analysis_id,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "error": str(e)
                    }, f, indent=2)

        # Add background task
        background_tasks.add_task(run_analysis)

        return AnalysisResponse(
            success=True,
            message="Wallet analysis started",
            analysis_id=analysis_id,
            wallet_address=request.wallet_address,
            analysis_type="wallet"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in wallet analysis endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Batch analysis endpoint
@app.post("/analyze/batch", response_model=AnalysisResponse)
async def analyze_batch(
    request: BatchAnalysisRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key),
    intelligence: EthermaxIntelligence = Depends(get_intelligence)
):
    """Analyze multiple wallets in batch"""
    try:
        analysis_id = str(uuid.uuid4())

        # Validate wallet addresses
        for wallet in request.wallet_addresses:
            if not wallet.startswith("0x") or len(wallet) != 42:
                raise HTTPException(status_code=400, detail=f"Invalid wallet address format: {wallet}")

        # Start batch analysis in background
        async def run_batch_analysis():
            try:
                logger.info(f"Starting batch analysis for {len(request.wallet_addresses)} wallets")

                batch_results = {}

                for wallet_address in request.wallet_addresses:
                    try:
                        # Perform analysis based on type
                        if request.analysis_type == "comprehensive":
                            result = await intelligence.analyze_trading_patterns(wallet_address=wallet_address)
                        elif request.analysis_type == "patterns_only":
                            patterns = await intelligence._recognize_trading_patterns(
                                await intelligence._get_wallet_trades(wallet_address)
                            )
                            result = {"patterns": patterns}
                        elif request.analysis_type == "risk_only":
                            trades = await intelligence._get_wallet_trades(wallet_address)
                            result = await intelligence._assess_trading_risk(trades)
                        else:
                            raise ValueError(f"Unknown analysis type: {request.analysis_type}")

                        batch_results[wallet_address] = {
                            "success": True,
                            "result": result
                        }

                    except Exception as e:
                        logger.error(f"Analysis failed for wallet {wallet_address}: {e}")
                        batch_results[wallet_address] = {
                            "success": False,
                            "error": str(e)
                        }

                # Store batch result
                result_file = intelligence.cache_dir / f"batch_analysis_{analysis_id}.json"
                with open(result_file, 'w') as f:
                    json.dump({
                        "analysis_id": analysis_id,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "analysis_type": request.analysis_type,
                        "priority": request.priority,
                        "wallet_count": len(request.wallet_addresses),
                        "results": batch_results
                    }, f, indent=2, default=str)

                logger.info(f"Batch analysis completed for {len(request.wallet_addresses)} wallets")

            except Exception as e:
                logger.error(f"Batch analysis failed: {e}")
                # Store error result
                result_file = intelligence.cache_dir / f"batch_analysis_{analysis_id}.json"
                with open(result_file, 'w') as f:
                    json.dump({
                        "analysis_id": analysis_id,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "error": str(e)
                    }, f, indent=2)

        # Add background task
        background_tasks.add_task(run_batch_analysis)

        return AnalysisResponse(
            success=True,
            message="Batch analysis started",
            analysis_id=analysis_id,
            wallet_address="batch",
            analysis_type=request.analysis_type
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch analysis endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Get analysis results endpoint
@app.get("/analyze/results/{analysis_id}", response_model=APIResponse)
async def get_analysis_results(
    analysis_id: str,
    api_key: str = Depends(verify_api_key),
    intelligence: EthermaxIntelligence = Depends(get_intelligence)
):
    """Get results of a previous analysis"""
    try:
        # Check for individual analysis
        result_file = intelligence.cache_dir / f"analysis_{analysis_id}.json"
        if result_file.exists():
            with open(result_file, 'r') as f:
                result = json.load(f)

            return APIResponse(
                success=True,
                message="Analysis results retrieved",
                data=result
            )

        # Check for batch analysis
        batch_result_file = intelligence.cache_dir / f"batch_analysis_{analysis_id}.json"
        if batch_result_file.exists():
            with open(batch_result_file, 'r') as f:
                result = json.load(f)

            return APIResponse(
                success=True,
                message="Batch analysis results retrieved",
                data=result
            )

        raise HTTPException(status_code=404, detail="Analysis not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis results: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Start monitoring endpoint
@app.post("/monitoring/start", response_model=MonitoringResponse)
async def start_monitoring_endpoint(
    request: MonitoringRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key),
    intelligence: EthermaxIntelligence = Depends(get_intelligence)
):
    """Start real-time monitoring for wallets"""
    try:
        monitoring_id = str(uuid.uuid4())

        # Validate wallet addresses
        for wallet in request.wallet_addresses:
            if not wallet.startswith("0x") or len(wallet) != 42:
                raise HTTPException(status_code=400, detail=f"Invalid wallet address format: {wallet}")

        # Start monitoring in background
        async def run_monitoring():
            try:
                logger.info(f"Starting monitoring for {len(request.wallet_addresses)} wallets")

                # Start real-time monitoring
                success = await intelligence.start_real_time_monitoring(
                    wallet_addresses=request.wallet_addresses,
                    alert_thresholds=request.alert_thresholds,
                    notification_channels=request.notification_channels
                )

                if success:
                    background_tasks[monitoring_id] = {
                        "status": "running",
                        "wallets": request.wallet_addresses,
                        "started_at": datetime.now(timezone.utc).isoformat(),
                        "alert_count": 0
                    }
                    logger.info(f"Monitoring started successfully for {monitoring_id}")
                else:
                    logger.error(f"Failed to start monitoring for {monitoring_id}")

            except Exception as e:
                logger.error(f"Monitoring failed: {e}")
                background_tasks[monitoring_id] = {
                    "status": "failed",
                    "error": str(e),
                    "started_at": datetime.now(timezone.utc).isoformat()
                }

        # Add background task
        background_tasks.add_task(run_monitoring)

        return MonitoringResponse(
            success=True,
            message="Monitoring started",
            monitoring_id=monitoring_id,
            wallet_addresses=request.wallet_addresses,
            status="starting"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting monitoring: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Get monitoring status endpoint
@app.get("/monitoring/status/{monitoring_id}", response_model=APIResponse)
async def get_monitoring_status(
    monitoring_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Get status of a monitoring session"""
    try:
        if monitoring_id not in background_tasks:
            raise HTTPException(status_code=404, detail="Monitoring session not found")

        monitoring_data = background_tasks[monitoring_id]

        return APIResponse(
            success=True,
            message="Monitoring status retrieved",
            data=monitoring_data
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting monitoring status: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Stop monitoring endpoint
@app.post("/monitoring/stop/{monitoring_id}", response_model=APIResponse)
async def stop_monitoring(
    monitoring_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Stop a monitoring session"""
    try:
        if monitoring_id not in background_tasks:
            raise HTTPException(status_code=404, detail="Monitoring session not found")

        # Update status
        background_tasks[monitoring_id]["status"] = "stopped"
        background_tasks[monitoring_id]["stopped_at"] = datetime.now(timezone.utc).isoformat()

        return APIResponse(
            success=True,
            message="Monitoring stopped",
            data={"monitoring_id": monitoring_id, "status": "stopped"}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping monitoring: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Generate report endpoint
@app.post("/reports/generate", response_model=APIResponse)
async def generate_report_endpoint(
    request: ReportRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key),
    intelligence: EthermaxIntelligence = Depends(get_intelligence)
):
    """Generate intelligence report for a wallet"""
    try:
        report_id = str(uuid.uuid4())

        # Validate wallet address
        if not request.wallet_address.startswith("0x") or len(request.wallet_address) != 42:
            raise HTTPException(status_code=400, detail="Invalid wallet address format")

        # Generate report in background
        async def generate_report_task():
            try:
                logger.info(f"Generating {request.report_type} report for {request.wallet_address}")

                # Generate report
                report = await intelligence.generate_intelligence_report(
                    wallet_address=request.wallet_address,
                    report_type=request.report_type,
                    format=request.format,
                    include_visualizations=request.include_visualizations
                )

                # Save report
                report_file = intelligence.cache_dir / f"report_{report_id}.{request.format}"

                if request.format == "json":
                    with open(report_file, 'w') as f:
                        json.dump(report, f, indent=2, default=str)
                elif request.format in ["pdf", "html"]:
                    # For non-JSON formats, save as JSON with metadata
                    with open(report_file.with_suffix('.json'), 'w') as f:
                        json.dump(report, f, indent=2, default=str)

                logger.info(f"Report generated successfully for {request.wallet_address}")

            except Exception as e:
                logger.error(f"Report generation failed: {e}")
                # Save error report
                error_file = intelligence.cache_dir / f"report_{report_id}_error.json"
                with open(error_file, 'w') as f:
                    json.dump({
                        "error": str(e),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "wallet_address": request.wallet_address
                    }, f, indent=2)

        # Add background task
        background_tasks.add_task(generate_report_task)

        return APIResponse(
            success=True,
            message="Report generation started",
            data={
                "report_id": report_id,
                "wallet_address": request.wallet_address,
                "report_type": request.report_type,
                "format": request.format
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Get report endpoint
@app.get("/reports/{report_id}")
async def get_report(
    report_id: str,
    format: str = Query("json", description="Report format"),
    api_key: str = Depends(verify_api_key),
    intelligence: EthermaxIntelligence = Depends(get_intelligence)
):
    """Download a generated report"""
    try:
        # Try different file extensions
        possible_files = [
            intelligence.cache_dir / f"report_{report_id}.{format}",
            intelligence.cache_dir / f"report_{report_id}.json",
            intelligence.cache_dir / f"report_{report_id}_error.json"
        ]

        report_file = None
        for file_path in possible_files:
            if file_path.exists():
                report_file = file_path
                break

        if not report_file:
            raise HTTPException(status_code=404, detail="Report not found")

        if report_file.name.endswith("_error.json"):
            # Return error as JSON
            with open(report_file, 'r') as f:
                error_data = json.load(f)
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": "Report generation failed",
                    "error": error_data.get("error", "Unknown error")
                }
            )

        # Return file
        if format == "json":
            with open(report_file, 'r') as f:
                report_data = json.load(f)
            return JSONResponse(content=report_data)
        else:
            return FileResponse(
                path=report_file,
                filename=f"ethermax_report_{report_id}.{format}",
                media_type=f"application/{format}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting report: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Pattern search endpoint
@app.post("/patterns/search", response_model=APIResponse)
async def search_patterns(
    request: PatternSearchRequest,
    api_key: str = Depends(verify_api_key),
    intelligence: EthermaxIntelligence = Depends(get_intelligence)
):
    """Search for specific trading patterns"""
    try:
        # Get recent trade data
        trade_data = await intelligence._get_recent_trades(days=request.time_range_days)

        # Recognize patterns
        all_patterns = await intelligence._recognize_trading_patterns(trade_data)

        # Filter patterns based on request
        filtered_patterns = []

        for pattern in all_patterns:
            # Filter by pattern type
            if request.pattern_types and pattern.pattern_type not in request.pattern_types:
                continue

            # Filter by confidence threshold
            if pattern.confidence_score < request.confidence_threshold:
                continue

            # Filter by risk level
            if request.risk_levels and pattern.risk_level not in request.risk_levels:
                continue

            filtered_patterns.append({
                "pattern_id": pattern.pattern_id,
                "pattern_type": pattern.pattern_type,
                "confidence_score": pattern.confidence_score,
                "risk_level": pattern.risk_level,
                "wallets_involved": pattern.wallets_involved,
                "timestamp": pattern.timestamp.isoformat(),
                "description": pattern.description,
                "features": pattern.features
            })

        return APIResponse(
            success=True,
            message="Pattern search completed",
            data={
                "patterns_found": len(filtered_patterns),
                "search_criteria": {
                    "pattern_types": request.pattern_types,
                    "confidence_threshold": request.confidence_threshold,
                    "risk_levels": request.risk_levels,
                    "time_range_days": request.time_range_days
                },
                "patterns": filtered_patterns
            }
        )

    except Exception as e:
        logger.error(f"Error searching patterns: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# ETHERMAX detection endpoint
@app.get("/intelligence/ethermax/{wallet_address}", response_model=APIResponse)
async def detect_ethermax_endpoint(
    wallet_address: str,
    api_key: str = Depends(verify_api_key),
    intelligence: EthermaxIntelligence = Depends(get_intelligence)
):
    """Detect ETHERMAX patterns for a specific wallet"""
    try:
        # Validate wallet address
        if not wallet_address.startswith("0x") or len(wallet_address) != 42:
            raise HTTPException(status_code=400, detail="Invalid wallet address format")

        # Detect ETHERMAX patterns
        ethermax_analysis = await detect_ethermax_patterns(wallet_address)

        return APIResponse(
            success=True,
            message="ETHERMAX analysis completed",
            data={
                "wallet_address": wallet_address,
                "analysis": ethermax_analysis,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in ETHERMAX detection: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Get recent alerts endpoint
@app.get("/alerts/recent", response_model=APIResponse)
async def get_recent_alerts(
    limit: int = Query(50, description="Maximum number of alerts to return"),
    severity: Optional[str] = Query(None, description="Filter by severity level"),
    api_key: str = Depends(verify_api_key),
    intelligence: EthermaxIntelligence = Depends(get_intelligence)
):
    """Get recent alerts from the system"""
    try:
        # Get alert files
        alert_files = list(intelligence.cache_dir.glob("alert_*.json"))

        # Sort by modification time (newest first)
        alert_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

        alerts = []
        for alert_file in alert_files[:limit]:
            try:
                with open(alert_file, 'r') as f:
                    alert_data = json.load(f)

                # Filter by severity if specified
                if severity and alert_data.get("severity") != severity:
                    continue

                alerts.append(alert_data)

            except Exception as e:
                logger.warning(f"Could not read alert file {alert_file}: {e}")

        return APIResponse(
            success=True,
            message=f"Retrieved {len(alerts)} recent alerts",
            data={
                "alerts": alerts,
                "total_count": len(alerts),
                "severity_filter": severity
            }
        )

    except Exception as e:
        logger.error(f"Error getting recent alerts: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Statistics endpoint
@app.get("/statistics", response_model=APIResponse)
async def get_statistics(
    time_range_days: int = Query(30, description="Time range for statistics"),
    api_key: str = Depends(verify_api_key),
    intelligence: EthermaxIntelligence = Depends(get_intelligence)
):
    """Get system statistics and metrics"""
    try:
        # Get recent trade data
        trade_data = await intelligence._get_recent_trades(days=time_range_days)

        # Calculate statistics
        total_trades = len(trade_data)
        unique_wallets = len(set(trade.get("wallet_address") for trade in trade_data))

        # Pattern statistics
        patterns = await intelligence._recognize_trading_patterns(trade_data)
        pattern_types = {}
        for pattern in patterns:
            pattern_types[pattern.pattern_type] = pattern_types.get(pattern.pattern_type, 0) + 1

        # Risk statistics
        risk_levels = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for pattern in patterns:
            risk_levels[pattern.risk_level] += 1

        # Alert statistics
        alert_files = list(intelligence.cache_dir.glob("alert_*.json"))
        recent_alerts = [f for f in alert_files
                        if (datetime.now(timezone.utc) - datetime.fromtimestamp(f.stat().st_mtime, timezone.utc)).days <= time_range_days]

        statistics = {
            "time_range_days": time_range_days,
            "trading_statistics": {
                "total_trades": total_trades,
                "unique_wallets": unique_wallets,
                "avg_trades_per_wallet": total_trades / max(unique_wallets, 1)
            },
            "pattern_statistics": {
                "total_patterns": len(patterns),
                "pattern_types": pattern_types,
                "risk_distribution": risk_levels
            },
            "alert_statistics": {
                "total_alerts": len(recent_alerts),
                "alerts_per_day": len(recent_alerts) / max(time_range_days, 1)
            },
            "system_statistics": {
                "active_monitoring_sessions": len(background_tasks),
                "cache_directory": str(intelligence.cache_dir),
                "intelligence_initialized": intelligence.is_initialized
            }
        }

        return APIResponse(
            success=True,
            message="Statistics retrieved successfully",
            data=statistics
        )

    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error_code": exc.status_code,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error": str(exc),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

# Main function to run the API
def run_api(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Run the ETHERMAX Intelligence API"""
    uvicorn.run(
        "ethermax_intelligence_api:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    run_api()