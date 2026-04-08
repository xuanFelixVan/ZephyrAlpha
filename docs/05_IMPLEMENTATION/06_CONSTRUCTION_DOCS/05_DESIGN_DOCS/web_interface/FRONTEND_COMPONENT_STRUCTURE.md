---
module_id: T.06.UI002
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: '2026-04-07'
owner: ﻠ۵ﮒﺕﻟﮒﺝﮔﭘﮔ?
responsibility:
- 系统实施与部署管理与优化维护
standard_type: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﻟ؟ﺝﻟ؟۰ﮔﮒ
applicable_scope: Webﻝ؟۰ﻝﻝﻠ۱ﮒﻝ،ﺁﻝﭨﻛﭨﭘﻝﭨﮔ
compliance_level: ﮒﮒ۶ﻟ؟ﺝﻟ؟۰
parent_document: ../INDEX.md
implementation_status: ﻟﺟﻟ۰?
# ﮒﻝ،ﺁﻝﭨﻛﭨﭘﻝﭨﮔ?

## 核心定位

定义前端组件的结构规范，包含组件分类、组件接口、组件通信等，确保前端组件规范化。


> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> ﮔﺕﻠ۲ﻠﮒﻛﭦ۳ﮔﻝﺏﭨﻝﭨ v5.3 - Webﻝ؟۰ﻝﻝﻠ۱ﮒﻝ،ﺁﻝﭨﻛﭨﭘﻝﭨﮔ
> **ﻝﺑ۱ﮒﺙ**: `DESIGN_004`
> **ﮒﺏﻟﮔﮔ۰۲**: Webﻝ؟۰ﻝﻝﻠ۱ﮔﭘﮔﻟ؟ﺝﻟ؟۰


## 设计目标

### 主要目标

1. **功能完整性**: 确保文档内容完整，满足使用需求
2. **易用性**: 提高文档可读性，便于快速理解
3. **可维护性**: 文档结构清晰，便于后续维护
4. **一致性**: 确保文档格式和风格统一

### 质量目标

- 文档完整性: 100%
- 格式规范性: 100%
- 内容准确性: 100%


## 1. ﮔﺑﻛﺛﻝﭨﻛﭨﭘﮔﭘﮔ

### 1.1 ﻝﭨﻛﭨﭘﮒﺎﮔ؛۰ﻝﭨﮔ

```mermaid
graph TD
A[App ﮔﺗﻝﭨﻛﭨﭘ] --> B[Layout ﮒﺕﮒﺎﻝﭨﻛﭨﭘ]
B --> C1[Header ﮒ۳ﺑﻠ۷ﮔ]
B --> C2[Sidebar ﻛﺝ۶ﻟﺝﺗﮔ]
    B --> C3[MainContent ﻛﺕﭨﮒﮒ؟ﺗﮒﭦ]
B --> C4[Footer ﮒﭦﻠ۷ﮔ]
    
    C3 --> D1[DashboardPage ﻛﭨ۹ﻟ۰۷ﮔﺟﻠ۰ﭖﻠ۱]
    C3 --> D2[TradeMonitorPage ﻛﭦ۳ﮔﻝﮔ۶ﻠ۰ﭖﻠ۱]
    C3 --> D3[PerformancePage ﮔ۶ﻟﺛﻠ۰ﭖﻠ۱]
    C3 --> D4[ConfigPage ﻠﻝﺛ؟ﻠ۰ﭖﻠ۱]
    C3 --> D5[SystemHealthPage ﻝﺏﭨﻝﭨﮒ۴ﮒﭦﺓﻠ۰ﭖﻠ۱]
    
    D1 --> E1[DashboardContainer ﻛﭨ۹ﻟ۰۷ﮔﺟﮒ؟ﺗﮒ۷]
    D2 --> E2[TradeMonitorContainer ﻛﭦ۳ﮔﻝﮔ۶ﮒ؟ﺗﮒ۷]
    D3 --> E3[PerformanceContainer ﮔ۶ﻟﺛﮒ؟ﺗﮒ۷]
    D4 --> E4[ConfigContainer ﻠﻝﺛ؟ﮒ؟ﺗﮒ۷]
    D5 --> E5[SystemHealthContainer ﻝﺏﭨﻝﭨﮒ۴ﮒﭦﺓﮒ؟ﺗﮒ۷]
    
E1 --> F1[EngineStatusGrid ﮒﺙﮔﻝﭘﮔﻝﺛﮔﺙ]
E1 --> F2[MetricsCards ﮔﮔﮒ۰ﻝﻝﭨ]
E1 --> F3[AlertPanel ﮒﻟ۵ﻠ۱ﮔﺟ]
    
E2 --> F4[TradeTable ﻛﭦ۳ﮔﻟ۰۷ﮔﺙ]
    E2 --> F5[TradeFilters ﻛﭦ۳ﮔﻟﺟﮔﭨ۳ﮒ۷]
    E2 --> F6[TradeDetailModal ﻛﭦ۳ﮔﻟﺁ۵ﮔﮔ۷۰ﮔﮔ۰]
    
    E3 --> F7[PerformanceChart ﮔ۶ﻟﺛﮒﺝﻟ۰۷]
    E3 --> F8[TimeRangeSelector ﮔﭘﻠﺑﻟﮒﺑﻠﮔ۸ﮒ۷]
E3 --> F9[MetricSelector ﮔﮔﻠﮔ۸ﮒ۷]
    
    E4 --> F10[EngineConfigForm ﮒﺙﮔﻠﻝﺛ؟ﻟ۰۷ﮒ]
E4 --> F11[StrategyConfigEditor ﻝﻝ۴ﻠﻝﺛ؟ﻝﺙﻟﺝﮒ۷]
    E4 --> F12[RiskLimitEditor ﻠ۲ﻠ۸ﻠﻠ۱ﻝﺙﻟﺝﮒ۷]
    
    E5 --> F13[HealthStatusPanel ﮒ۴ﮒﭦﺓﻝﭘﮔﻠ۱ﮔﺟ]
    E5 --> F14[LogViewer ﮔ۴ﮒﺟﮔ۴ﻝﮒ۷]
E5 --> F15[AlertHistory ﮒﻟ۵ﮒﮒﺎ]
```

