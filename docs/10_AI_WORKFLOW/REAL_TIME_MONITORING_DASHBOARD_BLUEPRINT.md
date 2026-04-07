---
module_id: AIWF_RMD_001
version: 1.0.0
status: Active
created_date: 2026-04-05
last_updated: 2026-04-05
owner: 首席架构师
standard_type: 专业机构级蓝图
applicable_scope: 实时监控仪表盘模块
compliance_level: 专业标准
parent_document: INDEX.md
layer: Layer 3 (舆情分析层)
priority: P0
estimated_effort: 30h
responsibility:
  - 蓝图设计、架构规划

---
---


## 文档职责说明

**本文档职责**: 实时监控仪表盘模块蓝图
- 舆情热力图、情感趋势图、预警时间线

**📌 职责边界说明**:
- **本文档**: 舆情专用仪表盘模块，负责舆情数据可视化展示
- **REAL_TIME_RISK_MONITOR**: 系统级核心风险监控，负责全系统风险评估
- **LIVE_TRADING_MONITOR**: 实盘交易专用监控，负责交易层面的监控
- **REAL_TIME_ALERT_SYSTEM**: 舆情专用预警模块，负责舆情预警

**职责关系**:
```
统一告警平台（上游）
    ├── REAL_TIME_RISK_MONITOR（系统级风险监控）
    ├── LIVE_TRADING_MONITOR（实盘交易监控）
    ├── REAL_TIME_ALERT_SYSTEM（舆情预警）
    └── REAL_TIME_MONITORING_DASHBOARD（本模块：舆情仪表盘）
```

# 实时监控仪表盘模块蓝图 (Real-time Monitoring Dashboard Blueprint)

> **核心职责**: 蓝图设计和架构规划
> **职责边界**: 
> - ✅ 本文档负责：蓝图设计和架构规划相关内容
> - ❌ 本文档不负责：其他模块内容


> **模块ID**: AIWF_RMD_001
> **版本**: v1.0
> **创建日期**: 2026-04-05
> **Layer定位**: 舆情分析层
> **优先级**: P0 (阻断性)
> **预计工作量**: 30小时

---

## 一、模块概述

### 1.1 设计背景

**业务需求**:
- 提供实时舆情监控可视化界面
- 支持多维度舆情数据展示（热力图、趋势图、时间线）
- 实现预警事件的实时推送和展示
- 支持数据源和模型性能的实时监控

**技术痛点**:
- 当前缺少可视化的监控界面
- 缺少实时数据展示能力
- 缺少多维度数据对比视图
- 缺少移动端支持

**预期价值**:
- 监控效率提升80%
- 预警响应时间缩短50%
- 数据可视化覆盖率100%
- 移动端可用性提升

### 1.2 模块定位

**Layer归属**: 舆情分析层
**模块类别**: 可视化模块
**架构角色**: 监控展示层，为运维和决策提供可视化支持

---

## 二、详细架构设计

### 2.1 系统架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                    实时监控仪表盘模块架构                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │         Frontend Layer (前端展示层)                           │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │   │
│  │  │舆情热力图│ │情感趋势图│ │预警时间线│ │对比视图  │        │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘        │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │   │
│  │  │数据源监控│ │模型监控  │ │用户交互  │ │移动端适配│        │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘        │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                          ↓                                           │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │         API Gateway Layer (API网关层)                         │   │
│  │  - RESTful API                                                │   │
│  │  - WebSocket实时推送                                          │   │
│  │  - 认证与授权                                                 │   │
│  │  - 限流与缓存                                                 │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                          ↓                                           │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │         Data Aggregation Layer (数据聚合层)                   │   │
│  │  - 实时数据聚合                                               │   │
│  │  - 历史数据查询                                               │   │
│  │  - 数据缓存                                                   │   │
│  │  - 数据预处理                                                 │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                          ↓                                           │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │         Data Source Layer (数据源层)                          │   │
│  │  - 舆情数据库                                                 │   │
│  │  - 因子数据库                                                 │   │
│  │  - 预警数据库                                                 │   │
│  │  - 监控指标库                                                 │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 核心组件设计

#### 2.2.1 舆情热力图组件 (SentimentHeatmap)

**功能**:
- 实时展示不同资产/行业的舆情热度
- 使用颜色深浅表示舆情强度
- 支持点击钻取查看详情

**设计要点**:

