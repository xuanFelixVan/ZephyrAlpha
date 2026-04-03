---
document_type: P1级风险缓解方案设计
version: 1.0.0
created_date: 2026-04-02
owner: 首席技术评审官
standard_type: 专业量化机构风险管理
compliance_level: 专业标准
status: 待实施
applicable_scope: 系统实施
parent_document: ../INDEX.md
implementation_status: 设计阶段
module_id: IMP_P1_RISK_MITIGATION_D
last_updated: 2026-04-02
---

# P1级风险缓解方案设计文档

> **创建日期**: 2026-04-02
> **风险等级**: P1 (高)
> **风险数量**: 18个
> **处理原则**: 开发前设计方案，开发阶段实施

---

## 1. P1级风险清单

### 1.1 外部API依赖风险（12个）

| 风险ID | 风险描述 | 涉及模块 | 影响范围 |
|--------|----------|----------|----------|
| **R-LLM-001** | GLM-4-Flash API调用失败 | DailyReporter, MonthlyReporter, MarketAnalyzer | AI报告生成失败 |
| **R-LLM-002** | GLM-4-Flash API超时 | DailyReporter, MonthlyReporter, MarketAnalyzer | 报告生成延迟 |
| **R-LLM-003** | GLM-4-Flash API成本超支 | 所有LLM集成模块 | 成本控制失效 |
| **R-QMT-001** | QMT客户端连接失败 | QMTDataInterface, QMTExecutor | 数据获取失败、交易执行失败 |
| **R-QMT-002** | QMT API响应超时 | QMTDataInterface, QMTExecutor | 数据延迟、交易延迟 |
| **R-IFIND-001** | iFind数据源不可用 | iFindConnector | 因子数据缺失 |
| **R-IFIND-002** | iFind API限流 | iFindConnector | 数据获取受限 |
| **R-NEWS-001** | 新闻爬虫被封禁 | NewsCrawler | 舆情数据缺失 |
| **R-NEWS-002** | 新闻API不可用 | NewsCrawler | 舆情数据缺失 |
| **R-DINGTALK-001** | 钉钉API不可用 | NotificationSystem | 通知发送失败 |
| **R-WECHAT-001** | 企业微信API不可用 | NotificationSystem | 通知发送失败 |
| **R-SMS-001** | 短信API不可用 | NotificationSystem | 通知发送失败 |

### 1.2 数据源不可用风险（6个）

| 风险ID | 风险描述 | 涉及模块 | 影响范围 |
|--------|----------|----------|----------|
| **R-DATA-001** | 上游数据源不可用 | 所有Layer 0模块 | 数据获取失败 |
| **R-DATA-002** | 数据库连接失败 | DataStorage, PositionManager | 数据持久化失败 |
| **R-DATA-003** | 缓存服务不可用 | 所有缓存模块 | 性能下降 |
| **R-DATA-004** | 数据质量异常 | DataValidator, DataCleaner | 数据错误 |
| **R-DATA-005** | 数据延迟过高 | 所有实时数据模块 | 实时性下降 |
| **R-DATA-006** | 数据存储空间不足 | DataStorage, TradeAuditor | 数据保存失败 |

---

## 2. 缓解方案设计

### 2.1 LLM API依赖风险缓解方案

#### 方案概述

**核心策略**: 降级方案 + 重试机制 + 成本控制 + 多模型备份

#### 2.1.1 降级方案设计

```python
class LLMFallbackStrategy:
    """LLM降级策略
    
    索引: RISK.LLM.FALLBACK.001
    """
    
    def __init__(self):
        self.strategies = [
            self._primary_llm,      # 主LLM (GLM-4-Flash)
            self._backup_llm,       # 备用LLM (GPT-3.5-Turbo)
            self._template_fallback, # 模板降级
            self._cache_fallback    # 缓存降级
        ]
        self.current_strategy = 0
        
    async def generate_with_fallback(
        self,
        prompt: str,
        context: Dict[str, Any]
    ) -> str:
        """带降级的生成
        
        降级顺序:
        1. 主LLM (GLM-4-Flash)
        2. 备用LLM (GPT-3.5-Turbo)
        3. 模板降级 (预定义模板)
        4. 缓存降级 (历史缓存)
        """
        for strategy in self.strategies:
            try:
                result = await strategy(prompt, context)
                if result:
                    return result
            except Exception as e:
                logger.warning(f"策略失败: {strategy.__name__}, 错误: {e}")
                continue
        
        raise LLMFallbackError("所有降级策略失败")
    
    async def _primary_llm(self, prompt: str, context: Dict) -> str:
        """主LLM: GLM-4-Flash"""
        return await self._call_glm4_flash(prompt, context)
    
    async def _backup_llm(self, prompt: str, context: Dict) -> str:
        """备用LLM: GPT-3.5-Turbo"""
        return await self._call_gpt35_turbo(prompt, context)
    
    async def _template_fallback(self, prompt: str, context: Dict) -> str:
        """模板降级: 使用预定义模板"""
        template = self._get_template(context['report_type'])
        return template.render(context)
    
    async def _cache_fallback(self, prompt: str, context: Dict) -> str:
        """缓存降级: 使用历史缓存"""
        cache_key = self._generate_cache_key(prompt, context)
        return await self._get_from_cache(cache_key)
```