### 1.2 ﻝﭨﻛﭨﭘﮒﻝﺎﭨﻟﺁﺑﮔ

| ﻝﭨﻛﭨﭘﮒﺎﻝﭦ۶ | ﻝﭨﻛﭨﭘﻝﺎﭨﮒ | ﻟﻟﺑ۲ﻟﺁﺑﮔ | ﻝ۳ﭦﻛﺝﻝﭨﻛﭨﭘ |
|
----|----------|----------|----------|
| **ﮔﺗﻝﭨ?* | App Component | ﮒﭦﻝ۷ﮒ۴ﮒ۲ﺅﺙﮒ۷ﮒﺎﻝﭘﮔﻝ؟۰?| `App.tsx` |
| **ﮒﺕﮒﺎﻝﭨﻛﭨﭘ** | Layout Components | ﻠ۰ﭖﻠ۱ﮒﺕﮒﺎﻝﭨﮔﺅﺙﮒﺁﺙﻟ۹ﮔ۰?| `Layout.tsx`, `Header.tsx` |
| **ﻠ۰ﭖﻠ۱ﻝﭨﻛﭨﭘ** | Page Components | ﻟﺓﺁﻝﺎﮒﺁﺗﮒﭦﻝﮒ؟ﮔﺑﻠ۰ﭖ?| `DashboardPage.tsx` |
| **ﮒ؟ﺗﮒ۷ﻝﭨﻛﭨﭘ** | Container Components | ﻛﺕﮒ۰ﻠﭨﻟﺝﮒ؟ﺗﮒ۷ﺅﺙﻝﭘﮔﻝ؟۰?| `DashboardContainer.tsx` |
| **ﮒﺎﻝ۳ﭦﻝﭨﻛﭨﭘ** | Presentational Components | ﻝﭦﺁUIﮒﺎﻝ۳ﭦﺅﺙﮔﻛﺕﮒ۰ﻠﭨﻟﺝ | `MetricCard.tsx` |
| **ﻟ۰۷ﮒﻝﭨﻛﭨﭘ** | Form Components | ﮔﺍﮔ؟ﻟﺝﮒ۴ﻛﺕﻠ۹?| `EngineConfigForm.tsx` |
| **ﮒﺝﻟ۰۷ﻝﭨﻛﭨﭘ** | Chart Components | ﮔﺍﮔ؟ﮒﺁﻟ۶?| `PerformanceChart.tsx` |
| **ﮒﺓ۴ﮒﺓﻝﭨﻛﭨﭘ** | Utility Components | ﻠﻝ۷ﮒﺓ۴ﮒﺓﻝﭨﻛﭨﭘ | `LoadingSpinner.tsx` |

## 2. ﮔﺕﮒﺟﻝﭨﻛﭨﭘﻟﺁ۵ﻝﭨﻟ؟ﺝﻟ؟۰

### 2.1 Layout ﮒﺕﮒﺎﻝﭨﻛﭨﭘ

#### 2.1.1 Header ﻝﭨﻛﭨﭘ
```typescript
interface HeaderProps {
  user: User | null;
  notifications: Notification[];
  onLogout: () => void;
  onNotificationClick: (id: string) => void;
}

const Header: React.FC<HeaderProps> = ({
  user,
  notifications,
  onLogout,
  onNotificationClick
}) => {
  // ﮒ؟ﻝﺍ?
};
```

**ﮒﻝﭨﻛﭨﭘﻝﭨ?*:
```
Header
ﻗﻗﻗ Logo (Logoﻝﭨﻛﭨﭘ)
ﻗﻗﻗ UserMenu (ﻝ۷ﮔﺓﻟﮒ)
?  ﻗﻗﻗ UserAvatar (ﻝ۷ﮔﺓﮒ۳ﺑﮒ)
?  ﻗﻗﻗ UserInfo (ﻝ۷ﮔﺓﻛﺟ۰ﮔﺁ)
?  ﻗﻗﻗ LogoutButton (ﻠﮒﭦﮔ?
ﻗﻗﻗ NotificationBell (ﻠﻝ۴ﻠﻠ)
?  ﻗﻗﻗ NotificationList (ﻠﻝ۴ﮒﻟ۰۷)
ﻗﻗﻗ QuickActions (ﮒﺟ،ﮔﺓﮔﻛﺛ)
    ﻗﻗﻗ RefreshButton (ﮒﺓﮔﺍﮔﻠ؟)
    ﻗﻗﻗ HelpButton (ﮒﺕ؟ﮒ۸ﮔﻠ؟)
```

