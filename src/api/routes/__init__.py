"""
API路由模块
"""
from fastapi import APIRouter

from src.api.routes import health, strategies, backtest, monitoring