#### 2.1.2 重试机制设计

```python
class RetryStrategy:
    """重试策略
    
    索引: RISK.LLM.RETRY.001
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
        exponential_base: float = 2.0
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        
    async def execute_with_retry(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """带重试的执行
        
        重试策略:
        - 最多重试3次
        - 指数退避: 1s, 2s, 4s
        - 最大延迟30秒
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    delay = min(
                        self.base_delay * (self.exponential_base ** attempt),
                        self.max_delay
                    )
                    logger.warning(
                        f"第{attempt + 1}次重试失败，{delay}秒后重试: {e}"
                    )
                    await asyncio.sleep(delay)
        
        raise last_exception
```

#### 2.1.3 成本控制设计

```python
class CostController:
    """成本控制器
    
    索引: RISK.LLM.COST.001
    """
    
    def __init__(
        self,
        daily_budget: float = 100.0,  # 日预算100元
        monthly_budget: float = 2000.0,  # 月预算2000元
        alert_threshold: float = 0.8  # 80%告警
    ):
        self.daily_budget = daily_budget
        self.monthly_budget = monthly_budget
        self.alert_threshold = alert_threshold
        self.daily_cost = 0.0
        self.monthly_cost = 0.0
        
    async def check_budget(self, estimated_cost: float) -> bool:
        """检查预算
        
        返回:
            bool: 是否在预算范围内
        """
        if self.daily_cost + estimated_cost > self.daily_budget:
            logger.error(f"日预算超支: 当前{self.daily_cost}, 预算{self.daily_budget}")
            return False
            
        if self.monthly_cost + estimated_cost > self.monthly_budget:
            logger.error(f"月预算超支: 当前{self.monthly_cost}, 预算{self.monthly_budget}")
            return False
            
        return True
    
    async def record_cost(self, actual_cost: float):
        """记录成本"""
        self.daily_cost += actual_cost
        self.monthly_cost += actual_cost
        
        # 检查告警阈值
        if self.daily_cost > self.daily_budget * self.alert_threshold:
            await self._send_alert("日预算即将超支")
        if self.monthly_cost > self.monthly_budget * self.alert_threshold:
            await self._send_alert("月预算即将超支")
```

#### 2.1.4 Token优化设计

```python
class TokenOptimizer:
    """Token优化器
    
    索引: RISK.LLM.TOKEN.001
    """
    
    def __init__(self, max_tokens: int = 2000):
        self.max_tokens = max_tokens
        
    def optimize_prompt(self, prompt: str, context: Dict) -> str:
        """优化Prompt
        
        优化策略:
        1. 移除冗余信息
        2. 压缩数据格式
        3. 使用缩写
        """
        # 移除冗余空白
        prompt = ' '.join(prompt.split())
        
        # 压缩数据格式
        if 'data' in context:
            context['data'] = self._compress_data(context['data'])
        
        # 限制数据量
        if len(str(context)) > self.max_tokens:
            context = self._truncate_context(context, self.max_tokens)
        
        return prompt.format(**context)
    
    def _compress_data(self, data: Any) -> str:
        """压缩数据"""
        if isinstance(data, pd.DataFrame):
            return data.to_json(orient='records', double_precision=2)
        return str(data)
```

---

### 2.2 QMT API依赖风险缓解方案

#### 方案概述

**核心策略**: 连接池 + 心跳检测 + 自动重连 + 降级方案

#### 2.2.1 连接池管理

```python
class QMTConnectionPool:
    """QMT连接池
    
    索引: RISK.QMT.POOL.001
    """
    
    def __init__(
        self,
        pool_size: int = 5,
        heartbeat_interval: int = 30,
        max_idle_time: int = 300
    ):
        self.pool_size = pool_size
        self.heartbeat_interval = heartbeat_interval
        self.max_idle_time = max_idle_time
        self.pool = []
        self.active_connections = {}
        
    async def get_connection(self) -> QMTConnection:
        """获取连接"""
        # 检查连接池
        if self.pool:
            conn = self.pool.pop()
            if await self._check_connection(conn):
                return conn
        
        # 创建新连接
        conn = await self._create_connection()
        return conn
    
    async def _check_connection(self, conn: QMTConnection) -> bool:
        """检查连接有效性"""
        try:
            await conn.ping()
            return True
        except:
            return False
    
    async def _create_connection(self) -> QMTConnection:
        """创建新连接"""
        conn = QMTConnection()
        await conn.connect()
        self._start_heartbeat(conn)
        return conn
```