#### 2.1.2 Sidebar ﻝﭨﻛﭨﭘ
```typescript
interface SidebarProps {
  activePath: string;
  onNavigate: (path: string) => void;
  collapsed: boolean;
  onCollapseChange: (collapsed: boolean) => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  activePath,
  onNavigate,
  collapsed,
  onCollapseChange
}) => {
  // ﮒ؟ﻝﺍ?
};
```

**ﮒﺁﺙﻟ۹ﻟﮒ?*:
```typescript
const menuItems = [
  {
    key: 'dashboard',
    icon: <DashboardOutlined />,
    label: 'ﻛﭨ۹ﻟ۰۷?,
    path: '/dashboard'
  },
  {
    key: 'trades',
    icon: <TransactionOutlined />,
    label: 'ﻛﭦ۳ﮔﻝﮔ۶',
    path: '/trades'
  },
  {
    key: 'performance',
    icon: <LineChartOutlined />,
    label: 'ﮔ۶ﻟﺛﮒﮔ',
    path: '/performance'
  },
  {
    key: 'config',
    icon: <SettingOutlined />,
    label: 'ﻠﻝﺛ؟ﻝ؟۰ﻝ',
    path: '/config',
    children: [
      { key: 'engines', label: 'ﮒﺙﮔﻠﻝﺛ؟', path: '/config/engines' },
{ key: 'strategies', label: 'ﻝﻝ۴ﻠﻝﺛ؟', path: '/config/strategies' },
      { key: 'risk', label: 'ﻠ۲ﻠ۸ﻠﻠ۱', path: '/config/risk' }
    ]
  },
  {
    key: 'system',
    icon: <MonitorOutlined />,
    label: 'ﻝﺏﭨﻝﭨﮒ۴ﮒﭦﺓ',
    path: '/system'
  }
];
```

### 2.2 DashboardPage ﻛﭨ۹ﻟ۰۷ﮔﺟﻠ۰ﭖ?

#### 2.2.1 ﻝﭨﻛﭨﭘﻝﭨﮔ
```
DashboardPage
ﻗﻗﻗ DashboardContainer
    ﻗﻗﻗ EngineStatusGrid
    ?  ﻗﻗﻗ EngineStatusCard (ﺣN)
?  ?  ﻗﻗﻗ EngineIcon (ﮒﺙﮔﮒﺝﮔ)
    ?  ?  ﻗﻗﻗ EngineName (ﮒﺙﮔﮒﻝ۶ﺍ)
    ?  ?  ﻗﻗﻗ StatusIndicator (ﻝﭘﮔﮔﻝ۳ﭦﮒ۷)
?  ?  ﻗﻗﻗ PerformanceMetrics (ﮔ۶ﻟﺛﮔﮔ)
    ?  ?  ﻗﻗﻗ ActionButtons (ﮔﻛﺛﮔﻠ؟)
?  ﻗﻗﻗ AddEngineCard (ﮔﺓﭨﮒﮒﺙﮔﮒ۰ﻝ)
    ﻗﻗﻗ MetricsOverview
    ?  ﻗﻗﻗ TotalTradesCard (ﮔﭨﻛﭦ۳ﮔﮔﺍ)
    ?  ﻗﻗﻗ TotalVolumeCard (ﮔﭨﻛﭦ۳ﮔﻠ۱)
    ?  ﻗﻗﻗ ActiveEnginesCard (ﮔﺑﭨﻟﺓﮒﺙﮔ)
    ?  ﻗﻗﻗ SystemHealthCard (ﻝﺏﭨﻝﭨﮒ۴ﮒﭦﺓ?
    ﻗﻗﻗ RecentAlertsPanel
?  ﻗﻗﻗ AlertItem (ﮒﻟ۵?
    ?  ﻗﻗﻗ ViewAllAlertsButton (ﮔ۴ﻝﮒ۷ﻠ۷)
    ﻗﻗﻗ QuickActionsPanel
        ﻗﻗﻗ StartAllEnginesButton (ﮒﺁﮒ۷ﮔﮔﮒﺙ?
ﻗﻗﻗ StopAllEnginesButton (ﮒﮔ۱ﮔﮔﮒﺙ?
        ﻗﻗﻗ RunHealthCheckButton (ﻟﺟﻟ۰ﮒ۴ﮒﭦﺓﮔ۲?
```

#### 2.2.2 EngineStatusCard ﻝﭨﻛﭨﭘﻟ؟ﺝﻟ؟۰
```typescript
interface EngineStatusCardProps {
  engine: Engine;
  onStart: (engineId: string) => void;
  onStop: (engineId: string) => void;
  onConfigure: (engineId: string) => void;
  onViewDetails: (engineId: string) => void;
}

const EngineStatusCard: React.FC<EngineStatusCardProps> = ({
  engine,
  onStart,
  onStop,
  onConfigure,
  onViewDetails
}) => {
  const statusColor = {
    running: 'green',
    stopped: 'gray',
    error: 'red',
    starting: 'orange'
  }[engine.status];

  return (
    <Card 
      title={
        <div className="engine-card-header">
          <EngineIcon type={engine.type} />
          <span className="engine-name">{engine.name}</span>
          <StatusBadge color={statusColor}>{engine.status}</StatusBadge>
        </div>
      }
      actions={[
        <Tooltip title="ﮒﺁﮒ۷">
          <PlayCircleOutlined onClick={() => onStart(engine.id)} />
        </Tooltip>,
<Tooltip title="ﮒﮔ۱">
          <StopOutlined onClick={() => onStop(engine.id)} />
        </Tooltip>,
        <Tooltip title="ﻠﻝﺛ؟">
          <SettingOutlined onClick={() => onConfigure(engine.id)} />
        </Tooltip>,
        <Tooltip title="ﻟﺁ۵ﮔ">
          <EyeOutlined onClick={() => onViewDetails(engine.id)} />
        </Tooltip>
      ]}
    >
      <div className="engine-metrics">
        <MetricItem label="CPU" value={`${engine.cpuUsage}%`} />
<MetricItem label="ﮒﮒ" value={`${engine.memoryUsage}%`} />
        <MetricItem label="ﻛﭨﮔ۴ﻛﭦ۳ﮔ" value={engine.tradesToday} />
        <MetricItem label="ﻠﻟﺁﺁ? value={engine.errorCount} />
      </div>
      <div className="engine-last-update">
        ﮔﮒﮔﺑ? {formatTime(engine.lastHeartbeat)}
      </div>
    </Card>
  );
};
```

