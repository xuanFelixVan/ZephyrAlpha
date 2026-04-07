---
module_id: T.06.UI002
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: ﻠ۵ﮒﺕ­ﻟﮒﺝﮔﭘﮔ?
responsibility:
  - 实施指南、部署文档
standard_type: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﻟ؟ﺝﻟ؟۰ﮔ ﮒ
applicable_scope: Webﻝ؟۰ﻝﻝﻠ۱ﮒﻝ،ﺁﻝﭨﻛﭨﭘﻝﭨﮔ
compliance_level: ﮒﮒ۶ﻟ؟ﺝﻟ؟۰
parent_document: ../INDEX.md
implementation_status: ﻟﺟﻟ۰?
---
---


# ﮒﻝ،ﺁﻝﭨﻛﭨﭘﻝﭨﮔ?
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> ﮔﺕﻠ۲ﻠﮒﻛﭦ۳ﮔﻝﺏﭨﻝﭨ v5.3 - Webﻝ؟۰ﻝﻝﻠ۱ﮒﻝ،ﺁﻝﭨﻛﭨﭘﻝﭨﮔ
> **ﻝﺑ۱ﮒﺙ**: `DESIGN_004`
> **ﮒﺏﻟﮔﮔ۰۲**: [Webﻝ؟۰ﻝﻝﻠ۱ﮔﭘﮔﻟ؟ﺝﻟ؟۰](T.06.UI001.web_management_interface_architecture_design.md)

## 1. ﮔﺑﻛﺛﻝﭨﻛﭨﭘﮔﭘﮔ

### 1.1 ﻝﭨﻛﭨﭘﮒﺎﮔ؛۰ﻝﭨﮔ

```mermaid
graph TD
    A[App ﮔ ﺗﻝﭨﻛﭨﭘ] --> B[Layout ﮒﺕﮒﺎﻝﭨﻛﭨﭘ]
    B --> C1[Header ﮒ۳ﺑﻠ۷ﮔ ]
    B --> C2[Sidebar ﻛﺝ۶ﻟﺝﺗﮔ ]
    B --> C3[MainContent ﻛﺕﭨﮒﮒ؟ﺗﮒﭦ]
    B --> C4[Footer ﮒﭦﻠ۷ﮔ ]
    
    C3 --> D1[DashboardPage ﻛﭨ۹ﻟ۰۷ﮔﺟﻠ۰ﭖﻠ۱]
    C3 --> D2[TradeMonitorPage ﻛﭦ۳ﮔﻝﮔ۶ﻠ۰ﭖﻠ۱]
    C3 --> D3[PerformancePage ﮔ۶ﻟﺛﻠ۰ﭖﻠ۱]
    C3 --> D4[ConfigPage ﻠﻝﺛ؟ﻠ۰ﭖﻠ۱]
    C3 --> D5[SystemHealthPage ﻝﺏﭨﻝﭨﮒ۴ﮒﭦﺓﻠ۰ﭖﻠ۱]
    
    D1 --> E1[DashboardContainer ﻛﭨ۹ﻟ۰۷ﮔﺟﮒ؟ﺗﮒ۷]
    D2 --> E2[TradeMonitorContainer ﻛﭦ۳ﮔﻝﮔ۶ﮒ؟ﺗﮒ۷]
    D3 --> E3[PerformanceContainer ﮔ۶ﻟﺛﮒ؟ﺗﮒ۷]
    D4 --> E4[ConfigContainer ﻠﻝﺛ؟ﮒ؟ﺗﮒ۷]
    D5 --> E5[SystemHealthContainer ﻝﺏﭨﻝﭨﮒ۴ﮒﭦﺓﮒ؟ﺗﮒ۷]
    
    E1 --> F1[EngineStatusGrid ﮒﺙﮔﻝﭘﮔﻝﺛﮔ ﺙ]
    E1 --> F2[MetricsCards ﮔﮔ ﮒ۰ﻝﻝﭨ]
    E1 --> F3[AlertPanel ﮒﻟ­۵ﻠ۱ﮔﺟ]
    
    E2 --> F4[TradeTable ﻛﭦ۳ﮔﻟ۰۷ﮔ ﺙ]
    E2 --> F5[TradeFilters ﻛﭦ۳ﮔﻟﺟﮔﭨ۳ﮒ۷]
    E2 --> F6[TradeDetailModal ﻛﭦ۳ﮔﻟﺁ۵ﮔﮔ۷۰ﮔﮔ۰]
    
    E3 --> F7[PerformanceChart ﮔ۶ﻟﺛﮒﺝﻟ۰۷]
    E3 --> F8[TimeRangeSelector ﮔﭘﻠﺑﻟﮒﺑﻠﮔ۸ﮒ۷]
    E3 --> F9[MetricSelector ﮔﮔ ﻠﮔ۸ﮒ۷]
    
    E4 --> F10[EngineConfigForm ﮒﺙﮔﻠﻝﺛ؟ﻟ۰۷ﮒ]
    E4 --> F11[StrategyConfigEditor ﻝ­ﻝ۴ﻠﻝﺛ؟ﻝﺙﻟﺝﮒ۷]
    E4 --> F12[RiskLimitEditor ﻠ۲ﻠ۸ﻠﻠ۱ﻝﺙﻟﺝﮒ۷]
    
    E5 --> F13[HealthStatusPanel ﮒ۴ﮒﭦﺓﻝﭘﮔﻠ۱ﮔﺟ]
    E5 --> F14[LogViewer ﮔ۴ﮒﺟﮔ۴ﻝﮒ۷]
    E5 --> F15[AlertHistory ﮒﻟ­۵ﮒﮒﺎ]
```