#### 2.2.2 自动重连机制

```python
class QMTReconnectStrategy:
    """QMT自动重连策略
    
    索引: RISK.QMT.RECONNECT.001
    """
    
    def __init__(
        self,
        max_retries: int = 5,
        retry_delay: float = 5.0,
        backoff_factor: float = 2.0
    ):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.backoff_factor = backoff_factor
        
    async def execute_with_reconnect(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """带重连的执行"""
        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
            except QMTConnectionError as e:
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (self.backoff_factor ** attempt)
                    logger.warning(f"QMT连接失败，{delay}秒后重连: {e}")
                    await asyncio.sleep(delay)
                    await self._reconnect()
                else:
                    raise
```

#### 2.2.3 降级方案

```python
class QMTFallbackStrategy:
    """QMT降级策略
    
    索引: RISK.QMT.FALLBACK.001
    """
    
    async def get_data_with_fallback(
        self,
        data_type: str,
        params: Dict
    ) -> pd.DataFrame:
        """带降级的数据获取
        
        降级顺序:
        1. QMT实时数据
        2. 本地缓存数据
        3. Baostock历史数据
        """
        try:
            # 尝试QMT实时数据
            return await self._get_from_qmt(data_type, params)
        except:
            pass
        
        try:
            # 尝试本地缓存
            return await self._get_from_cache(data_type, params)
        except:
            pass
        
        try:
            # 尝试Baostock历史数据
            return await self._get_from_baostock(data_type, params)
        except:
            raise DataFallbackError("所有数据源降级失败")
```

---

### 2.3 数据源不可用风险缓解方案

#### 方案概述

**核心策略**: 数据缓存 + 多源备份 + 健康检查 + 降级方案

#### 2.3.1 数据缓存机制

```python
class DataCacheManager:
    """数据缓存管理器
    
    索引: RISK.DATA.CACHE.001
    """
    
    def __init__(
        self,
        cache_ttl: int = 600,  # 缓存有效期10分钟
        max_cache_size: int = 1000  # 最大缓存数量
    ):
        self.cache_ttl = cache_ttl
        self.max_cache_size = max_cache_size
        self.cache = {}
        self.timestamps = {}
        
    async def get_or_fetch(
        self,
        key: str,
        fetch_func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """获取或拉取数据"""
        # 检查缓存
        if key in self.cache:
            timestamp = self.timestamps[key]
            if time.time() - timestamp < self.cache_ttl:
                return self.cache[key]
        
        # 拉取新数据
        data = await fetch_func(*args, **kwargs)
        
        # 更新缓存
        self.cache[key] = data
        self.timestamps[key] = time.time()
        
        # 清理过期缓存
        await self._cleanup_cache()
        
        return data
```

#### 2.3.2 多源备份机制

```python
class MultiSourceDataManager:
    """多源数据管理器
    
    索引: RISK.DATA.MULTI.001
    """
    
    def __init__(self):
        self.sources = {
            'primary': ['qmt', 'ifind'],
            'secondary': ['baostock', 'tushare'],
            'tertiary': ['local_cache', 'backup_db']
        }
        
    async def get_data(
        self,
        data_type: str,
        params: Dict
    ) -> pd.DataFrame:
        """获取数据（多源备份）"""
        for priority, sources in self.sources.items():
            for source in sources:
                try:
                    data = await self._fetch_from_source(
                        source, data_type, params
                    )
                    if data is not None and not data.empty:
                        return data
                except Exception as e:
                    logger.warning(f"数据源{source}失败: {e}")
                    continue
        
        raise DataSourceError("所有数据源不可用")
```

#### 2.3.3 健康检查机制

```python
class HealthChecker:
    """健康检查器
    
    索引: RISK.DATA.HEALTH.001
    """
    
    def __init__(
        self,
        check_interval: int = 60,  # 检查间隔60秒
        timeout: int = 10  # 超时时间10秒
    ):
        self.check_interval = check_interval
        self.timeout = timeout
        self.health_status = {}
        
    async def check_all_sources(self) -> Dict[str, bool]:
        """检查所有数据源健康状态"""
        tasks = []
        for source in self._get_all_sources():
            tasks.append(self._check_source(source))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for source, result in zip(self._get_all_sources(), results):
            self.health_status[source] = not isinstance(result, Exception)
        
        return self.health_status
    
    async def _check_source(self, source: str) -> bool:
        """检查单个数据源"""
        try:
            async with asyncio.timeout(self.timeout):
                return await self._ping_source(source)
        except:
            return False
```