### 2.3 TradeMonitorPage ﻛﭦ۳ﮔﻝﮔ۶ﻠ۰ﭖﻠ۱

#### 2.3.1 ﻝﭨﻛﭨﭘﻝﭨﮔ
```
TradeMonitorPage
ﻗﻗﻗ TradeMonitorContainer
    ﻗﻗﻗ TradeFilters
    ?  ﻗﻗﻗ DateRangePicker (ﮔ۴ﮔﻟﮒﺑﻠﮔ۸?
?  ﻗﻗﻗ SymbolSelector (ﮔﻝﻠﮔ۸?
    ?  ﻗﻗﻗ EngineSelector (ﮒﺙﮔﻠﮔ۸?
    ?  ﻗﻗﻗ SideFilter (ﻛﺗﺍﮒﮔﺗﮒﻟﺟﮔﭨ۳?
    ?  ﻗﻗﻗ ApplyFiltersButton (ﮒﭦﻝ۷ﻟﺟﮔﭨ۳?
    ﻗﻗﻗ TradeTable
?  ﻗﻗﻗ TradeTableHeader (ﻟ۰۷ﮔﺙﮒ۳ﺑﻠ۷)
?  ﻗﻗﻗ TradeTableRow (ﻟ۰۷ﮔﺙ?ﺣN)
    ?  ?  ﻗﻗﻗ TradeIdCell (ﻛﭦ۳ﮔID)
    ?  ?  ﻗﻗﻗ TimestampCell (ﮔﭘﻠﺑ?
?  ?  ﻗﻗﻗ SymbolCell (ﮔﻝ)
    ?  ?  ﻗﻗﻗ SideCell (ﻛﺗﺍﮒﮔﺗﮒ)
?  ?  ﻗﻗﻗ PriceCell (ﻛﭨﺓﮔﺙ)
    ?  ?  ﻗﻗﻗ QuantityCell (ﮔﺍﻠ)
    ?  ?  ﻗﻗﻗ VolumeCell (ﻠﻠ۱)
    ?  ?  ﻗﻗﻗ EngineCell (ﮒﺙﮔ)
    ?  ?  ﻗﻗﻗ ActionsCell (ﮔﻛﺛ)
?  ﻗﻗﻗ TradeTableFooter (ﻟ۰۷ﮔﺙﮒﭦﻠ۷)
    ﻗﻗﻗ TradeStatsPanel
    ?  ﻗﻗﻗ TotalTradesStat (ﮔﭨﻛﭦ۳ﮔﮔﺍ)
    ?  ﻗﻗﻗ TotalVolumeStat (ﮔﭨﻛﭦ۳ﮔﻠ۱)
?  ﻗﻗﻗ AvgPriceStat (ﮒﺗﺏﮒﻛﭨﺓﮔﺙ)
    ?  ﻗﻗﻗ TradeDistributionChart (ﻛﭦ۳ﮔﮒﮒﺕ?
    ﻗﻗﻗ TradeDetailModal (ﻛﭦ۳ﮔﻟﺁ۵ﮔﮔ۷۰ﮔﮔ۰)
```

