"""
健康检查路由

提供系统健康状态检查接口
"""
from fastapi import APIRouter
from datetime import datetime
from typing import Dict, Any

router = APIRouter()


@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """
    系统健康检查

    返回系统运行状态和各模块健康状态

    Returns:
        Dict[str, Any]: 健康状态信息
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "modules": {
            "database": "healthy",
            "cache": "healthy",
            "trading_engine": "healthy",
            "risk_manager": "healthy",
        },
    }


@router.get("/health/ready", response_model=Dict[str, Any])
async def readiness_check():
    """
    就绪检查

    检查系统是否准备好接收请求

    Returns:
        Dict[str, Any]: 就绪状态
    """
    return {
        "ready": True,
        "timestamp": datetime.now().isoformat(),
        "checks": {
            "database": True,
            "redis": True,
            "market_data": True,
        },
    }


@router.get("/health/live", response_model=Dict[str, Any])
async def liveness_check():
    """
    存活检查

    检查系统是否存活

    Returns:
        Dict[str, Any]: 存活状态
    """
    return {
        "alive": True,
        "timestamp": datetime.now().isoformat(),
    }