### 1.2 ﻝﭨﻛﭨﭘﮒﻝﺎﭨﻟﺁﺑﮔ

| ﻝﭨﻛﭨﭘﮒﺎﻝﭦ۶ | ﻝﭨﻛﭨﭘﻝﺎﭨﮒ | ﻟﻟﺑ۲ﻟﺁﺑﮔ | ﻝ۳ﭦﻛﺝﻝﭨﻛﭨﭘ |
|----------|----------|----------|----------|
| **ﮔ ﺗﻝﭨ?* | App Component | ﮒﭦﻝ۷ﮒ۴ﮒ۲ﺅﺙﮒ۷ﮒﺎﻝﭘﮔﻝ؟۰?| `App.tsx` |
| **ﮒﺕﮒﺎﻝﭨﻛﭨﭘ** | Layout Components | ﻠ۰ﭖﻠ۱ﮒﺕﮒﺎﻝﭨﮔﺅﺙﮒﺁﺙﻟ۹ﮔ۰?| `Layout.tsx`, `Header.tsx` |
| **ﻠ۰ﭖﻠ۱ﻝﭨﻛﭨﭘ** | Page Components | ﻟﺓﺁﻝﺎﮒﺁﺗﮒﭦﻝﮒ؟ﮔﺑﻠ۰ﭖ?| `DashboardPage.tsx` |
| **ﮒ؟ﺗﮒ۷ﻝﭨﻛﭨﭘ** | Container Components | ﻛﺕﮒ۰ﻠﭨﻟﺝﮒ؟ﺗﮒ۷ﺅﺙﻝﭘﮔﻝ؟۰?| `DashboardContainer.tsx` |
| **ﮒﺎﻝ۳ﭦﻝﭨﻛﭨﭘ** | Presentational Components | ﻝﭦﺁUIﮒﺎﻝ۳ﭦﺅﺙﮔ ﻛﺕﮒ۰ﻠﭨﻟﺝ | `MetricCard.tsx` |
| **ﻟ۰۷ﮒﻝﭨﻛﭨﭘ** | Form Components | ﮔﺍﮔ؟ﻟﺝﮒ۴ﻛﺕﻠ۹?| `EngineConfigForm.tsx` |
| **ﮒﺝﻟ۰۷ﻝﭨﻛﭨﭘ** | Chart Components | ﮔﺍﮔ؟ﮒﺁﻟ۶?| `PerformanceChart.tsx` |
| **ﮒﺓ۴ﮒﺓﻝﭨﻛﭨﭘ** | Utility Components | ﻠﻝ۷ﮒﺓ۴ﮒﺓﻝﭨﻛﭨﭘ | `LoadingSpinner.tsx` |

## 2. ﮔ ﺕﮒﺟﻝﭨﻛﭨﭘﻟﺁ۵ﻝﭨﻟ؟ﺝﻟ؟۰

### 2.1 Layout ﮒﺕﮒﺎﻝﭨﻛﭨﭘ