#### 2.3.2 TradeTable ﻝﭨﻛﭨﭘﻟ؟ﺝﻟ؟۰
```typescript
interface TradeTableProps {
  trades: Trade[];
  loading: boolean;
  onRowClick: (trade: Trade) => void;
  onSortChange: (sortBy: string, sortOrder: 'asc' | 'desc') => void;
  pagination: {
    current: number;
    pageSize: number;
    total: number;
    onChange: (page: number, pageSize: number) => void;
  };
}

const TradeTable: React.FC<TradeTableProps> = ({
  trades,
  loading,
  onRowClick,
  onSortChange,
  pagination
}) => {
  const columns = [
    {
      title: 'ﻛﭦ۳ﮔID',
      dataIndex: 'tradeId',
      key: 'tradeId',
      sorter: true,
      width: 120
    },
    {
      title: 'ﮔﭘﻠﺑ',
      dataIndex: 'timestamp',
      key: 'timestamp',
      sorter: true,
      render: (timestamp: string) => formatDateTime(timestamp),
      width: 150
    },
    {
title: 'ﮔﻝ',
      dataIndex: 'symbol',
      key: 'symbol',
      width: 100
    },
    {
      title: 'ﮔﺗﮒ',
      dataIndex: 'side',
      key: 'side',
      render: (side: string) => (
        <Tag color={side === 'buy' ? 'green' : 'red'}>
          {side === 'buy' ? 'ﻛﺗﺍﮒ۴' : 'ﮒﮒﭦ'}
        </Tag>
      ),
      width: 80
    },
    {
title: 'ﻛﭨﺓﮔﺙ',
      dataIndex: 'price',
      key: 'price',
      sorter: true,
      render: (price: number) => formatCurrency(price),
      width: 100
    },
    {
      title: 'ﮔﺍﻠ',
      dataIndex: 'quantity',
      key: 'quantity',
      sorter: true,
      width: 100
    },
    {
      title: 'ﻠﻠ۱',
      dataIndex: 'volume',
      key: 'volume',
      sorter: true,
      render: (volume: number) => formatCurrency(volume),
      width: 120
    },
    {
      title: 'ﮒﺙﮔ',
      dataIndex: 'engineId',
      key: 'engineId',
      width: 100
    },
    {
      title: 'ﮔﻛﺛ',
      key: 'actions',
      render: (_: any, trade: Trade) => (
        <Button
          type="link"
          onClick={() => onRowClick(trade)}
          icon={<EyeOutlined />}
        >
          ﻟﺁ۵ﮔ
        </Button>
      ),
      width: 80
    }
  ];

  return (
    <Table
      columns={columns}
      dataSource={trades}
      loading={loading}
      rowKey="tradeId"
      pagination={pagination}
      onChange={(pagination, filters, sorter) => {
        if (sorter && 'field' in sorter) {
          onSortChange(
            sorter.field as string,
            sorter.order === 'ascend' ? 'asc' : 'desc'
          );
        }
      }}
      onRow={(record) => ({
        onClick: () => onRowClick(record)
      })}
    />
  );
};
```

### 2.4 PerformancePage ﮔ۶ﻟﺛﮒﮔﻠ۰ﭖﻠ۱

#### 2.4.1 ﻝﭨﻛﭨﭘﻝﭨﮔ
```
PerformancePage
ﻗﻗﻗ PerformanceContainer
    ﻗﻗﻗ ChartControls
    ?  ﻗﻗﻗ TimeRangeSelector (ﮔﭘﻠﺑﻟﮒﺑﻠﮔ۸?
?  ﻗﻗﻗ MetricSelector (ﮔﮔﻠﮔ۸?
    ?  ﻗﻗﻗ ChartTypeSelector (ﮒﺝﻟ۰۷ﻝﺎﭨﮒﻠﮔ۸?
    ?  ﻗﻗﻗ EngineFilter (ﮒﺙﮔﻟﺟﮔﭨ۳?
    ?  ﻗﻗﻗ RefreshButton (ﮒﺓﮔﺍﮔﻠ؟)
    ﻗﻗﻗ ChartArea
    ?  ﻗﻗﻗ EquityCurveChart (ﮔﻝﮔﺎﻝﭦﺟ?
    ?  ﻗﻗﻗ DrawdownChart (ﮒﮔ۳?
    ?  ﻗﻗﻗ SharpeRatioChart (ﮒ۳ﮔ؟ﮔﺁﻝ?
    ?  ﻗﻗﻗ TradeDistributionChart (ﻛﭦ۳ﮔﮒﮒﺕ?
?  ﻗﻗﻗ PerformanceHeatmap (ﮔ۶ﻟﺛﻝﮒ?
    ﻗﻗﻗ PerformanceMetricsPanel
    ?  ﻗﻗﻗ SharpeRatioCard (ﮒ۳ﮔ؟ﮔﺁﻝ)
    ?  ﻗﻗﻗ MaxDrawdownCard (ﮔﮒ۳۶ﮒ?
    ?  ﻗﻗﻗ WinRateCard (ﻟﻝ)
    ?  ﻗﻗﻗ AvgReturnCard (ﮒﺗﺏﮒﮔﭘﻝ)
    ?  ﻗﻗﻗ VolatilityCard (ﮔﺏ۱ﮒ۷?
    ﻗﻗﻗ ExportControls
        ﻗﻗﻗ ExportCSVButton (ﮒﺁﺙﮒﭦCSV)
        ﻗﻗﻗ ExportPNGButton (ﮒﺁﺙﮒﭦPNG)
        ﻗﻗﻗ ShareReportButton (ﮒﻛﭦ،ﮔ۴ﮒ)
```