---

## 3. 实施计划

### 3.1 开发前准备（必须完成）

| 任务 | 工时 | 负责人 | 完成标准 |
|------|------|--------|----------|
| **LLM降级方案设计** | 4小时 | 架构师 | 设计文档完成 |
| **QMT连接池设计** | 3小时 | 架构师 | 设计文档完成 |
| **数据缓存机制设计** | 3小时 | 架构师 | 设计文档完成 |
| **监控告警方案设计** | 2小时 | 架构师 | 设计文档完成 |

**总计**: 12小时（1.5天）

### 3.2 开发阶段实施

| 阶段 | 任务 | 工时 | 优先级 |
|------|------|------|--------|
| **Phase 1** | 实现LLM降级方案 | 8小时 | P1 |
| **Phase 1** | 实现QMT连接池 | 6小时 | P1 |
| **Phase 1** | 实现数据缓存机制 | 6小时 | P1 |
| **Phase 2** | 实现监控告警 | 4小时 | P1 |
| **Phase 2** | 实现健康检查 | 4小时 | P1 |

**总计**: 28小时（3.5天）

### 3.3 测试验证

| 测试项 | 工时 | 验收标准 |
|--------|------|----------|
| **降级方案测试** | 4小时 | 所有降级路径可用 |
| **重连机制测试** | 2小时 | 自动重连成功率≥95% |
| **缓存机制测试** | 2小时 | 缓存命中率≥80% |
| **监控告警测试** | 2小时 | 告警触发准确率100% |

**总计**: 10小时（1.25天）

---

## 4. 验收标准

### 4.1 LLM API风险缓解

| 指标 | 目标值 | 验证方法 |
|------|--------|----------|
| **降级成功率** | ≥95% | 模拟API失败测试 |
| **重试成功率** | ≥90% | 模拟网络故障测试 |
| **成本控制准确率** | 100% | 成本监控测试 |
| **Token优化率** | ≥20% | Token消耗对比测试 |

### 4.2 QMT API风险缓解

| 指标 | 目标值 | 验证方法 |
|------|--------|----------|
| **连接成功率** | ≥98% | 连接测试 |
| **自动重连成功率** | ≥95% | 断线重连测试 |
| **降级成功率** | ≥90% | 模拟故障测试 |

### 4.3 数据源风险缓解

| 指标 | 目标值 | 验证方法 |
|------|--------|----------|
| **数据获取成功率** | ≥98% | 数据获取测试 |
| **缓存命中率** | ≥80% | 缓存测试 |
| **健康检查准确率** | 100% | 健康检查测试 |

---

## 5. 监控指标

### 5.1 实时监控

| 监控项 | 告警阈值 | 告警级别 |
|--------|----------|----------|
| **LLM API成功率** | <90% | P1 |
| **LLM成本超支** | >预算80% | P2 |
| **QMT连接成功率** | <95% | P1 |
| **数据获取成功率** | <95% | P1 |
| **缓存命中率** | <70% | P2 |

### 5.2 日志记录

```python
class RiskMonitorLogger:
    """风险监控日志
    
    索引: RISK.MONITOR.LOG.001
    """
    
    @staticmethod
    def log_risk_event(
        risk_id: str,
        event_type: str,
        severity: str,
        details: Dict[str, Any]
    ):
        """记录风险事件"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'risk_id': risk_id,
            'event_type': event_type,
            'severity': severity,
            'details': details
        }
        
        logger.warning(f"风险事件: {json.dumps(log_entry, ensure_ascii=False)}")
        
        # 发送告警
        if severity in ['P0', 'P1']:
            AlertManager.send_alert(log_entry)
```

---

## 6. 总结

### 6.1 关键要点

1. ✅ **P1级风险不需要开发前全部修复**
2. ✅ **开发前需要完成缓解方案设计**
3. ✅ **开发阶段实施缓解方案**
4. ✅ **建立监控告警机制**

### 6.2 实施建议

1. **立即行动**: 完成缓解方案设计（1.5天）
2. **开发阶段**: 实施缓解方案（3.5天）
3. **测试阶段**: 验证缓解效果（1.25天）
4. **上线后**: 持续监控优化

---

**文档状态**: ✅ 已完成
**下一步**: 开始缓解方案设计