#### 2.1.1 Header ﻝﭨﻛﭨﭘ
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
  // ﮒ؟ﻝﺍ?
};
```

**ﮒ­ﻝﭨﻛﭨﭘﻝﭨ?*:
```
Header
ﻗﻗﻗ Logo (Logoﻝﭨﻛﭨﭘ)
ﻗﻗﻗ UserMenu (ﻝ۷ﮔﺓﻟﮒ)
?  ﻗﻗﻗ UserAvatar (ﻝ۷ﮔﺓﮒ۳ﺑﮒ)
?  ﻗﻗﻗ UserInfo (ﻝ۷ﮔﺓﻛﺟ۰ﮔﺁ)
?  ﻗﻗﻗ LogoutButton (ﻠﮒﭦﮔ?
ﻗﻗﻗ NotificationBell (ﻠﻝ۴ﻠﻠ)
?  ﻗﻗﻗ NotificationList (ﻠﻝ۴ﮒﻟ۰۷)
ﻗﻗﻗ QuickActions (ﮒﺟ،ﮔﺓﮔﻛﺛ)
    ﻗﻗﻗ RefreshButton (ﮒﺓﮔﺍﮔﻠ؟)
    ﻗﻗﻗ HelpButton (ﮒﺕ؟ﮒ۸ﮔﻠ؟)
```

#### 2.1.2 Sidebar ﻝﭨﻛﭨﭘ
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
  // ﮒ؟ﻝﺍ?
};
```

**ﮒﺁﺙﻟ۹ﻟﮒ?*:
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
    label: 'ﻛﭦ۳ﮔﻝﮔ۶',
    path: '/trades'
  },
  {
    key: 'performance',
    icon: <LineChartOutlined />,
    label: 'ﮔ۶ﻟﺛﮒﮔ',
    path: '/performance'
  },
  {
    key: 'config',
    icon: <SettingOutlined />,
    label: 'ﻠﻝﺛ؟ﻝ؟۰ﻝ',
    path: '/config',
    children: [
      { key: 'engines', label: 'ﮒﺙﮔﻠﻝﺛ؟', path: '/config/engines' },
      { key: 'strategies', label: 'ﻝ­ﻝ۴ﻠﻝﺛ؟', path: '/config/strategies' },
      { key: 'risk', label: 'ﻠ۲ﻠ۸ﻠﻠ۱', path: '/config/risk' }
    ]
  },
  {
    key: 'system',
    icon: <MonitorOutlined />,
    label: 'ﻝﺏﭨﻝﭨﮒ۴ﮒﭦﺓ',
    path: '/system'
  }
];
```

### 2.2 DashboardPage ﻛﭨ۹ﻟ۰۷ﮔﺟﻠ۰ﭖ?

#### 2.2.1 ﻝﭨﻛﭨﭘﻝﭨﮔ
```
DashboardPage
ﻗﻗﻗ DashboardContainer
    ﻗﻗﻗ EngineStatusGrid
    ?  ﻗﻗﻗ EngineStatusCard (ﺣN)
    ?  ?  ﻗﻗﻗ EngineIcon (ﮒﺙﮔﮒﺝﮔ )
    ?  ?  ﻗﻗﻗ EngineName (ﮒﺙﮔﮒﻝ۶ﺍ)
    ?  ?  ﻗﻗﻗ StatusIndicator (ﻝﭘﮔﮔﻝ۳ﭦﮒ۷)
    ?  ?  ﻗﻗﻗ PerformanceMetrics (ﮔ۶ﻟﺛﮔﮔ )
    ?  ?  ﻗﻗﻗ ActionButtons (ﮔﻛﺛﮔﻠ؟)
    ?  ﻗﻗﻗ AddEngineCard (ﮔﺓﭨﮒ ﮒﺙﮔﮒ۰ﻝ)
    ﻗﻗﻗ MetricsOverview
    ?  ﻗﻗﻗ TotalTradesCard (ﮔﭨﻛﭦ۳ﮔﮔﺍ)
    ?  ﻗﻗﻗ TotalVolumeCard (ﮔﭨﻛﭦ۳ﮔﻠ۱)
    ?  ﻗﻗﻗ ActiveEnginesCard (ﮔﺑﭨﻟﺓﮒﺙﮔ)
    ?  ﻗﻗﻗ SystemHealthCard (ﻝﺏﭨﻝﭨﮒ۴ﮒﭦﺓ?
    ﻗﻗﻗ RecentAlertsPanel
    ?  ﻗﻗﻗ AlertItem (ﮒﻟ­۵?
    ?  ﻗﻗﻗ ViewAllAlertsButton (ﮔ۴ﻝﮒ۷ﻠ۷)
    ﻗﻗﻗ QuickActionsPanel
        ﻗﻗﻗ StartAllEnginesButton (ﮒﺁﮒ۷ﮔﮔﮒﺙ?
        ﻗﻗﻗ StopAllEnginesButton (ﮒﮔ­۱ﮔﮔﮒﺙ?
        ﻗﻗﻗ RunHealthCheckButton (ﻟﺟﻟ۰ﮒ۴ﮒﭦﺓﮔ۲?
```

#### 2.2.2 EngineStatusCard ﻝﭨﻛﭨﭘﻟ؟ﺝﻟ؟۰
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
        <Tooltip title="ﮒﺁﮒ۷">
          <PlayCircleOutlined onClick={() => onStart(engine.id)} />
        </Tooltip>,
        <Tooltip title="ﮒﮔ­۱">
          <StopOutlined onClick={() => onStop(engine.id)} />
        </Tooltip>,
        <Tooltip title="ﻠﻝﺛ؟">
          <SettingOutlined onClick={() => onConfigure(engine.id)} />
        </Tooltip>,
        <Tooltip title="ﻟﺁ۵ﮔ">
          <EyeOutlined onClick={() => onViewDetails(engine.id)} />
        </Tooltip>
      ]}
    >
      <div className="engine-metrics">
        <MetricItem label="CPU" value={`${engine.cpuUsage}%`} />
        <MetricItem label="ﮒﮒ­" value={`${engine.memoryUsage}%`} />
        <MetricItem label="ﻛﭨﮔ۴ﻛﭦ۳ﮔ" value={engine.tradesToday} />
        <MetricItem label="ﻠﻟﺁﺁ? value={engine.errorCount} />
      </div>
      <div className="engine-last-update">
        ﮔﮒﮔﺑ? {formatTime(engine.lastHeartbeat)}
      </div>
    </Card>
  );
};
```

### 2.3 TradeMonitorPage ﻛﭦ۳ﮔﻝﮔ۶ﻠ۰ﭖﻠ۱

#### 2.3.1 ﻝﭨﻛﭨﭘﻝﭨﮔ
```
TradeMonitorPage
ﻗﻗﻗ TradeMonitorContainer
    ﻗﻗﻗ TradeFilters
    ?  ﻗﻗﻗ DateRangePicker (ﮔ۴ﮔﻟﮒﺑﻠﮔ۸?
    ?  ﻗﻗﻗ SymbolSelector (ﮔ ﻝﻠﮔ۸?
    ?  ﻗﻗﻗ EngineSelector (ﮒﺙﮔﻠﮔ۸?
    ?  ﻗﻗﻗ SideFilter (ﻛﺗﺍﮒﮔﺗﮒﻟﺟﮔﭨ۳?
    ?  ﻗﻗﻗ ApplyFiltersButton (ﮒﭦﻝ۷ﻟﺟﮔﭨ۳?
    ﻗﻗﻗ TradeTable
    ?  ﻗﻗﻗ TradeTableHeader (ﻟ۰۷ﮔ ﺙﮒ۳ﺑﻠ۷)
    ?  ﻗﻗﻗ TradeTableRow (ﻟ۰۷ﮔ ﺙ?ﺣN)
    ?  ?  ﻗﻗﻗ TradeIdCell (ﻛﭦ۳ﮔID)
    ?  ?  ﻗﻗﻗ TimestampCell (ﮔﭘﻠﺑ?
    ?  ?  ﻗﻗﻗ SymbolCell (ﮔ ﻝ)
    ?  ?  ﻗﻗﻗ SideCell (ﻛﺗﺍﮒﮔﺗﮒ)
    ?  ?  ﻗﻗﻗ PriceCell (ﻛﭨﺓﮔ ﺙ)
    ?  ?  ﻗﻗﻗ QuantityCell (ﮔﺍﻠ)
    ?  ?  ﻗﻗﻗ VolumeCell (ﻠﻠ۱)
    ?  ?  ﻗﻗﻗ EngineCell (ﮒﺙﮔ)
    ?  ?  ﻗﻗﻗ ActionsCell (ﮔﻛﺛ)
    ?  ﻗﻗﻗ TradeTableFooter (ﻟ۰۷ﮔ ﺙﮒﭦﻠ۷)
    ﻗﻗﻗ TradeStatsPanel
    ?  ﻗﻗﻗ TotalTradesStat (ﮔﭨﻛﭦ۳ﮔﮔﺍ)
    ?  ﻗﻗﻗ TotalVolumeStat (ﮔﭨﻛﭦ۳ﮔﻠ۱)
    ?  ﻗﻗﻗ AvgPriceStat (ﮒﺗﺏﮒﻛﭨﺓﮔ ﺙ)
    ?  ﻗﻗﻗ TradeDistributionChart (ﻛﭦ۳ﮔﮒﮒﺕ?
    ﻗﻗﻗ TradeDetailModal (ﻛﭦ۳ﮔﻟﺁ۵ﮔﮔ۷۰ﮔﮔ۰)
```

#### 2.3.2 TradeTable ﻝﭨﻛﭨﭘﻟ؟ﺝﻟ؟۰
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
      title: 'ﻛﭦ۳ﮔID',
      dataIndex: 'tradeId',
      key: 'tradeId',
      sorter: true,
      width: 120
    },
    {
      title: 'ﮔﭘﻠﺑ',
      dataIndex: 'timestamp',
      key: 'timestamp',
      sorter: true,
      render: (timestamp: string) => formatDateTime(timestamp),
      width: 150
    },
    {
      title: 'ﮔ ﻝ',
      dataIndex: 'symbol',
      key: 'symbol',
      width: 100
    },
    {
      title: 'ﮔﺗﮒ',
      dataIndex: 'side',
      key: 'side',
      render: (side: string) => (
        <Tag color={side === 'buy' ? 'green' : 'red'}>
          {side === 'buy' ? 'ﻛﺗﺍﮒ۴' : 'ﮒﮒﭦ'}
        </Tag>
      ),
      width: 80
    },
    {
      title: 'ﻛﭨﺓﮔ ﺙ',
      dataIndex: 'price',
      key: 'price',
      sorter: true,
      render: (price: number) => formatCurrency(price),
      width: 100
    },
    {
      title: 'ﮔﺍﻠ',
      dataIndex: 'quantity',
      key: 'quantity',
      sorter: true,
      width: 100
    },
    {
      title: 'ﻠﻠ۱',
      dataIndex: 'volume',
      key: 'volume',
      sorter: true,
      render: (volume: number) => formatCurrency(volume),
      width: 120
    },
    {
      title: 'ﮒﺙﮔ',
      dataIndex: 'engineId',
      key: 'engineId',
      width: 100
    },
    {
      title: 'ﮔﻛﺛ',
      key: 'actions',
      render: (_: any, trade: Trade) => (
        <Button
          type="link"
          onClick={() => onRowClick(trade)}
          icon={<EyeOutlined />}
        >
          ﻟﺁ۵ﮔ
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

### 2.4 PerformancePage ﮔ۶ﻟﺛﮒﮔﻠ۰ﭖﻠ۱

#### 2.4.1 ﻝﭨﻛﭨﭘﻝﭨﮔ
```
PerformancePage
ﻗﻗﻗ PerformanceContainer
    ﻗﻗﻗ ChartControls
    ?  ﻗﻗﻗ TimeRangeSelector (ﮔﭘﻠﺑﻟﮒﺑﻠﮔ۸?
    ?  ﻗﻗﻗ MetricSelector (ﮔﮔ ﻠﮔ۸?
    ?  ﻗﻗﻗ ChartTypeSelector (ﮒﺝﻟ۰۷ﻝﺎﭨﮒﻠﮔ۸?
    ?  ﻗﻗﻗ EngineFilter (ﮒﺙﮔﻟﺟﮔﭨ۳?
    ?  ﻗﻗﻗ RefreshButton (ﮒﺓﮔﺍﮔﻠ؟)
    ﻗﻗﻗ ChartArea
    ?  ﻗﻗﻗ EquityCurveChart (ﮔﻝﮔﺎﻝﭦﺟ?
    ?  ﻗﻗﻗ DrawdownChart (ﮒﮔ۳?
    ?  ﻗﻗﻗ SharpeRatioChart (ﮒ۳ﮔ؟ﮔﺁﻝ?
    ?  ﻗﻗﻗ TradeDistributionChart (ﻛﭦ۳ﮔﮒﮒﺕ?
    ?  ﻗﻗﻗ PerformanceHeatmap (ﮔ۶ﻟﺛﻝ­ﮒ?
    ﻗﻗﻗ PerformanceMetricsPanel
    ?  ﻗﻗﻗ SharpeRatioCard (ﮒ۳ﮔ؟ﮔﺁﻝ)
    ?  ﻗﻗﻗ MaxDrawdownCard (ﮔﮒ۳۶ﮒ?
    ?  ﻗﻗﻗ WinRateCard (ﻟﻝ)
    ?  ﻗﻗﻗ AvgReturnCard (ﮒﺗﺏﮒﮔﭘﻝ)
    ?  ﻗﻗﻗ VolatilityCard (ﮔﺏ۱ﮒ۷?
    ﻗﻗﻗ ExportControls
        ﻗﻗﻗ ExportCSVButton (ﮒﺁﺙﮒﭦCSV)
        ﻗﻗﻗ ExportPNGButton (ﮒﺁﺙﮒﭦPNG)
        ﻗﻗﻗ ShareReportButton (ﮒﻛﭦ،ﮔ۴ﮒ)
```

#### 2.4.2 PerformanceChart ﻝﭨﻛﭨﭘﻟ؟ﺝﻟ؟۰
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

## 3. ﻝﭨﻛﭨﭘﻛﭦ۳ﻛﭦﮒﺏﻝﺏﭨ

### 3.1 ﮔﺍﮔ؟ﮔﭖﮒﺝ

```mermaid
graph LR
    A[ﮒﻝ،ﺁAPI] --> B[API Service]
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

### 3.2 ﻝﭘﮔﻝ؟۰ﻝﻟ؟ﺝ?

#### 3.2.1 Redux Store ﻝﭨﮔ
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

#### 3.2.2 ﮒﺏﻠ؟Actionﮒ؟ﻛﺗ
```typescript
// ﮒﺙﮔﻝﺕﮒﺏAction
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

// ﻛﭦ۳ﮔﻝﺕﮒﺏAction
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

## 4. ﻝﭨﻛﭨﭘﮒﺙﮒﻟ۶?

### 4.1 ﮒﺛﮒﻟ۶ﻟ
| ﻝﭨﻛﭨﭘﻝﺎﭨﮒ | ﮒﺛﮒﻟ۶ﮒ | ﻝ۳ﭦﻛﺝ |
|----------|----------|------|
| **ﻠ۰ﭖﻠ۱ﻝﭨﻛﭨﭘ** | `[PageName]Page` | `DashboardPage.tsx` |
| **ﮒ؟ﺗﮒ۷ﻝﭨﻛﭨﭘ** | `[Feature]Container` | `DashboardContainer.tsx` |
| **ﮒﺎﻝ۳ﭦﻝﭨﻛﭨﭘ** | `[ComponentName]` | `MetricCard.tsx` |
| **ﻟ۰۷ﮒﻝﭨﻛﭨﭘ** | `[FormName]Form` | `EngineConfigForm.tsx` |
| **ﮒﺝﻟ۰۷ﻝﭨﻛﭨﭘ** | `[ChartName]Chart` | `PerformanceChart.tsx` |
| **ﮒﺓ۴ﮒﺓﻝﭨﻛﭨﭘ** | `[UtilityName]` | `LoadingSpinner.tsx` |

### 4.2 ﮔﻛﭨﭘﻝﭨﮔﻟ۶ﻟ
```
src/
ﻗﻗﻗ components/
?  ﻗﻗﻗ layout/           # ﮒﺕﮒﺎﻝﭨﻛﭨﭘ
?  ?  ﻗﻗﻗ Header.tsx
?  ?  ﻗﻗﻗ Sidebar.tsx
?  ?  ﻗﻗﻗ Layout.tsx
?  ﻗﻗﻗ pages/           # ﻠ۰ﭖﻠ۱ﻝﭨﻛﭨﭘ
?  ?  ﻗﻗﻗ DashboardPage.tsx
?  ?  ﻗﻗﻗ TradeMonitorPage.tsx
?  ?  ﻗﻗﻗ PerformancePage.tsx
?  ﻗﻗﻗ containers/      # ﮒ؟ﺗﮒ۷ﻝﭨﻛﭨﭘ
?  ?  ﻗﻗﻗ DashboardContainer.tsx
?  ?  ﻗﻗﻗ TradeMonitorContainer.tsx
?  ?  ﻗﻗﻗ PerformanceContainer.tsx
?  ﻗﻗﻗ charts/         # ﮒﺝﻟ۰۷ﻝﭨﻛﭨﭘ
?  ?  ﻗﻗﻗ PerformanceChart.tsx
?  ?  ﻗﻗﻗ TradeDistributionChart.tsx
?  ﻗﻗﻗ forms/          # ﻟ۰۷ﮒﻝﭨﻛﭨﭘ
?  ?  ﻗﻗﻗ EngineConfigForm.tsx
?  ?  ﻗﻗﻗ StrategyConfigForm.tsx
?  ﻗﻗﻗ common/         # ﻠﻝ۷ﻝﭨﻛﭨﭘ
?      ﻗﻗﻗ LoadingSpinner.tsx
?      ﻗﻗﻗ ErrorBoundary.tsx
?      ﻗﻗﻗ NotFound.tsx
ﻗﻗﻗ services/           # ﮔﮒ۰?
?  ﻗﻗﻗ api.ts
?  ﻗﻗﻗ websocket.ts
?  ﻗﻗﻗ auth.ts
ﻗﻗﻗ store/              # ﻝﭘﮔﻝ؟۰?
?  ﻗﻗﻗ index.ts
?  ﻗﻗﻗ actions.ts
?  ﻗﻗﻗ reducers.ts
?  ﻗﻗﻗ selectors.ts
ﻗﻗﻗ hooks/              # ﻟ۹ﮒ؟ﻛﺗHook
?  ﻗﻗﻗ useEngines.ts
?  ﻗﻗﻗ useTrades.ts
?  ﻗﻗﻗ useWebSocket.ts
ﻗﻗﻗ utils/              # ﮒﺓ۴ﮒﺓﮒﺛﮔﺍ
?  ﻗﻗﻗ formatters.ts
?  ﻗﻗﻗ validators.ts
?  ﻗﻗﻗ constants.ts
ﻗﻗﻗ types/              # TypeScriptﻝﺎﭨﮒﮒ؟ﻛﺗ
    ﻗﻗﻗ index.ts
    ﻗﻗﻗ engine.ts
    ﻗﻗﻗ trade.ts
```

### 4.3 ﻝﭨﻛﭨﭘﮒﺙﮒﮒ?

#### 4.3.1 ﮒﻛﺕﻟﻟﺑ۲ﮒﮒ
- ﮔﺁﻛﺕ۹ﻝﭨﻛﭨﭘﮒ۹ﻟﺑﻟﺑ۲ﻛﺕﻛﺕ۹ﮒ?
- ﮒ؟ﺗﮒ۷ﻝﭨﻛﭨﭘﻟﺑﻟﺑ۲ﻝﭘﮔﻝ؟۰ﻝﮒﻛﺕﮒ۰ﻠﭨﻟﺝ
- ﮒﺎﻝ۳ﭦﻝﭨﻛﭨﭘﮒ۹ﻟﺑﻟﺑ۲UIﮔﺕﺎﮔ

#### 4.3.2 ﮒﺁﮒ۳ﻝ۷ﮔ۶ﮒ?
- ﮔﮒﻠﻝ۷ﻝﭨﻛﭨﭘﮒﺍ`common/`ﻝ؟ﮒﺛ
- ﻝﭨﻛﭨﭘﮒﮔﺍﻟ؟ﺝﻟ؟۰ﻟ۵ﻝﭖ?
- ﮔﺁﮔﻟ۹ﮒ؟ﻛﺗﮔ ﺓﮒﺙﮒﻛﭦﻛﭨﭘ

#### 4.3.3 ﮒﺁﮔﭖﻟﺁﮔ۶ﮒ?
- ﻝﭨﻛﭨﭘﻠﭨﻟﺝﻛﺕUIﮒﻝ۵ﭨ
- ﻛﺛﺟﻝ۷Propsﮔﺏ۷ﮒ۴ﻛﺝﻟﭖ
- ﮔﻛﺝﮔﭖﻟﺁﮒﮒ۴ﺛﻝﮔ۴?

#### 4.3.4 ﮔ۶ﻟﺛﻛﺙﮒﮒﮒ
- ﻛﺛﺟﻝ۷React.memoﻠﺟﮒﻛﺕﮒﺟﻟ۵ﻝﻠﮔﺕﺎ?
- ﻛﺛﺟﻝ۷useMemo/useCallbackﻛﺙﮒﻟ؟۰ﻝ؟
- ﮒ؟ﻝﺍﻟﮔﮔﭨﮒ۷ﮒ۳ﻝﮒ۳۶ﮔﺍﮔ؟ﮒ?
- ﮔﻠﮒ ﻟﺛﺛﮒ۳۶ﮒﻝﭨﻛﭨﭘ

## 5. ﮒ؟ﮔﺛﮔﮒ

### 5.1 ﻝﭨﻛﭨﭘﮒﺙﮒﻠ۰ﭦ?
1. **ﮒﭦﻝ۰ﻝﭨﻛﭨﭘ** (??
   - Layoutﻝﭨﻛﭨﭘ (Header, Sidebar, Footer)
   - ﻠﻝ۷ﻝﭨﻛﭨﭘ (LoadingSpinner, ErrorBoundary)
   - ﮒﺓ۴ﮒﺓﮒﺛﮔﺍﮒﻝﺎﭨﮒﮒ؟?

2. **ﻠ۰ﭖﻠ۱ﮔ۰ﮔﭘ** (??
   - ﻠ۰ﭖﻠ۱ﻟﺓﺁﻝﺎﻠﻝﺛ؟
   - ﻠ۰ﭖﻠ۱ﻠ۹۷ﮔﭘﻝﭨﻛﭨﭘ
   - ﮒﺁﺙﻟ۹ﮒﮔﻠﮔ۶?

3. **ﮔ ﺕﮒﺟﮒﻟﺛﻝﭨﻛﭨﭘ** (?-4?
   - Dashboardﻝﺕﮒﺏﻝﭨﻛﭨﭘ
   - TradeMonitorﻝﺕﮒﺏﻝﭨﻛﭨﭘ
   - Performanceﻝﺕﮒﺏﻝﭨﻛﭨﭘ

4. **ﻠ،ﻝﭦ۶ﮒﻟﺛﻝﭨﻛﭨﭘ** (??
   - Configﻝﺕﮒﺏﻝﭨﻛﭨﭘ
   - SystemHealthﻝﺕﮒﺏﻝﭨﻛﭨﭘ
   - ﮒﺁﺙﮒﭦﮒﮒﻛﭦ،ﮒ?

5. **ﻛﺙﮒﮒﮔﭖ?* (?-7?
   - ﮔ۶ﻟﺛﻛﺙﮒ
   - ﮒﮒﭦﮒﺙﻟ؟ﺝ?
   - ﮒﮒﮔﭖﻟﺁﮒE2Eﮔﭖﻟﺁ

### 5.2 ﻝﭨﻛﭨﭘﮔﭖﻟﺁﻝ­ﻝ۴
| ﮔﭖﻟﺁﻝﺎﭨﮒ | ﮔﭖﻟﺁﮒﺓ۴ﮒﺓ | ﮔﭖﻟﺁﻝ؟ﮔ  | ﻟ۵ﻝﻝﻝ؟?|
|----------|----------|----------|------------|
| **ﮒﮒﮔﭖﻟﺁ** | Jest + React Testing Library | ﻝﭨﻛﭨﭘﻠﭨﻟﺝﮒﮔﺕﺎ?| ?0% |
| **ﻠﮔﮔﭖﻟﺁ** | Cypress | ﻝﭨﻛﭨﭘﻠﺑﻛﭦ۳?| ?0% |
| **E2Eﮔﭖﻟﺁ** | Cypress | ﮒ؟ﮔﺑﻝ۷ﮔﺓﮔﭖﻝ۷ | ?0% |
| **ﮔ۶ﻟﺛﮔﭖﻟﺁ** | Lighthouse | ﮒ ﻟﺛﺛﮒﮔﺕﺎﮔﮔ۶ﻟﺛ | ﻟﺝﺝﮔ  |
| **ﮒﺁﻟ۶ﮒﮔﭖ?* | Storybook + Chromatic | UIﻛﺕﻟﺑﮔ۶ﮒﮒﮒﺛ | 100% |

### 5.3 ﻝﭨﻛﭨﭘﮔﮔ۰۲ﻟ۶ﻟ
ﮔﺁﻛﺕ۹ﻝﭨﻛﭨﭘﻠﻟ۵ﮒﮒ،ﺅﺙ
1. **ﻝﭨﻛﭨﭘﻟﺁﺑﮔ**: ﻝ۷ﻠﻙﮒﻟﺛﻙﻛﺛﺟﻝ۷ﮒﭦ?
2. **Propsﮔ۴ﮒ۲**: TypeScriptﮔ۴ﮒ۲ﮒ؟ﻛﺗ
3. **ﻛﺛﺟﻝ۷ﻝ۳ﭦﻛﺝ**: ﻛﭨ۲ﻝ ﻝ۳ﭦﻛﺝ
4. **ﮔﺏ۷ﮔﻛﭦﻠ۰ﺗ**: ﻛﺛﺟﻝ۷ﻠﮒﭘﮒﮔﻛﺛﺏﮒ؟?
5. **APIﮔﮔ۰۲**: ﮔﺗﮔﺏﮒﻛﭦﻛﭨﭘﻟﺁﺑ?

---

**ﮔﮔ۰۲ﻝﮔ؛**: 1.0.0  
**ﮔﮒﮔﺑ?*: 2026-04-02  
**ﻝﭨﺑﮔ۳?*: ﻠ۵ﮒﺕ­ﻟﮒﺝﮔﭘﮔ? 
**ﻝﺑ۱ﮒﺙ**: `DESIGN_004`  
**ﻝ?*: ?ﻟ؟ﺝﻟ؟۰ﮒ؟ﮔﺅﺙﮒﺝﻟﺁﮒ؟۰