#### 2.4.2 PerformanceChart ﻝﭨﻛﭨﭘﻟ؟ﺝﻟ؟۰
```typescript
interface PerformanceChartProps {
  data: ChartData[];
  chartType: 'line' | 'bar' | 'area' | 'scatter';
  title: string;
  xAxisKey: string;
  yAxisKey: string;
  color?: string;
  height?: number;
  onPointClick?: (point: ChartDataPoint) => void;
}

const PerformanceChart: React.FC<PerformanceChartProps> = ({
  data,
  chartType,
  title,
  xAxisKey,
  yAxisKey,
  color = '#1890ff',
  height = 400,
  onPointClick
}) => {
  const chartConfig = {
    line: {
      type: 'monotone',
      dataKey: yAxisKey,
      stroke: color,
      strokeWidth: 2,
      dot: false,
      activeDot: { r: 6, onClick: onPointClick }
    },
    bar: {
      dataKey: yAxisKey,
      fill: color
    },
    area: {
      type: 'monotone',
      dataKey: yAxisKey,
      stroke: color,
      fill: color,
      fillOpacity: 0.3
    },
    scatter: {
      dataKey: yAxisKey,
      fill: color,
      r: 4
    }
  };

  return (
    <div className="performance-chart">
      <h3>{title}</h3>
      <ResponsiveContainer width="100%" height={height}>
        <RechartsChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey={xAxisKey} 
            tickFormatter={formatDate}
          />
          <YAxis 
            tickFormatter={formatNumber}
            label={{ value: yAxisKey, angle: -90, position: 'insideLeft' }}
          />
          <Tooltip 
            formatter={(value) => [formatNumber(value as number), yAxisKey]}
            labelFormatter={formatDate}
          />
          <Legend />
          {chartType === 'line' && <Line {...chartConfig.line} />}
          {chartType === 'bar' && <Bar {...chartConfig.bar} />}
          {chartType === 'area' && <Area {...chartConfig.area} />}
          {chartType === 'scatter' && <Scatter {...chartConfig.scatter} />}
        </RechartsChart>
      </ResponsiveContainer>
    </div>
  );
};
```

## 3. ﻝﭨﻛﭨﭘﻛﭦ۳ﻛﭦﮒﺏﻝﺏﭨ

### 3.1 ﮔﺍﮔ؟ﮔﭖﮒﺝ

```mermaid
graph LR
    A[ﮒﻝ،ﺁAPI] --> B[API Service]
    B --> C[Redux Store]
    C --> D[Container Components]
    D --> E[Presentational Components]
    E --> F[UI Events]
    F --> D
    D --> G[Action Creators]
    G --> C
    C --> H[Selectors]
    H --> D
    
    I[WebSocket] --> J[WebSocket Service]
    J --> C
```

### 3.2 ﻝﭘﮔﻝ؟۰ﻝﻟ؟ﺝ?

#### 3.2.1 Redux Store ﻝﭨﮔ
```typescript
interface RootState {
  auth: AuthState;
  engines: EnginesState;
  trades: TradesState;
  performance: PerformanceState;
  config: ConfigState;
  system: SystemState;
  ui: UIState;
}

interface EnginesState {
  engineList: Engine[];
  loading: boolean;
  error: string | null;
  selectedEngineId: string | null;
}

interface TradesState {
  trades: Trade[];
  filters: TradeFilters;
  loading: boolean;
  error: string | null;
  pagination: Pagination;
  selectedTrade: Trade | null;
}

interface UIState {
  sidebarCollapsed: boolean;
  theme: 'light' | 'dark';
  notifications: Notification[];
  modal: {
    type: string | null;
    data: any;
  };
}
```

#### 3.2.2 ﮒﺏﻠ؟Actionﮒ؟ﻛﺗ
```typescript
// ﮒﺙﮔﻝﺕﮒﺏAction
const fetchEngines = createAsyncThunk('engines/fetch', async () => {
  const response = await engineAPI.getEngines();
  return response.data;
});

const startEngine = createAsyncThunk('engines/start', async (engineId: string) => {
  const response = await engineAPI.startEngine(engineId);
  return response.data;
});

const updateEngineConfig = createAsyncThunk('engines/updateConfig', 
  async ({ engineId, config }: { engineId: string; config: EngineConfig }) => {
    const response = await engineAPI.updateConfig(engineId, config);
    return response.data;
  }
);

// ﻛﭦ۳ﮔﻝﺕﮒﺏAction
const fetchTrades = createAsyncThunk('trades/fetch', 
  async (filters: TradeFilters) => {
    const response = await tradeAPI.getTrades(filters);
    return response.data;
  }
);

// WebSocket Action
const websocketMessageReceived = createAction('websocket/message', 
  (message: WebSocketMessage) => ({ payload: message })
);
```

## 4. ﻝﭨﻛﭨﭘﮒﺙﮒﻟ۶?

### 4.1 ﮒﺛﮒﻟ۶ﻟ
| ﻝﭨﻛﭨﭘﻝﺎﭨﮒ | ﮒﺛﮒﻟ۶ﮒ | ﻝ۳ﭦﻛﺝ |
|----------|----------|------|
| **ﻠ۰ﭖﻠ۱ﻝﭨﻛﭨﭘ** | `[PageName]Page` | `DashboardPage.tsx` |
| **ﮒ؟ﺗﮒ۷ﻝﭨﻛﭨﭘ** | `[Feature]Container` | `DashboardContainer.tsx` |
| **ﮒﺎﻝ۳ﭦﻝﭨﻛﭨﭘ** | `[ComponentName]` | `MetricCard.tsx` |
| **ﻟ۰۷ﮒﻝﭨﻛﭨﭘ** | `[FormName]Form` | `EngineConfigForm.tsx` |
| **ﮒﺝﻟ۰۷ﻝﭨﻛﭨﭘ** | `[ChartName]Chart` | `PerformanceChart.tsx` |
| **ﮒﺓ۴ﮒﺓﻝﭨﻛﭨﭘ** | `[UtilityName]` | `LoadingSpinner.tsx` |