```typescript
interface HeatmapConfig {
  dataSource: 'twitter' | 'reddit' | 'news' | 'all';
  aggregationLevel: 'asset' | 'sector' | 'market';
  colorScale: 'RdYlGn' | 'Viridis' | 'Custom';
  updateInterval: number; // seconds
  enableDrillDown: boolean;
}

class SentimentHeatmap {
  private config: HeatmapConfig;
  private data: Map<string, SentimentData>;
  
  constructor(config: HeatmapConfig) {
    this.config = config;
  }
  
  async updateData(): Promise<void> {
    const response = await fetch('/api/sentiment/heatmap', {
      method: 'POST',
      body: JSON.stringify({
        dataSource: this.config.dataSource,
        aggregationLevel: this.config.aggregationLevel
      })
    });
    
    this.data = await response.json();
    this.render();
  }
  
  render(): void {
    // 使用Plotly或D3.js渲染热力图
    Plotly.newPlot('heatmap-container', this.prepareData(), this.getLayout());
  }
  
  onCellClick(asset: string): void {
    // 钻取查看详情
    this.showDetail(asset);
  }
}
```

**API设计**:

```python
@app.post('/api/sentiment/heatmap')
async def get_sentiment_heatmap(request: HeatmapRequest):
    """获取舆情热力图数据"""
    # 查询舆情数据
    sentiment_data = await db.query("""
        SELECT 
            asset_symbol,
            AVG(sentiment_score) as avg_sentiment,
            COUNT(*) as mention_count
        FROM sentiment_data
        WHERE timestamp > NOW() - INTERVAL '1 hour'
        AND data_source = %s
        GROUP BY asset_symbol
    """, (request.dataSource,))
    
    # 聚合数据
    if request.aggregationLevel == 'sector':
        sentiment_data = aggregate_by_sector(sentiment_data)
    
    return {
        'data': sentiment_data,
        'timestamp': datetime.now()
    }
```

#### 2.2.2 情感趋势图组件 (SentimentTrendChart)

**功能**:
- 展示情感得分的时间序列趋势
- 支持多资产对比
- 支持不同时间粒度（分钟、小时、天）

**设计要点**:

```typescript
interface TrendChartConfig {
  assets: string[];
  timeRange: '1h' | '6h' | '24h' | '7d' | '30d';
  granularity: 'minute' | 'hour' | 'day';
  showVolume: boolean;
  showMovingAverage: boolean;
}

class SentimentTrendChart {
  private config: TrendChartConfig;
  private chart: PlotlyChart;
  
  async updateData(): Promise<void> {
    const response = await fetch('/api/sentiment/trend', {
      method: 'POST',
      body: JSON.stringify(this.config)
    });
    
    const data = await response.json();
    this.render(data);
  }
  
  render(data: TrendData): void {
    const traces = this.config.assets.map(asset => ({
      x: data.timestamps,
      y: data.sentiments[asset],
      name: asset,
      type: 'scatter',
      mode: 'lines'
    }));
    
    Plotly.newPlot('trend-chart', traces, this.getLayout());
  }
}
```

#### 2.2.3 预警事件时间线组件 (AlertTimeline)

**功能**:
- 实时展示预警事件
- 支持事件筛选和搜索
- 支持事件详情查看

**设计要点**:

```typescript
interface AlertTimelineConfig {
  severity: ('P0' | 'P1' | 'P2' | 'P3')[];
  eventTypes: string[];
  timeRange: '1h' | '6h' | '24h' | '7d';
  autoRefresh: boolean;
}

class AlertTimeline {
  private config: AlertTimelineConfig;
  private alerts: Alert[];
  private ws: WebSocket;
  
  constructor(config: AlertTimelineConfig) {
    this.config = config;
    this.connectWebSocket();
  }
  
  connectWebSocket(): void {
    this.ws = new WebSocket('ws://localhost:8000/ws/alerts');
    
    this.ws.onmessage = (event) => {
      const alert = JSON.parse(event.data);
      this.addAlert(alert);
    };
  }
  
  addAlert(alert: Alert): void {
    this.alerts.unshift(alert);
    this.render();
  }
  
  render(): void {
    const container = document.getElementById('alert-timeline');
    container.innerHTML = this.alerts.map(alert => `
      <div class="alert-item severity-${alert.severity}">
        <div class="alert-time">${formatTime(alert.timestamp)}</div>
        <div class="alert-title">${alert.title}</div>
        <div class="alert-description">${alert.description}</div>
      </div>
    `).join('');
  }
}
```

**WebSocket推送设计**:

```python
@app.websocket('/ws/alerts')
async def alert_websocket(websocket: WebSocket):
    """预警事件WebSocket推送"""
    await websocket.accept()
    
    try:
        while True:
            # 等待新预警事件
            alert = await alert_queue.get()
            
            # 推送给客户端
            await websocket.send_json(alert)
    except WebSocketDisconnect:
        pass
```

#### 2.2.4 多维度对比视图组件 (ComparisonView)

**功能**:
- 支持多资产舆情对比
- 支持多数据源对比
- 支持多时间维度对比

**设计要点**:

```typescript
interface ComparisonConfig {
  compareType: 'asset' | 'source' | 'time';
  items: string[];
  metrics: ('sentiment' | 'volume' | 'impact')[];
  chartType: 'line' | 'bar' | 'radar';
}

class ComparisonView {
  private config: ComparisonConfig;
  
  async loadData(): Promise<void> {
    const response = await fetch('/api/sentiment/compare', {
      method: 'POST',
      body: JSON.stringify(this.config)
    });
    
    const data = await response.json();
    this.render(data);
  }
  
  render(data: ComparisonData): void {
    // 根据chartType选择不同的渲染方式
    switch (this.config.chartType) {
      case 'line':
        this.renderLineChart(data);
        break;
      case 'bar':
        this.renderBarChart(data);
        break;
      case 'radar':
        this.renderRadarChart(data);
        break;
    }
  }
}
```

#### 2.2.5 数据源健康监控面板 (DataSourceHealthPanel)

**功能**:
- 实时监控数据源可用性
- 监控数据源响应时间
- 监控数据源错误率
- 支持告警通知

**设计要点**:

```typescript
interface DataSourceHealth {
  source: string;
  status: 'healthy' | 'degraded' | 'down';
  responseTime: number; // ms
  errorRate: number; // percentage
  lastUpdate: Date;
  dailyVolume: number;
}

class DataSourceHealthPanel {
  private healthData: Map<string, DataSourceHealth>;
  
  async updateHealth(): Promise<void> {
    const response = await fetch('/api/monitor/datasource-health');
    this.healthData = await response.json();
    this.render();
  }
  
  render(): void {
    const container = document.getElementById('datasource-health');
    container.innerHTML = Array.from(this.healthData.entries()).map(([source, health]) => `
      <div class="health-item status-${health.status}">
        <div class="source-name">${source}</div>
        <div class="status-indicator ${health.status}"></div>
        <div class="metrics">
          <div>响应时间: ${health.responseTime}ms</div>
          <div>错误率: ${health.errorRate}%</div>
          <div>日采集量: ${formatNumber(health.dailyVolume)}</div>
        </div>
      </div>
    `).join('');
  }
}
```

#### 2.2.6 模型性能监控面板 (ModelPerformancePanel)

**功能**:
- 监控模型预测准确率
- 监控模型推理延迟
- 监控模型资源使用
- 支持模型版本管理

**设计要点**:

```typescript
interface ModelPerformance {
  modelName: string;
  version: string;
  accuracy: number;
  latency: number; // ms
  throughput: number; // requests/second
  cpuUsage: number; // percentage
  memoryUsage: number; // percentage
  lastUpdated: Date;
}

class ModelPerformancePanel {
  private performanceData: Map<string, ModelPerformance>;
  
  async updatePerformance(): Promise<void> {
    const response = await fetch('/api/monitor/model-performance');
    this.performanceData = await response.json();
    this.render();
  }
  
  render(): void {
    const container = document.getElementById('model-performance');
    container.innerHTML = Array.from(this.performanceData.entries()).map(([model, perf]) => `
      <div class="performance-item">
        <div class="model-name">${model} (v${perf.version})</div>
        <div class="metrics">
          <div>准确率: ${(perf.accuracy * 100).toFixed(2)}%</div>
          <div>延迟: ${perf.latency}ms</div>
          <div>吞吐量: ${perf.throughput} req/s</div>
          <div>CPU: ${perf.cpuUsage}%</div>
          <div>内存: ${perf.memoryUsage}%</div>
        </div>
      </div>
    `).join('');
  }
}
```

#### 2.2.7 用户交互功能 (UserInteraction)

**功能**:
- 支持数据筛选和过滤
- 支持数据导出
- 支持自定义视图
- 支持告警订阅

**设计要点**:

```typescript
class UserInteraction {
  private filters: Filters;
  private subscriptions: Set<string>;
  
  applyFilters(filters: Filters): void {
    this.filters = filters;
    this.refreshData();
  }
  
  async exportData(format: 'csv' | 'json' | 'excel'): Promise<void> {
    const response = await fetch('/api/export', {
      method: 'POST',
      body: JSON.stringify({
        filters: this.filters,
        format: format
      })
    });
    
    const blob = await response.blob();
    downloadBlob(blob, `sentiment-data.${format}`);
  }
  
  async subscribeAlert(alertType: string): Promise<void> {
    await fetch('/api/alerts/subscribe', {
      method: 'POST',
      body: JSON.stringify({ alertType })
    });
    
    this.subscriptions.add(alertType);
  }
}
```

#### 2.2.8 移动端适配 (MobileAdaptation)

**功能**:
- 响应式布局设计
- 移动端手势支持
- 离线数据缓存
- 推送通知

**设计要点**:

```typescript
class MobileAdaptation {
  private isMobile: boolean;
  private serviceWorker: ServiceWorker;
  
  constructor() {
    this.isMobile = this.detectMobile();
    if (this.isMobile) {
      this.registerServiceWorker();
      this.setupPushNotifications();
    }
  }
  
  detectMobile(): boolean {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
      navigator.userAgent
    );
  }
  
  async registerServiceWorker(): Promise<void> {
    if ('serviceWorker' in navigator) {
      this.serviceWorker = await navigator.serviceWorker.register('/sw.js');
    }
  }
  
  async setupPushNotifications(): Promise<void> {
    const permission = await Notification.requestPermission();
    if (permission === 'granted') {
      // 订阅推送通知
      const subscription = await this.serviceWorker.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY)
      });
      
      await fetch('/api/push/subscribe', {
        method: 'POST',
        body: JSON.stringify(subscription)
      });
    }
  }
}
```

---

## 三、技术选型

### 3.1 开源项目评估

| 项目 | 功能 | Stars | 成熟度 | 推荐度 | 成本 |
|------|------|-------|--------|--------|------|
| **Streamlit** | 快速构建数据应用 | 35k | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 免费 |
| **Grafana** | 专业监控仪表盘 | 63k | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 开源版免费 |
| **Plotly Dash** | 交互式可视化 | 21k | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 免费 |
| **React** | 前端框架 | 226k | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 免费 |
| **Vue.js** | 前端框架 | 208k | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 免费 |

### 3.2 技术栈选择

**前端展示层**:
- React 18 / Vue 3 (前端框架)
- Plotly.js (图表库)
- D3.js (自定义可视化)
- Material-UI / Ant Design (UI组件库)

**API网关层**:
- FastAPI (Python后端)
- WebSocket (实时推送)
- Redis (缓存)
- Nginx (反向代理)

**数据聚合层**:
- Pandas (数据处理)
- TimescaleDB (时序数据)
- PostgreSQL (关系数据)
- Redis (缓存)

### 3.3 成本分析

| 组件 | 计算成本 | 存储成本 | 总成本 |
|------|---------|---------|--------|
| 前端服务 | $50/月 | $10/月 | $60/月 |
| API网关 | $80/月 | $20/月 | $100/月 |
| 数据聚合 | $100/月 | $50/月 | $150/月 |
| WebSocket服务 | $60/月 | $10/月 | $70/月 |
| 监控指标 | $40/月 | $30/月 | $70/月 |
| **总计** | **$330/月** | **$120/月** | **$450/月** |

---

## 四、实施路径

### Phase 1: 核心可视化组件（1周）

**目标**: 完成核心可视化组件开发

**任务清单**:
- [ ] 舆情热力图组件
- [ ] 情感趋势图组件
- [ ] 预警时间线组件
- [ ] 基础API开发

**验收标准**:
- 核心组件可用
- 数据展示正确
- 响应速度 < 2秒

### Phase 2: 监控面板与交互（1周）

**目标**: 完成监控面板和用户交互

**任务清单**:
- [ ] 数据源健康监控面板
- [ ] 模型性能监控面板
- [ ] 用户交互功能
- [ ] WebSocket实时推送

**验收标准**:
- 监控面板可用
- 实时推送可用
- 用户交互流畅

### Phase 3: 移动端与优化（1周）

**目标**: 完成移动端适配和性能优化

**任务清单**:
- [ ] 移动端响应式设计
- [ ] 离线缓存支持
- [ ] 推送通知
- [ ] 性能优化

**验收标准**:
- 移动端可用
- 离线缓存可用
- 推送通知可用
- 性能达标

---

## 五、风险与挑战

### 5.1 技术风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|---------|
| 实时推送延迟 | 高 | 中 | WebSocket优化和缓存 |
| 数据可视化性能 | 中 | 中 | 数据聚合和分页 |
| 移动端兼容性 | 中 | 低 | 响应式设计和测试 |

