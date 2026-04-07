---
module_id: A_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 文档管理员
responsibility:
  - 蓝图设计、架构规划
layer: Layer 2 (Alpha因子层)
standard_type: 专业量化机构蓝图
applicable_scope: 全系统
compliance_level: 专业标准
---
---


﻿---
standard_type: 蓝图标准
applicable_scope: å
¨ç³»ç»?
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 设计阶段
owner: ææ¡£ç»´æ¤è?
version: 1.0.0
module_id: DOC_TEMP_A_STOCK_BLUEPRI
created_date: 2026-04-01
last_updated: 2026-04-02
---
# Aè¡åå²æ°æ®å¤çä¸æ°æ®åºéæèå?
> **核心职责**: A Stock Data Processing蓝图设计
> **职责边界**: 
> - ✅ 本文档负责：A Stock Data Processing蓝图设计相关内容
> - ❌ 本文档不负责：其他模块内容


## 1. 数据现状分析

### 1.1 目录结构概览
```
D:\ZephyrAlpha\A股数据\量化交易数据\
âââ Aè¡_åæ¶æ°æ®/           # åéçº§è¡æ
æ°æ?(5åéã?5åéã?0åéã?0åé)
âââ Aè¡æ°æ?               # åå§æ°æ®ï¼å¯è½ä¸ºå¤ä»½ææªåç±»æ°æ®ï¼?
âââ Aè¡æ°æ®_zip/           # åç¼©çè¡æ
æ°æ®æä»?
â?  âââ daily.zip         # æ¥çº¿æ°æ®ï¼æªå¤æï¼?
â?  âââ daily_qfq.zip     # æ¥çº¿æ°æ®ï¼åå¤æï¼?
â?  âââ daily_hfq.zip     # æ¥çº¿æ°æ®ï¼åå¤æï¼?
â?  âââ weekly.zip        # å¨çº¿æ°æ®
â?  âââ monthly.zip       # æçº¿æ°æ®
â?  âââ ...å
¶ä»é¢çæ°æ®
âââ CSVè¡æ
æ°æ®/           # å·²è§£åçCSVæ ¼å¼è¡æ
数据
â?  âââ 000002.csv        # ååªè¡ç¥¨æ¥çº¿æ°æ®
â?  âââ 000858_5min.csv   # ååªè¡ç¥¨5åéæ°æ®
â?  âââ ...å
¶ä»è¡ç¥¨æä»¶
âââ ä¸å¸å
¬å¸è´¢å¡ä¿¡æ¯/       # è´¢å¡æ°æ®
â?  âââ åå²è¯¦ç»æ°æ®/
â?  â?  âââ å
¨é¨ä¸å¸å
¬å¸è´¢å¡ä¿¡æ¯_20250930.xlsx
â?  â?  âââ å
¨é¨ä¸å¸å
¬å¸è´¢å¡ä¿¡æ¯_20250630.xlsx
â?  â?  âââ ...åå²å­£åº¦æ°æ®
â?  âââ ææ°æ°æ?
âââ å¤æå å­/              # å¤æè®¡ç®ç¸å
³èæ¬åæ°æ?
```

### 1.2 æ°æ®æ ¼å¼ä¸ç¹å¾?

#### 1.2.1 è¡æ
数据格式
**日线数据 (000002.csv)**:
```csv
date,code,open,high,low,close,pre_close,change,pct_chg,vol,amount,adj_factor,turnover_rate,pe_ttm,pb,ps,pcf,is_st
2025-10-15,sz000002,12.34,12.56,12.12,12.45,12.30,0.15,1.22,1234567,15432100,1.0,0.85,8.76,1.23,2.34,5.67,0
```

**5分钟数据 (000858_5min.csv)**:
```csv
date,open,high,low,close,volume,code
2025-10-14 10:15:00,120.49,120.65,120.41,120.65,455272,sz000858
```

#### 1.2.2 财务数据格式
**Excel格式财务数据**:
- æä»¶: `å
¨é¨ä¸å¸å
¬å¸è´¢å¡ä¿¡æ¯_20250930.xlsx`
- æ°æ®é? 250+ è´¢å¡ææ å­æ®µ
- å
含: 资产负债表、利润表、现金流量表、财务比率、估值指标等
- æ¶é´è·¨åº¦: åå²å­£åº¦æ°æ®ï¼æå­£åº¦æä»¶å­å¨ï¼?

#### 1.2.3 压缩数据格式
**ZIP文件结构**:
- `daily.zip`: æ¥çº¿æªå¤ææ°æ?
- `daily_qfq.zip`: æ¥çº¿åå¤ææ°æ? 
- `daily_hfq.zip`: æ¥çº¿åå¤ææ°æ?
- `weekly.zip`: 周线数据
- `monthly.zip`: 月线数据

## 2. 总体处理架构设计

### 2.1 åå±å¤çæµæ°´çº?
```
åå§æ°æ®å±?â?æåè§£åå±?â?æ¸
æ´æ ååå± â?åç±»å­å¨å±?â?æ°æ®åºå±
    â?            â?             â?             â?           â?
   CSV/ZIP    æ°æ®è§£å      æ°æ®æ¸
洗        数据分类      SQLite/Parquet
   Excel      格式转换      异常处理        维度划分      数据仓库
```