### 4.2 ﮔﻛﭨﭘﻝﭨﮔﻟ۶ﻟ
```
src/
ﻗﻗﻗ components/
?  ﻗﻗﻗ layout/           # ﮒﺕﮒﺎﻝﭨﻛﭨﭘ
?  ?  ﻗﻗﻗ Header.tsx
?  ?  ﻗﻗﻗ Sidebar.tsx
?  ?  ﻗﻗﻗ Layout.tsx
?  ﻗﻗﻗ pages/           # ﻠ۰ﭖﻠ۱ﻝﭨﻛﭨﭘ
?  ?  ﻗﻗﻗ DashboardPage.tsx
?  ?  ﻗﻗﻗ TradeMonitorPage.tsx
?  ?  ﻗﻗﻗ PerformancePage.tsx
?  ﻗﻗﻗ containers/      # ﮒ؟ﺗﮒ۷ﻝﭨﻛﭨﭘ
?  ?  ﻗﻗﻗ DashboardContainer.tsx
?  ?  ﻗﻗﻗ TradeMonitorContainer.tsx
?  ?  ﻗﻗﻗ PerformanceContainer.tsx
?  ﻗﻗﻗ charts/         # ﮒﺝﻟ۰۷ﻝﭨﻛﭨﭘ
?  ?  ﻗﻗﻗ PerformanceChart.tsx
?  ?  ﻗﻗﻗ TradeDistributionChart.tsx
?  ﻗﻗﻗ forms/          # ﻟ۰۷ﮒﻝﭨﻛﭨﭘ
?  ?  ﻗﻗﻗ EngineConfigForm.tsx
?  ?  ﻗﻗﻗ StrategyConfigForm.tsx
?  ﻗﻗﻗ common/         # ﻠﻝ۷ﻝﭨﻛﭨﭘ
?      ﻗﻗﻗ LoadingSpinner.tsx
?      ﻗﻗﻗ ErrorBoundary.tsx
?      ﻗﻗﻗ NotFound.tsx
ﻗﻗﻗ services/           # ﮔﮒ۰?
?  ﻗﻗﻗ api.ts
?  ﻗﻗﻗ websocket.ts
?  ﻗﻗﻗ auth.ts
ﻗﻗﻗ store/              # ﻝﭘﮔﻝ؟۰?
?  ﻗﻗﻗ index.ts
?  ﻗﻗﻗ actions.ts
?  ﻗﻗﻗ reducers.ts
?  ﻗﻗﻗ selectors.ts
ﻗﻗﻗ hooks/              # ﻟ۹ﮒ؟ﻛﺗHook
?  ﻗﻗﻗ useEngines.ts
?  ﻗﻗﻗ useTrades.ts
?  ﻗﻗﻗ useWebSocket.ts
ﻗﻗﻗ utils/              # ﮒﺓ۴ﮒﺓﮒﺛﮔﺍ
?  ﻗﻗﻗ formatters.ts
?  ﻗﻗﻗ validators.ts
?  ﻗﻗﻗ constants.ts
ﻗﻗﻗ types/              # TypeScriptﻝﺎﭨﮒﮒ؟ﻛﺗ
    ﻗﻗﻗ index.ts
    ﻗﻗﻗ engine.ts
    ﻗﻗﻗ trade.ts
```

### 4.3 ﻝﭨﻛﭨﭘﮒﺙﮒﮒ?

#### 4.3.1 ﮒﻛﺕﻟﻟﺑ۲ﮒﮒ
- ﮔﺁﻛﺕ۹ﻝﭨﻛﭨﭘﮒ۹ﻟﺑﻟﺑ۲ﻛﺕﻛﺕ۹ﮒ?
- ﮒ؟ﺗﮒ۷ﻝﭨﻛﭨﭘﻟﺑﻟﺑ۲ﻝﭘﮔﻝ؟۰ﻝﮒﻛﺕﮒ۰ﻠﭨﻟﺝ
- ﮒﺎﻝ۳ﭦﻝﭨﻛﭨﭘﮒ۹ﻟﺑﻟﺑ۲UIﮔﺕﺎﮔ

#### 4.3.2 ﮒﺁﮒ۳ﻝ۷ﮔ۶ﮒ?
- ﮔﮒﻠﻝ۷ﻝﭨﻛﭨﭘﮒﺍ`common/`ﻝ؟ﮒﺛ
- ﻝﭨﻛﭨﭘﮒﮔﺍﻟ؟ﺝﻟ؟۰ﻟ۵ﻝﭖ?
- ﮔﺁﮔﻟ۹ﮒ؟ﻛﺗﮔﺓﮒﺙﮒﻛﭦﻛﭨﭘ

#### 4.3.3 ﮒﺁﮔﭖﻟﺁﮔ۶ﮒ?
- ﻝﭨﻛﭨﭘﻠﭨﻟﺝﻛﺕUIﮒﻝ۵ﭨ
- ﻛﺛﺟﻝ۷Propsﮔﺏ۷ﮒ۴ﻛﺝﻟﭖ
- ﮔﻛﺝﮔﭖﻟﺁﮒﮒ۴ﺛﻝﮔ۴?

#### 4.3.4 ﮔ۶ﻟﺛﻛﺙﮒﮒﮒ
- ﻛﺛﺟﻝ۷React.memoﻠﺟﮒﻛﺕﮒﺟﻟ۵ﻝﻠﮔﺕﺎ?
- ﻛﺛﺟﻝ۷useMemo/useCallbackﻛﺙﮒﻟ؟۰ﻝ؟
- ﮒ؟ﻝﺍﻟﮔﮔﭨﮒ۷ﮒ۳ﻝﮒ۳۶ﮔﺍﮔ؟ﮒ?
- ﮔﻠﮒﻟﺛﺛﮒ۳۶ﮒﻝﭨﻛﭨﭘ