### 5.2 业务风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|---------|
| 用户需求变化 | 中 | 中 | 模块化设计和快速迭代 |
| 数据质量问题 | 高 | 低 | 数据验证和清洗 |

### 5.3 挑战

1. **实时数据推送**
   - 挑战: 大量客户端并发推送
   - 解决方案: WebSocket连接池和消息队列

2. **数据可视化性能**
   - 挑战: 大数据量渲染卡顿
   - 解决方案: 数据聚合和虚拟滚动

3. **移动端体验**
   - 挑战: 屏幕尺寸限制
   - 解决方案: 响应式设计和手势交互

---

## 六、验收标准

### 6.1 功能验收标准

| 功能 | 验收标准 | 测试方法 |
|------|---------|---------|
| 舆情热力图 | 数据展示正确 | 功能测试 |
| 情感趋势图 | 趋势展示正确 | 功能测试 |
| 预警时间线 | 实时推送可用 | 功能测试 |
| 数据源监控 | 监控数据准确 | 功能测试 |
| 模型监控 | 监控数据准确 | 功能测试 |
| 移动端适配 | 响应式可用 | 兼容性测试 |

### 6.2 性能验收标准

| 指标 | 目标值 | 测试方法 |
|------|--------|---------|
| 页面加载时间 | < 3秒 | 性能测试 |
| 数据刷新延迟 | < 2秒 | 性能测试 |
| WebSocket延迟 | < 1秒 | 性能测试 |
| 移动端响应 | < 5秒 | 性能测试 |

### 6.3 质量验收标准

| 指标 | 目标值 | 测试方法 |
|------|--------|---------|
| 代码覆盖率 | > 70% | 单元测试 |
| 文档完整性 | 100% | 人工审查 |
| 浏览器兼容性 | 主流浏览器 | 兼容性测试 |

---

## 七、依赖关系

### 7.1 上游依赖

| 依赖模块 | 依赖类型 | 说明 |
|---------|---------|------|
| 数据源扩展模块 | 数据依赖 | 提供数据源健康数据 |
| 深度学习情感分析模块 | 数据依赖 | 提供情感分析数据 |
| 实时预警系统模块 | 数据依赖 | 提供预警事件数据 |
| 舆情因子库模块 | 数据依赖 | 提供因子数据 |

### 7.2 下游依赖

| 依赖模块 | 依赖类型 | 说明 |
|---------|---------|------|
| 运维人员 | 用户依赖 | 使用监控仪表盘 |
| 决策人员 | 用户依赖 | 使用监控仪表盘 |

---

## 八、参考资源

### 8.1 开源项目

- **Streamlit**: https://github.com/streamlit/streamlit
- **Grafana**: https://github.com/grafana/grafana
- **Plotly Dash**: https://github.com/plotly/dash
- **React**: https://github.com/facebook/react
- **Vue.js**: https://github.com/vuejs/vue

### 8.2 设计资源

- **Material Design**: https://material.io/design
- **Ant Design**: https://ant.design
- **Chart.js**: https://www.chartjs.org
- **D3.js**: https://d3js.org

### 8.3 最佳实践

- **数据可视化**: docs/09_BEST_PRACTICES/DATA_VISUALIZATION.md
- **实时推送**: docs/09_BEST_PRACTICES/REALTIME_PUSH.md
- **移动端设计**: docs/09_BEST_PRACTICES/MOBILE_DESIGN.md

---

**版本**: v1.0 | **更新**: 2026-04-05 | **状态**: 活跃
---

## 1. 文档治理

### 1.1 System_Manifest.md索引

```markdown
#### Layer 0: 系统架构
##### 0.001. Aiwf Rmd
- **模块ID**: AIWF_RMD_001
- **蓝图文档**: [REAL_TIME_MONITORING_DASHBOARD_BLUEPRINT.md](./REAL_TIME_MONITORING_DASHBOARD_BLUEPRINT.md)
- **技术规格书**: 待创建
- **职责**: 实时监控仪表盘模块
- **状态**: Active
```

### 1.2 模块职责边界

| 模块 | 职责 | 边界 |
|------|------|------|
| **Aiwf Rmd** | 实时监控仪表盘模块 | **核心模块** |

### 1.3 版本管理

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-05 | 初始版本创建 | 首席蓝图架构师 |

---

**蓝图版本**: v1.0.0 | **创建日期**: 2026-04-05 | **状态**: Active
