"""
策略管理路由

提供策略的CRUD操作接口
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

router = APIRouter()


class StrategyBase(BaseModel):
    """策略基础模型"""
    name: str = Field(..., description="策略名称")
    description: Optional[str] = Field(None, description="策略描述")
    strategy_type: str = Field(..., description="策略类型")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="策略参数")
    enabled: bool = Field(default=True, description="是否启用")


class StrategyCreate(StrategyBase):
    """策略创建模型"""
    pass


class StrategyUpdate(BaseModel):
    """策略更新模型"""
    name: Optional[str] = None
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None


class StrategyResponse(StrategyBase):
    """策略响应模型"""
    id: str = Field(..., description="策略ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    status: str = Field(default="created", description="策略状态")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "strategy_001",
                "name": "双均线策略",
                "description": "基于双均线的趋势跟踪策略",
                "strategy_type": "trend_following",
                "parameters": {
                    "short_window": 20,
                    "long_window": 60
                },
                "enabled": True,
                "created_at": "2026-04-05T10:00:00",
                "updated_at": "2026-04-05T10:00:00",
                "status": "running"
            }
        }


@router.get("/", response_model=List[StrategyResponse])
async def list_strategies(
    skip: int = 0,
    limit: int = 100,
    strategy_type: Optional[str] = None,
    enabled: Optional[bool] = None,
):
    """
    获取策略列表
    
    支持分页和过滤
    
    Args:
        skip: 跳过记录数
        limit: 返回记录数
        strategy_type: 策略类型过滤
        enabled: 启用状态过滤
    
    Returns:
        List[StrategyResponse]: 策略列表
    """
    strategies = [
        StrategyResponse(
            id="strategy_001",
            name="双均线策略",
            description="基于双均线的趋势跟踪策略",
            strategy_type="trend_following",
            parameters={"short_window": 20, "long_window": 60},
            enabled=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            status="running",
        ),
        StrategyResponse(
            id="strategy_002",
            name="动量策略",
            description="基于动量因子的策略",
            strategy_type="momentum",
            parameters={"lookback": 20, "threshold": 0.05},
            enabled=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            status="running",
        ),
    ]
    
    return strategies[skip:skip+limit]


@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(strategy_id: str):
    """
    获取单个策略详情
    
    Args:
        strategy_id: 策略ID
    
    Returns:
        StrategyResponse: 策略详情
    
    Raises:
        HTTPException: 策略不存在
    """
    if strategy_id != "strategy_001":
        raise HTTPException(status_code=404, detail="策略不存在")
    
    return StrategyResponse(
        id=strategy_id,
        name="双均线策略",
        description="基于双均线的趋势跟踪策略",
        strategy_type="trend_following",
        parameters={"short_window": 20, "long_window": 60},
        enabled=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        status="running",
    )


@router.post("/", response_model=StrategyResponse, status_code=201)
async def create_strategy(strategy: StrategyCreate):
    """
    创建新策略
    
    Args:
        strategy: 策略创建参数
    
    Returns:
        StrategyResponse: 创建的策略
    """
    return StrategyResponse(
        id="strategy_new",
        name=strategy.name,
        description=strategy.description,
        strategy_type=strategy.strategy_type,
        parameters=strategy.parameters,
        enabled=strategy.enabled,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        status="created",
    )


@router.put("/{strategy_id}", response_model=StrategyResponse)
async def update_strategy(strategy_id: str, strategy: StrategyUpdate):
    """
    更新策略
    
    Args:
        strategy_id: 策略ID
        strategy: 策略更新参数
    
    Returns:
        StrategyResponse: 更新后的策略
    
    Raises:
        HTTPException: 策略不存在
    """
    if strategy_id != "strategy_001":
        raise HTTPException(status_code=404, detail="策略不存在")
    
    return StrategyResponse(
        id=strategy_id,
        name=strategy.name or "双均线策略",
        description=strategy.description or "基于双均线的趋势跟踪策略",
        strategy_type="trend_following",
        parameters=strategy.parameters or {"short_window": 20, "long_window": 60},
        enabled=strategy.enabled if strategy.enabled is not None else True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        status="updated",
    )


@router.delete("/{strategy_id}", status_code=204)
async def delete_strategy(strategy_id: str):
    """
    删除策略
    
    Args:
        strategy_id: 策略ID
    
    Raises:
        HTTPException: 策略不存在
    """
    if strategy_id != "strategy_001":
        raise HTTPException(status_code=404, detail="策略不存在")
    
    return None