### 2.2 技术栈选择
| 组件 | 技术选择 | 理由 |
|------|----------|------|
| **æ°æ®æå** | Python `zipfile`, `pandas` | åçæ¯æï¼å
存效率高 |
| **æ°æ®æ¸
æ´** | `pandas`, `numpy` | å¼ºå¤§çæ°æ®æä½è½å?|
| **æ°æ®å­å¨** | **SQLite** (å
æ°æ? + **Parquet** (è¡æ
数据) | 查询效率+存储压缩 |
| **ä»»å¡è°åº¦** | Python `multiprocessing` | ç®åæç¨ï¼éåä¸ªäººå¼å?|
| **çæ§æ¥å¿** | Python `logging` + è¿åº¦æ?| å®æ¶åé¦ï¼æäºè°è¯?|

## 3. æ°æ®æåä¸è§£åæ¹æ¡?

### 3.1 提取策略

#### 3.1.1 ZIP文件批量解压
```python
import zipfile
import os
from pathlib import Path

class ZipExtractor:
    def __init__(self, zip_dir, output_dir):
        self.zip_dir = Path(zip_dir)
        self.output_dir = Path(output_dir)
        
    def extract_all(self, force=False):
        """批量解压所有ZIP文件"""
        zip_files = list(self.zip_dir.glob("*.zip"))
        
        for zip_file in zip_files:
            output_subdir = self.output_dir / zip_file.stem
            if output_subdir.exists() and not force:
                print(f"è·³è¿å·²è§£å? {zip_file.name}")
                continue
                
            print(f"解压: {zip_file.name}")
            with zipfile.ZipFile(zip_file, 'r') as zf:
                zf.extractall(output_subdir)
                
    def get_extracted_structure(self):
        """获取解压后的文件结构"""
        structure = {}
        for item in self.output_dir.rglob("*"):
            if item.is_file():
                rel_path = item.relative_to(self.output_dir)
                structure.setdefault(rel_path.parent, []).append(rel_path.name)
        return structure
```

#### 3.1.2 CSV文件批量读取
```python
import pandas as pd
from concurrent.futures import ProcessPoolExecutor

class CSVReader:
    def __init__(self, csv_dir):
        self.csv_dir = Path(csv_dir)
        
    def read_single_file(self, csv_path):
        """读取单个CSV文件"""
        try:
            df = pd.read_csv(csv_path)
            # æ·»å æä»¶åä½ä¸ºæ°æ®æ¥æºæ è®?
            df['source_file'] = csv_path.name
            return df
        except Exception as e:
            print(f"读取失败 {csv_path}: {e}")
            return None
            
    def read_all_files(self, pattern="*.csv", max_workers=4):
        """并行读取所有CSV文件"""
        csv_files = list(self.csv_dir.rglob(pattern))
        data_frames = []
        
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self.read_single_file, f) for f in csv_files]
            for future in futures:
                result = future.result()
                if result is not None:
                    data_frames.append(result)
                    
        return pd.concat(data_frames, ignore_index=True) if data_frames else pd.DataFrame()
```

#### 3.1.3 Excel财务数据读取
```python
class FinancialDataReader:
    def __init__(self, excel_dir):
        self.excel_dir = Path(excel_dir)
        
    def read_quarterly_data(self):
        """è¯»åææå­£åº¦è´¢å¡æ°æ?""
        quarter_files = sorted(self.excel_dir.glob("å
¨é¨ä¸å¸å
¬å¸è´¢å¡ä¿¡æ¯_*.xlsx"))
        all_data = []
        
        for file_path in quarter_files:
            # 从文件名提取季度信息
            quarter_str = file_path.stem.split('_')[-1]  # å¦?20250930
            quarter_date = pd.to_datetime(quarter_str, format='%Y%m%d')
            
            print(f"读取: {file_path.name}")
            df = pd.read_excel(file_path, dtype={'股票代码': str})
            df['report_date'] = quarter_date
            df['data_type'] = 'financial'
            
            all_data.append(df)
            
        return pd.concat(all_data, ignore_index=True)
```

### 3.2 解压目录结构规划
```
processed_data/
├── extracted/                    # 解压后的原始文件
â?  âââ daily/                   # æ¥çº¿æ°æ®
â?  âââ daily_qfq/              # åå¤ææ¥çº?
â?  âââ daily_hfq/              # åå¤ææ¥çº?
â?  âââ weekly/                 # å¨çº¿æ°æ®
â?  âââ monthly/                # æçº¿æ°æ®
├── raw_csv/                     # 原始CSV数据（保持原样）
├── raw_financial/               # 原始财务数据（保持原样）
âââ metadata/                    # å
æ°æ®æä»?
    ├── file_index.json         # 文件索引
    ├── data_schema.json        # 数据模式定义
    └── extraction_log.csv      # 提取日志
```

## 4. æ°æ®æ¸
洗与标准化流程

### 4.1 æ¸
洗规则定义

#### 4.1.1 è¡æ
æ°æ®æ¸
洗规则
| å­æ®µ | æ¸
洗规则 | 异常处理 |
|------|----------|----------|
| **date** | è½¬æ¢ä¸ºdatetimeæ ¼å¼ï¼éªè¯æ¥ææææ?| æ ææ¥ææ è®°ä¸ºNaTï¼å¯æå?|
| **code** | 标准化为`交易所.代码`格式 (如`SZ.000002`) | 无效代码删除整行 |
| **price** | ä»·æ ¼>0ï¼å¼çâ¤æé«â¥æä½â¤æ¶ç | ä»·æ ¼å¼å¸¸æ è®°å¹¶æå?|
| **volume** | æäº¤éâ¥0 | è´å¼è®¾ä¸? |
| **amount** | æäº¤é¢â¥0ï¼ä¸ä»·æ ¼*volumeä¸è?| ä¸ä¸è´æ¶éæ°è®¡ç® |
| **pct_chg** | æ¶¨è·å¹
å¨[-10%, 10%]åçèå´ | è¶
åºèå´ä½¿ç¨åå¼å¡«å
?|

#### 4.1.2 è´¢å¡æ°æ®æ¸
洗规则
| å­æ®µç±»å | æ¸
洗规则 | 说明 |
|----------|----------|------|
| **ä»£ç å­æ®µ** | ç»ä¸ä¸?ä½æ°å­ä»£ç ï¼è¡¥åå¯? | ä¾¿äºå
³èè¡æ
数据 |
| **æ°å¼å­æ®?* | æ¿æ¢"NaN"ã?-"ãç©ºå¼ä¸ºnp.nan | ä¿ææ°æ®ä¸è´æ?|
| **ææ¬å­æ®µ** | å»é¤é¦å°¾ç©ºæ ¼ï¼ç»ä¸ç¼ç ä¸ºUTF-8 | é¿å
ç¼ç é®é¢ |
| **日期字段** | 转换为datetime格式 | 统一时间处理 |

### 4.2 标准化处理类

```python
class DataCleaner:
    def __init__(self):
        self.rules = self._load_cleaning_rules()
        
    def clean_market_data(self, df):
        """æ¸
æ´è¡æ
数据"""
        # 1. ä»£ç æ åå?
        df['code'] = df['code'].apply(self._standardize_code)
        
        # 2. æ¥ææ åå?
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # 3. 价格数据验证
        price_cols = ['open', 'high', 'low', 'close']
        for col in price_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            # ä»·æ ¼å¿
é¡»ä¸ºæ­£æ?
            df.loc[df[col] <= 0, col] = np.nan
            
        # 4. é»è¾å
³ç³»éªè¯
        df = self._validate_price_logic(df)
        
        # 5. ç¼ºå¤±å¼å¤ç?
        df = self._handle_missing_values(df)
        
        return df
        
    def clean_financial_data(self, df):
        """æ¸
洗财务数据"""
        # 1. ä»£ç æ åå?
        if '股票代码' in df.columns:
            df['stock_code'] = df['股票代码'].astype(str).str.zfill(6)
            
        # 2. æ°å¼å­æ®µå¤ç?
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        # 3. 文本字段处理
        text_cols = df.select_dtypes(include=[object]).columns
        for col in text_cols:
            df[col] = df[col].astype(str).str.strip()
            
        # 4. å»é¤å
¨ä¸ºNaNçè¡
        df = df.dropna(how='all')
        
        return df
        
    def _standardize_code(self, code):
        """æ ååè¡ç¥¨ä»£ç ?""
        if pd.isna(code):
            return None
            
        code_str = str(code)
        # ç§»é¤ç©ºæ ¼åç¹æ®å­ç¬?
        code_str = re.sub(r'[^a-zA-Z0-9]', '', code_str)
        
        # æ ååæ ¼å¼? SZ.000002 æ?SH.600000
        if code_str.startswith(('sz', 'SZ')):
            return f"SZ.{code_str[2:]}"
        elif code_str.startswith(('sh', 'SH')):
            return f"SH.{code_str[2:]}"
        else:
            # 假设6位数字代码，自动添加交易所
            if len(code_str) == 6:
                if code_str.startswith(('0', '3')):
                    return f"SZ.{code_str}"
                elif code_str.startswith(('6', '9')):
                    return f"SH.{code_str}"
            return code_str
```

### 4.3 异常检测与处理

```python
class AnomalyDetector:
    def detect_price_anomalies(self, df):
        """æ£æµä»·æ ¼å¼å¸?""
        anomalies = []
        
        # 1. ä»·æ ¼è·³å¨æ£æµ?(æ¥å
æ¶¨è·å¹
è¿å¤?
        df['pct_change'] = df['close'].pct_change()
        large_jumps = df[abs(df['pct_change']) > 0.2]  # 20%以上跳动
        
        # 2. æäº¤éå¼å¸¸æ£æµ?
        volume_mean = df['volume'].rolling(20).mean()
        volume_std = df['volume'].rolling(20).std()
        volume_anomalies = df[df['volume'] > (volume_mean + 3 * volume_std)]
        
        # 3. ä»·æ ¼å
³ç³»å¼å¸¸ (å¼ç?æé«? æä½?æ¶çç­?
        logic_anomalies = df[
            (df['open'] > df['high']) | 
            (df['low'] > df['close']) |
            (df['high'] < df['low'])
        ]
        
        return {
            'price_jumps': large_jumps,
            'volume_anomalies': volume_anomalies,
            'logic_errors': logic_anomalies
        }
        
    def impute_missing_values(self, df):
        """ç¼ºå¤±å¼æå?""
        # ååå¡«å

 (适用于交易日数据)
        df_filled = df.fillna(method='ffill')
        
        # çº¿æ§æå?(éç¨äºè¿ç»­æ¶é´åºå?
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df_filled[numeric_cols] = df_filled[numeric_cols].interpolate(method='linear')
        
        # ååå¡«å

å©ä½ç¼ºå¤±å?
        df_filled = df_filled.fillna(method='bfill')
        
        return df_filled
```

## 5. æ°æ®åç±»ä¸ç»´åº¦åå?

### 5.1 分类体系设计

#### 5.1.1 ææ°æ®ç±»ååç±?
```
数据分类体系:
âââ è¡æ
数据
â?  âââ æ¥çº¿æ°æ® (daily)
â?  â?  âââ æªå¤æ?(raw)
â?  â?  âââ åå¤æ?(qfq)
â?  â?  âââ åå¤æ?(hfq)
â?  âââ å¨çº¿æ°æ® (weekly)
â?  âââ æçº¿æ°æ® (monthly)
â?  âââ åéæ°æ® (intraday)
â?      âââ 5åé (5min)
â?      âââ 15åé (15min)
â?      âââ 30åé (30min)
â?      âââ 60åé (60min)
├── 财务数据
â?  âââ èµäº§è´åºè¡¨ (balance_sheet)
â?  âââ å©æ¶¦è¡?(income_statement)
â?  âââ ç°éæµéè¡?(cash_flow)
â?  âââ è´¢å¡æ¯ç (financial_ratios)
├── 基础信息数据
â?  âââ è¡ç¥¨åè¡¨ (stock_list)
â?  âââ è¡ä¸åç±» (industry)
â?  âââ ææ°æå (index_constituents)
└── 衍生数据
    âââ ææ¯ææ ?(technical_indicators)
    ├── 因子数据 (factors)
    └── 回测结果 (backtest_results)
```

#### 5.1.2 ææ¶é´ç»´åº¦åç±?
- **åå²å
¨éæ°æ®**: ææåå²æ°æ®ï¼ç¨äºæ¨¡åè®­ç»
- **滚动窗口数据**: 最近N年数据，用于实时分析
- **季度切片数据**: 按财务季度划分，用于季报分析
- **å¹´åº¦æ±æ»æ°æ?*: æå¹´åº¦æ±æ»ï¼ç¨äºå¹´åº¦å¯¹æ¯

### 5.2 分类处理实现

```python
class DataClassifier:
    def __init__(self):
        self.classification_rules = self._load_classification_rules()
        
    def classify_by_frequency(self, df, date_col='date'):
        """æé¢çåç±»æ°æ?""
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col])
        
        # 计算时间间隔
        time_diff = df[date_col].diff().dropna()
        if len(time_diff) > 0:
            mode_interval = time_diff.mode().iloc[0]
            
            if mode_interval.days >= 28:
                return 'monthly'
            elif mode_interval.days >= 7:
                return 'weekly'
            elif mode_interval.days == 1:
                return 'daily'
            elif mode_interval.total_seconds() <= 3600:  # 1å°æ¶ä»¥å

                return 'intraday'
                
        return 'unknown'
        
    def classify_by_content(self, df):
        """æå
å®¹åç±»æ°æ?""
        column_set = set(df.columns)
        
        # è´¢å¡æ°æ®ç¹å¾å?
        financial_keywords = ['èµäº§', 'è´å?, 'å©æ¶¦', 'æ¶å
¥', 'ç°éæµ?, 'æ¯ç']
        financial_cols = [col for col in column_set 
                         if any(keyword in str(col) for keyword in financial_keywords)]
        
        # è¡æ
æ°æ®ç¹å¾å?
        market_keywords = ['open', 'high', 'low', 'close', 'volume', 'amount']
        market_cols = [col for col in column_set 
                      if any(keyword.lower() in str(col).lower() for keyword in market_keywords)]
        
        if len(financial_cols) > 5:
            return 'financial'
        elif len(market_cols) >= 4:
            return 'market'
        else:
            return 'metadata'
            
    def split_by_time_period(self, df, date_col='date', period='year'):
        """ææ¶é´å¨æåå²æ°æ?""
        df[date_col] = pd.to_datetime(df[date_col])
        
        if period == 'year':
            df['period'] = df[date_col].dt.year
        elif period == 'quarter':
            df['period'] = df[date_col].dt.to_period('Q')
        elif period == 'month':
            df['period'] = df[date_col].dt.to_period('M')
            
        # è¿åæå¨æåç»çæ°æ®å­å
¸
        return {period: group.drop('period', axis=1) 
                for period, group in df.groupby('period')}
```

## 6. æ°æ®åºå­å¨æ¹æ¡?

### 6.1 存储架构设计

#### 6.1.1 混合存储策略
```
存储架构:
âââ SQLiteæ°æ®åº?(è½»éçº§ï¼ç¨äºå
æ°æ®åæ¥è¯¢)
â?  âââ metadata.db    # å
æ°æ®è¡¨
â?  âââ stock_info.db  # è¡ç¥¨åºæ¬ä¿¡æ¯
â?  âââ index_info.db  # ææ°ä¿¡æ¯
âââ Parquetæä»¶å­å¨ (é«æ§è½ï¼ç¨äºå¤§éè¡æ
æ°æ?
â?  âââ daily/        # æ¥çº¿æ°æ®
â?  âââ weekly/       # å¨çº¿æ°æ®
â?  âââ monthly/      # æçº¿æ°æ®
â?  âââ intraday/     # åéæ°æ®
└── HDF5文件存储 (可选，用于复杂财务数据)
    ├── financial/    # 财务数据
    └── factors/      # 因子数据
```

#### 6.1.2 è¡¨ç»æè®¾è®?

**1. å
æ°æ®è¡¨ (metadata)**
```sql
CREATE TABLE metadata (
    id INTEGER PRIMARY KEY,
    data_type TEXT NOT NULL,      -- 'market', 'financial', 'intraday'
    frequency TEXT,               -- 'daily', 'weekly', 'monthly', '5min'
    stock_code TEXT NOT NULL,
    start_date DATE,
    end_date DATE,
    file_path TEXT,               -- Parquet文件路径
    record_count INTEGER,
    data_size_mb REAL,
    last_updated TIMESTAMP,
    UNIQUE(data_type, frequency, stock_code)
);
```

**2. è¡ç¥¨åºæ¬ä¿¡æ¯è¡?(stock_info)**
```sql
CREATE TABLE stock_info (
    stock_code TEXT PRIMARY KEY,
    stock_name TEXT,
    exchange TEXT,               -- 'SZ', 'SH'
    industry TEXT,
    listing_date DATE,
    delisting_date DATE,
    is_st INTEGER,               -- 是否ST
    market_cap REAL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**3. æ¥çº¿æ°æ®è¡¨ç»æ?(ç¤ºä¾)**
```sql
CREATE TABLE daily_market_data (
    id INTEGER PRIMARY KEY,
    stock_code TEXT NOT NULL,
    trade_date DATE NOT NULL,
    open_price REAL,
    high_price REAL,
    low_price REAL,
    close_price REAL,
    volume BIGINT,
    amount REAL,
    turnover_rate REAL,
    pe_ttm REAL,
    pb REAL,
    adj_factor REAL,
    is_st INTEGER,
    FOREIGN KEY (stock_code) REFERENCES stock_info(stock_code),
    UNIQUE(stock_code, trade_date)
);
```

### 6.2 æ°æ®åå
¥å®ç°

```python
class DatabaseManager:
    def __init__(self, db_path='zephyr_alpha.db', parquet_dir='data/parquet'):
        self.db_path = Path(db_path)
        self.parquet_dir = Path(parquet_dir)
        self.parquet_dir.mkdir(parents=True, exist_ok=True)
        
    def save_market_data(self, df, frequency='daily', adj_type='raw'):
        """ä¿å­è¡æ
æ°æ®å°æ··åå­å?""
        if df.empty:
            return
            
        # 1. 保存到Parquet文件
        parquet_path = self._save_to_parquet(df, frequency, adj_type)
        
        # 2. æ´æ°å
æ°æ®è¡¨
        self._update_metadata(df, frequency, adj_type, parquet_path)
        
        # 3. å¯éï¼ä¿å­å°SQLiteï¼ç¨äºå°è§æ¨¡æ¥è¯¢ï¼?
        if frequency == 'daily':
            self._save_to_sqlite(df, 'daily_market_data')
            
    def _save_to_parquet(self, df, frequency, adj_type):
        """保存到Parquet文件"""
        # æè¡ç¥¨ä»£ç ååºå­å?
        partition_cols = ['stock_code'] if 'stock_code' in df.columns else ['code']
        
        # 构建文件路径
        file_path = self.parquet_dir / frequency / adj_type
        file_path.mkdir(parents=True, exist_ok=True)
        
        # 保存为Parquet
        df.to_parquet(
            file_path / f"{frequency}_{adj_type}.parquet",
            partition_cols=partition_cols,
            compression='snappy'
        )
        
        return str(file_path)
        
    def _update_metadata(self, df, frequency, adj_type, file_path):
        """æ´æ°å
æ°æ®è¡¨"""
        conn = sqlite3.connect(self.db_path)
        
        metadata = {
            'data_type': 'market',
            'frequency': frequency,
            'adj_type': adj_type,
            'start_date': df['date'].min(),
            'end_date': df['date'].max(),
            'record_count': len(df),
            'file_path': file_path,
            'last_updated': datetime.now()
        }
        
        # æå
¥ææ´æ°å
æ°æ®
        # ... å
·ä½å®ç°
        
        conn.close()
        
    def save_financial_data(self, df):
        """保存财务数据"""
        # 财务数据更适合保存为Parquet + 单独的表
        file_path = self.parquet_dir / 'financial' / 'quarterly'
        file_path.mkdir(parents=True, exist_ok=True)
        
        # ææ¥åæåè¡ç¥¨ä»£ç åå?
        df.to_parquet(
            file_path / "financial_data.parquet",
            partition_cols=['report_date', 'stock_code'],
            compression='snappy'
        )
```

### 6.3 数据查询接口

```python
class DataQuery:
    def __init__(self, db_manager):
        self.db = db_manager
        
    def get_stock_data(self, stock_codes, start_date, end_date, frequency='daily'):
        """获取股票数据"""
        # 1. ä»å
æ°æ®è¡¨æ¥æ¾æä»¶ä½ç½?
        parquet_files = self._locate_parquet_files(stock_codes, frequency)
        
        # 2. 从Parquet文件读取数据
        data_frames = []
        for file_path in parquet_files:
            df = pd.read_parquet(file_path)
            # 筛选时间和股票代码
            mask = (df['date'] >= start_date) & (df['date'] <= end_date)
            if stock_codes:
                mask = mask & df['code'].isin(stock_codes)
            filtered_df = df.loc[mask]
            data_frames.append(filtered_df)
            
        return pd.concat(data_frames, ignore_index=True) if data_frames else pd.DataFrame()
        
    def get_financial_data(self, stock_codes, report_date=None):
        """获取财务数据"""
        # 类似逻辑，从Parquet文件读取
        pass
        
    def get_stock_info(self, stock_codes=None):
        """获取股票基本信息"""
        conn = sqlite3.connect(self.db.db_path)
        query = "SELECT * FROM stock_info"
        if stock_codes:
            placeholders = ','.join('?' * len(stock_codes))
            query += f" WHERE stock_code IN ({placeholders})"
            df = pd.read_sql_query(query, conn, params=stock_codes)
        else:
            df = pd.read_sql_query(query, conn)
        conn.close()
        return df
```

## 7. å®æ´å¤çæµæ°´çº¿å®ç?

### 7.1 ä¸»å¤çæµç¨?

```python
class AShareDataPipeline:
    def __init__(self, source_dir, output_dir):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        
        # 初始化各组件
        self.extractor = ZipExtractor(
            self.source_dir / "A股数据_zip",
            self.output_dir / "extracted"
        )
        self.csv_reader = CSVReader(self.source_dir / "CSVè¡æ
数据")
        self.financial_reader = FinancialDataReader(
            self.source_dir / "ä¸å¸å
¬å¸è´¢å¡ä¿¡æ¯" / "åå²è¯¦ç»æ°æ®"
        )
        self.cleaner = DataCleaner()
        self.classifier = DataClassifier()
        self.db_manager = DatabaseManager(
            db_path=self.output_dir / "database" / "zephyr_alpha.db",
            parquet_dir=self.output_dir / "parquet_data"
        )
        
    def run_full_pipeline(self):
        """è¿è¡å®æ´å¤çæµæ°´çº?""
        print("=" * 60)
        print("A股数据处理流水线启动")
        print("=" * 60)
        
        # 步骤1: 提取解压
        print("\n[1/5] æååè§£åæ°æ?..")
        self.extractor.extract_all(force=False)
        
        # 步骤2: 读取原始数据
        print("\n[2/5] 读取原始数据...")
        market_data = self.csv_reader.read_all_files(pattern="*.csv")
        financial_data = self.financial_reader.read_quarterly_data()
        
        # æ­¥éª¤3: æ°æ®æ¸
洗
        print("\n[3/5] æ°æ®æ¸
洗和标准化...")
        cleaned_market = self.cleaner.clean_market_data(market_data)
        cleaned_financial = self.cleaner.clean_financial_data(financial_data)
        
        # 步骤4: 数据分类
        print("\n[4/5] æ°æ®åç±»åç»´åº¦åå?..")
        market_classified = self.classifier.classify_by_frequency(cleaned_market)
        financial_classified = self.classifier.classify_by_content(cleaned_financial)
        
        # 步骤5: 存储到数据库
        print("\n[5/5] 存储到数据库...")
        self.db_manager.save_market_data(cleaned_market, frequency='daily')
        self.db_manager.save_financial_data(cleaned_financial)
        
        # 生成处理报告
        self._generate_report(cleaned_market, cleaned_financial)
        
        print("\n" + "=" * 60)
        print("å¤çå®æï¼?)
        print("=" * 60)
        
    def _generate_report(self, market_data, financial_data):
        """生成处理报告"""
        report = {
            'market_data': {
                'records': len(market_data),
                'stocks': market_data['code'].nunique() if 'code' in market_data.columns else 0,
                'date_range': {
                    'start': market_data['date'].min(),
                    'end': market_data['date'].max()
                } if 'date' in market_data.columns else None
            },
            'financial_data': {
                'records': len(financial_data),
                'companies': financial_data['stock_code'].nunique() if 'stock_code' in financial_data.columns else 0,
                'quarters': financial_data['report_date'].nunique() if 'report_date' in financial_data.columns else 0
            },
            'storage_info': {
                'database_size_mb': self._get_file_size(self.db_manager.db_path),
                'parquet_dir_size_mb': self._get_dir_size(self.db_manager.parquet_dir)
            }
        }
        
        # 保存报告为JSON
        report_path = self.output_dir / "processing_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
            
        print(f"å¤çæ¥åå·²ä¿å­? {report_path}")
```

### 7.2 增量更新机制

```python
class IncrementalUpdater:
    def __init__(self, pipeline):
        self.pipeline = pipeline
        self.last_update_file = pipeline.output_dir / "last_update.json"
        
    def check_for_updates(self):
        """æ£æ¥æ¯å¦ææ°æ°æ®éè¦æ´æ?""
        # æ£æ¥ZIPæä»¶æ¯å¦ææ´æ?
        zip_files = list(self.pipeline.source_dir.glob("*.zip"))
        last_update_time = self._load_last_update_time()
        
        new_files = []
        for zip_file in zip_files:
            if zip_file.stat().st_mtime > last_update_time:
                new_files.append(zip_file)
                
        return new_files
        
    def incremental_update(self):
        """增量更新数据"""
        new_files = self.check_for_updates()
        
        if not new_files:
            print("没有发现新数据，无需更新")
            return
            
        print(f"åç° {len(new_files)} ä¸ªæ°æä»¶éè¦å¤ç?)
        
        # 只处理新文件
        for zip_file in new_files:
            print(f"å¤çæ°æä»? {zip_file.name}")
            # è§£åæ°æä»?
            # è¯»åæ°æ°æ?
            # æ¸
洗和标准化
            # å¢éæ´æ°æ°æ®åº?
            
        # æ´æ°æåå¤çæ¶é?
        self._save_last_update_time()
        
    def _load_last_update_time(self):
        """å è½½æåæ´æ°æ¶é?""
        if self.last_update_file.exists():
            with open(self.last_update_file, 'r') as f:
                data = json.load(f)
                return data.get('last_update_time', 0)
        return 0
        
    def _save_last_update_time(self):
        """ä¿å­æåæ´æ°æ¶é?""
        data = {
            'last_update_time': time.time(),
            'update_date': datetime.now().isoformat()
        }
        with open(self.last_update_file, 'w') as f:
            json.dump(data, f)
```

## 8. é¨ç½²ä¸è¿è¡æå?

### 8.1 环境要求
```yaml
python_version: ">=3.8"
dependencies:
  - pandas>=1.3.0
  - numpy>=1.21.0
  - sqlite3 (å
ç½®)
  - pyarrow>=6.0.0  # Parquet支持
  - openpyxl>=3.0.0  # Excel支持
  - tqdm>=4.62.0    # è¿åº¦æ?
```

### 8.2 é
ç½®æä»¶ç¤ºä¾
```yaml
# config.yaml
data_pipeline:
  source_dir: "D:/ZephyrAlpha/Aè¡æ°æ?éåäº¤ææ°æ®"
  output_dir: "D:/ZephyrAlpha/processed_data"
  
  processing:
    max_workers: 4           # å¹¶è¡å¤çæ?
    chunk_size: 100000       # 分块大小
    memory_limit_gb: 8       # å
存限制
    
  cleaning:
    price_range: [0, 10000]  # 价格合理范围
    volume_threshold: 1e9    # æäº¤éå¼å¸¸éå?
    pct_chg_limit: 0.2       # æ¶¨è·å¹
éå?
    
  storage:
    db_path: "zephyr_alpha.db"
    parquet_compression: "snappy"
    hdf5_compression: "gzip"
    
  logging:
    level: "INFO"
    file: "data_pipeline.log"
    max_size_mb: 100
```

### 8.3 运行脚本
```python
# run_pipeline.py
import yaml
from pathlib import Path
from a_share_pipeline import AShareDataPipeline

def main():
    # å è½½é
ç½®
    config_path = Path("config.yaml")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 初始化流水线
    pipeline = AShareDataPipeline(
        source_dir=config['data_pipeline']['source_dir'],
        output_dir=config['data_pipeline']['output_dir']
    )
    
    # è¿è¡å®æ´æµæ°´çº?
    pipeline.run_full_pipeline()
    
    # æè¿è¡å¢éæ´æ?
    # updater = IncrementalUpdater(pipeline)
    # updater.incremental_update()

if __name__ == "__main__":
    main()
```

### 8.4 çæ§ä¸ç»´æ?
```python
# monitor.py
class PipelineMonitor:
    def __init__(self, pipeline):
        self.pipeline = pipeline
        
    def check_data_quality(self):
        """æ£æ¥æ°æ®è´¨é?""
        quality_report = {
            'completeness': self._check_completeness(),
            'consistency': self._check_consistency(),
            'accuracy': self._check_accuracy(),
            'timeliness': self._check_timeliness()
        }
        return quality_report
        
    def get_storage_usage(self):
        """è·åå­å¨ä½¿ç¨æ
况"""
        # 检查数据库大小
        # 检查Parquet文件大小
        # æ£æ¥ç£çç©ºé?
        pass
        
    def cleanup_old_data(self, days_to_keep=365):
        """æ¸
çæ§æ°æ?""
        # å é¤è¶
è¿æå®å¤©æ°çä¸´æ¶æä»?
        # 归档历史数据
        pass
```

## 9. 性能优化建议

### 9.1 å
存优化
1. **ååå¤ç**: å¤§æä»¶ååè¯»åï¼é¿å
å
存溢出
2. **æ°æ®ç±»åä¼å**: ä½¿ç¨åéçæ°å¼ç±»åï¼float32 vs float64ï¼?
3. **åæ¶éæ¾å
存**: 处理完成后及时删除不需要的数据

### 9.2 存储优化
1. **列式存储**: Parquet格式天然适合列式查询
2. **分区存储**: 按时间、股票代码分区，提高查询效率
3. **压缩选择**: Snappy压缩速度快，Gzip压缩率高

### 9.3 处理速度优化
1. **å¹¶è¡å¤ç**: å¤è¿ç¨å¤çä¸åè¡ç¥¨ææ¶é´æ®?
2. **åéåæä½?*: ä½¿ç¨pandasåéåå½æ°ï¼é¿å
å¾ªç¯
3. **ç¼å­æºå¶**: ç¼å­é¢ç¹è®¿é®çå
æ°æ®ååºç¡ä¿¡æ¯

## 10. æ
éæ¢å¤ä¸å¤ä»?

### 10.1 检查点机制
```python
class CheckpointManager:
    def __init__(self, checkpoint_dir):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
    def save_checkpoint(self, stage, data):
        """保存检查点"""
        checkpoint_file = self.checkpoint_dir / f"{stage}.checkpoint"
        # 保存处理状态和数据
        pass
        
    def load_checkpoint(self, stage):
        """加载检查点"""
        checkpoint_file = self.checkpoint_dir / f"{stage}.checkpoint"
        if checkpoint_file.exists():
            # 从检查点恢复
            pass
        return None
        
    def resume_from_checkpoint(self, pipeline):
        """从检查点恢复处理"""
        last_stage = self._find_last_checkpoint()
        if last_stage:
            print(f"从检查点恢复: {last_stage}")
            # 恢复处理流程
            pass
```

### 10.2 备份策略
1. **每日增量备份**: 备份当日新增数据
2. **æ¯å¨å
¨éå¤ä»½**: å¤ä»½æ´ä¸ªæ°æ®åº?
3. **å¼å°å¤ä»½**: éè¦æ°æ®å¤ä»½å°ä¸åç£çæäºå­å?

---

## 总结

这个蓝图提供了一个完整的A股历史数据处理方案，从原始数据提取到数据库存储的完整流程。方案特点：

1. **å
¨é¢æ?*: è¦çè¡æ
数据、财务数据、分钟数据等多种数据类型
2. **å®ç¨æ?*: æä¾å³ç¨çä»£ç ç¤ºä¾åé
ç½®æ¨¡æ¿
3. **å¯æ©å±æ?*: æ¨¡ååè®¾è®¡ï¼æäºæ©å±æ°çæ°æ®ç±»å
4. **é«ææ?*: éç¨æ··åå­å¨ç­ç¥ï¼å¹³è¡¡æ¥è¯¢æçåå­å¨ææ¬
5. **å¥å£®æ?*: å
å«éè¯¯å¤çãæ£æ¥ç¹ãå¤ä»½æ¢å¤æºå?

æ¨å¯ä»¥æ ¹æ®è¿ä¸ªèå¾éæ­¥å®ç°æ°æ®å¤çç³»ç»ï¼ä¹å¯ä»¥æ ¹æ®å®é
éæ±è°æ´åä¸ªæ¨¡åãå»ºè®®å
ä»æ ¸å¿çæ¥çº¿æ°æ®å¤çå¼å§ï¼éæ­¥æ©å±å°å
¶ä»æ°æ®ç±»åã
---

## 11. 文档治理

### 11.1 System_Manifest.md索引

```markdown
#### Layer 0: 系统架构
##### 0.BLUEPRI. Doc Temp A Stock
- **模块ID**: DOC_TEMP_A_STOCK_BLUEPRI
- **蓝图文档**: [A_STOCK_DATA_PROCESSING_BLUEPRINT.md](06_CONSTRUCTION_DOCS\01_BLUEPRINTS\A_STOCK_DATA_PROCESSING_BLUEPRINT.md)
- **技术规格书**: 待创建
- **职责**: å
¨ç³»ç»?
- **状态**: Active
```

### 11.2 模块职责边界

| 模块 | 职责 | 边界 |
|------|------|------|
| **Doc Temp A Stock** | å
¨ç³»ç»? | **核心模块** |

### 11.3 版本管理

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-01 | 初始版本创建 | 首席蓝图架构师 |

---

**蓝图版本**: v1.0.0 | **创建日期**: 2026-04-01 | **状态**: Active