## 5. ﮒ؟ﮔﺛﮔﮒ

### 5.1 ﻝﭨﻛﭨﭘﮒﺙﮒﻠ۰ﭦ?
1. **ﮒﭦﻝ۰ﻝﭨﻛﭨﭘ** (??
   - Layoutﻝﭨﻛﭨﭘ (Header, Sidebar, Footer)
   - ﻠﻝ۷ﻝﭨﻛﭨﭘ (LoadingSpinner, ErrorBoundary)
   - ﮒﺓ۴ﮒﺓﮒﺛﮔﺍﮒﻝﺎﭨﮒﮒ؟?

2. **ﻠ۰ﭖﻠ۱ﮔ۰ﮔﭘ** (??
   - ﻠ۰ﭖﻠ۱ﻟﺓﺁﻝﺎﻠﻝﺛ؟
   - ﻠ۰ﭖﻠ۱ﻠ۹۷ﮔﭘﻝﭨﻛﭨﭘ
   - ﮒﺁﺙﻟ۹ﮒﮔﻠﮔ۶?

3. **ﮔﺕﮒﺟﮒﻟﺛﻝﭨﻛﭨﭘ** (?-4?
   - Dashboardﻝﺕﮒﺏﻝﭨﻛﭨﭘ
   - TradeMonitorﻝﺕﮒﺏﻝﭨﻛﭨﭘ
   - Performanceﻝﺕﮒﺏﻝﭨﻛﭨﭘ

4. **ﻠ،ﻝﭦ۶ﮒﻟﺛﻝﭨﻛﭨﭘ** (??
   - Configﻝﺕﮒﺏﻝﭨﻛﭨﭘ
   - SystemHealthﻝﺕﮒﺏﻝﭨﻛﭨﭘ
   - ﮒﺁﺙﮒﭦﮒﮒﻛﭦ،ﮒ?

5. **ﻛﺙﮒﮒﮔﭖ?* (?-7?
   - ﮔ۶ﻟﺛﻛﺙﮒ
   - ﮒﮒﭦﮒﺙﻟ؟ﺝ?
   - ﮒﮒﮔﭖﻟﺁﮒE2Eﮔﭖﻟﺁ

### 5.2 ﻝﭨﻛﭨﭘﮔﭖﻟﺁﻝﻝ۴
| ﮔﭖﻟﺁﻝﺎﭨﮒ | ﮔﭖﻟﺁﮒﺓ۴ﮒﺓ | ﮔﭖﻟﺁﻝ؟ﮔ | ﻟ۵ﻝﻝﻝ؟?|
|----------|----------|----------|------------|
| **ﮒﮒﮔﭖﻟﺁ** | Jest + React Testing Library | ﻝﭨﻛﭨﭘﻠﭨﻟﺝﮒﮔﺕﺎ?| ?0% |
| **ﻠﮔﮔﭖﻟﺁ** | Cypress | ﻝﭨﻛﭨﭘﻠﺑﻛﭦ۳?| ?0% |
| **E2Eﮔﭖﻟﺁ** | Cypress | ﮒ؟ﮔﺑﻝ۷ﮔﺓﮔﭖﻝ۷ | ?0% |
| **ﮔ۶ﻟﺛﮔﭖﻟﺁ** | Lighthouse | ﮒﻟﺛﺛﮒﮔﺕﺎﮔﮔ۶ﻟﺛ | ﻟﺝﺝﮔ |
| **ﮒﺁﻟ۶ﮒﮔﭖ?* | Storybook + Chromatic | UIﻛﺕﻟﺑﮔ۶ﮒﮒﮒﺛ | 100% |

### 5.3 ﻝﭨﻛﭨﭘﮔﮔ۰۲ﻟ۶ﻟ
ﮔﺁﻛﺕ۹ﻝﭨﻛﭨﭘﻠﻟ۵ﮒﮒ،ﺅﺙ
1. **ﻝﭨﻛﭨﭘﻟﺁﺑﮔ**: ﻝ۷ﻠﻙﮒﻟﺛﻙﻛﺛﺟﻝ۷ﮒﭦ?
2. **Propsﮔ۴ﮒ۲**: TypeScriptﮔ۴ﮒ۲ﮒ؟ﻛﺗ
3. **ﻛﺛﺟﻝ۷ﻝ۳ﭦﻛﺝ**: ﻛﭨ۲ﻝﻝ۳ﭦﻛﺝ
4. **ﮔﺏ۷ﮔﻛﭦﻠ۰ﺗ**: ﻛﺛﺟﻝ۷ﻠﮒﭘﮒﮔﻛﺛﺏﮒ؟?
5. **APIﮔﮔ۰۲**: ﮔﺗﮔﺏﮒﻛﭦﻛﭨﭘﻟﺁﺑ?

---

**ﮔﮔ۰۲ﻝﮔ؛**: 1.0.0  
**ﮔﮒﮔﺑ?*: 2026-04-02  
**ﻝﭨﺑﮔ۳?*: ﻠ۵ﮒﺕﻟﮒﺝﮔﭘﮔ?
**ﻝﺑ۱ﮒﺙ**: `DESIGN_004`  
**ﻝ?*: ?ﻟ؟ﺝﻟ؟۰ﮒ؟ﮔﺅﺙﮒﺝﻟﺁﮒ؟۰
