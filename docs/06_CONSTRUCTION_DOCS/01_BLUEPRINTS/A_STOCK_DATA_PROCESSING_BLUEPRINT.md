---
standard_type: 蓝图标准
applicable_scope: 全系�?
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 设计阶段
owner: 文档维护�?
version: 1.0.0
module_id: DOC_TEMP_A_STOCK_BLUEPRI
created_date: 2026-04-01
last_updated: 2026-04-02
---
# A股历史数据处理与数据库集成蓝�?

## 1. 数据现状分析

### 1.1 目录结构概览
```
D:\ZephyrAlpha\A股数据\量化交易数据\
├── A股_分时数据/           # 分钟级行情数�?(5分钟�?5分钟�?0分钟�?0分钟)
├── A股数�?               # 原始数据（可能为备份或未分类数据�?
├── A股数据_zip/           # 压缩的行情数据文�?
�?  ├── daily.zip         # 日线数据（未复权�?
�?  ├── daily_qfq.zip     # 日线数据（前复权�?
�?  ├── daily_hfq.zip     # 日线数据（后复权�?
�?  ├── weekly.zip        # 周线数据
�?  ├── monthly.zip       # 月线数据
�?  └── ...其他频率数据
├── CSV行情数据/           # 已解压的CSV格式行情数据
�?  ├── 000002.csv        # 单只股票日线数据
�?  ├── 000858_5min.csv   # 单只股票5分钟数据
�?  └── ...其他股票文件
├── 上市公司财务信息/       # 财务数据
�?  ├── 历史详细数据/
�?  �?  ├── 全部上市公司财务信息_20250930.xlsx
�?  �?  ├── 全部上市公司财务信息_20250630.xlsx
�?  �?  └── ...历史季度数据
�?  └── 最新数�?
└── 复权因子/              # 复权计算相关脚本和数�?
```

### 1.2 数据格式与特�?

#### 1.2.1 行情数据格式
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
- 文件: `全部上市公司财务信息_20250930.xlsx`
- 数据�? 250+ 财务指标字段
- 包含: 资产负债表、利润表、现金流量表、财务比率、估值指标等
- 时间跨度: 历史季度数据（按季度文件存储�?

#### 1.2.3 压缩数据格式
**ZIP文件结构**:
- `daily.zip`: 日线未复权数�?
- `daily_qfq.zip`: 日线前复权数�? 
- `daily_hfq.zip`: 日线后复权数�?
- `weekly.zip`: 周线数据
- `monthly.zip`: 月线数据

## 2. 总体处理架构设计

### 2.1 四层处理流水�?
```
原始数据�?�?提取解压�?�?清洗标准化层 �?分类存储�?�?数据库层
    �?            �?             �?             �?           �?
   CSV/ZIP    数据解压      数据清洗        数据分类      SQLite/Parquet
   Excel      格式转换      异常处理        维度划分      数据仓库
```

### 2.2 技术栈选择
| 组件 | 技术选择 | 理由 |
|------|----------|------|
| **数据提取** | Python `zipfile`, `pandas` | 原生支持，内存效率高 |
| **数据清洗** | `pandas`, `numpy` | 强大的数据操作能�?|
| **数据存储** | **SQLite** (元数�? + **Parquet** (行情数据) | 查询效率+存储压缩 |
| **任务调度** | Python `multiprocessing` | 简单易用，适合个人开�?|
| **监控日志** | Python `logging` + 进度�?| 实时反馈，易于调�?|

## 3. 数据提取与解压方�?

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
                print(f"跳过已解�? {zip_file.name}")
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
            # 添加文件名作为数据来源标�?
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
        """读取所有季度财务数�?""
        quarter_files = sorted(self.excel_dir.glob("全部上市公司财务信息_*.xlsx"))
        all_data = []
        
        for file_path in quarter_files:
            # 从文件名提取季度信息
            quarter_str = file_path.stem.split('_')[-1]  # �?20250930
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
�?  ├── daily/                   # 日线数据
�?  ├── daily_qfq/              # 前复权日�?
�?  ├── daily_hfq/              # 后复权日�?
�?  ├── weekly/                 # 周线数据
�?  └── monthly/                # 月线数据
├── raw_csv/                     # 原始CSV数据（保持原样）
├── raw_financial/               # 原始财务数据（保持原样）
└── metadata/                    # 元数据文�?
    ├── file_index.json         # 文件索引
    ├── data_schema.json        # 数据模式定义
    └── extraction_log.csv      # 提取日志
```

## 4. 数据清洗与标准化流程

### 4.1 清洗规则定义

#### 4.1.1 行情数据清洗规则
| 字段 | 清洗规则 | 异常处理 |
|------|----------|----------|
| **date** | 转换为datetime格式，验证日期有效�?| 无效日期标记为NaT，可插�?|
| **code** | 标准化为`交易所.代码`格式 (如`SZ.000002`) | 无效代码删除整行 |
| **price** | 价格>0，开盘≤最高≥最低≤收盘 | 价格异常标记并插�?|
| **volume** | 成交量≥0 | 负值设�? |
| **amount** | 成交额≥0，与价格*volume一�?| 不一致时重新计算 |
| **pct_chg** | 涨跌幅在[-10%, 10%]合理范围 | 超出范围使用前值填�?|

#### 4.1.2 财务数据清洗规则
| 字段类型 | 清洗规则 | 说明 |
|----------|----------|------|
| **代码字段** | 统一�?位数字代码，补前�? | 便于关联行情数据 |
| **数值字�?* | 替换"NaN"�?-"、空值为np.nan | 保持数据一致�?|
| **文本字段** | 去除首尾空格，统一编码为UTF-8 | 避免编码问题 |
| **日期字段** | 转换为datetime格式 | 统一时间处理 |

### 4.2 标准化处理类

```python
class DataCleaner:
    def __init__(self):
        self.rules = self._load_cleaning_rules()
        
    def clean_market_data(self, df):
        """清洗行情数据"""
        # 1. 代码标准�?
        df['code'] = df['code'].apply(self._standardize_code)
        
        # 2. 日期标准�?
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # 3. 价格数据验证
        price_cols = ['open', 'high', 'low', 'close']
        for col in price_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            # 价格必须为正�?
            df.loc[df[col] <= 0, col] = np.nan
            
        # 4. 逻辑关系验证
        df = self._validate_price_logic(df)
        
        # 5. 缺失值处�?
        df = self._handle_missing_values(df)
        
        return df
        
    def clean_financial_data(self, df):
        """清洗财务数据"""
        # 1. 代码标准�?
        if '股票代码' in df.columns:
            df['stock_code'] = df['股票代码'].astype(str).str.zfill(6)
            
        # 2. 数值字段处�?
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        # 3. 文本字段处理
        text_cols = df.select_dtypes(include=[object]).columns
        for col in text_cols:
            df[col] = df[col].astype(str).str.strip()
            
        # 4. 去除全为NaN的行
        df = df.dropna(how='all')
        
        return df
        
    def _standardize_code(self, code):
        """标准化股票代�?""
        if pd.isna(code):
            return None
            
        code_str = str(code)
        # 移除空格和特殊字�?
        code_str = re.sub(r'[^a-zA-Z0-9]', '', code_str)
        
        # 标准化格�? SZ.000002 �?SH.600000
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
        """检测价格异�?""
        anomalies = []
        
        # 1. 价格跳动检�?(日内涨跌幅过�?
        df['pct_change'] = df['close'].pct_change()
        large_jumps = df[abs(df['pct_change']) > 0.2]  # 20%以上跳动
        
        # 2. 成交量异常检�?
        volume_mean = df['volume'].rolling(20).mean()
        volume_std = df['volume'].rolling(20).std()
        volume_anomalies = df[df['volume'] > (volume_mean + 3 * volume_std)]
        
        # 3. 价格关系异常 (开�?最�? 最�?收盘�?
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
        """缺失值插�?""
        # 前向填充 (适用于交易日数据)
        df_filled = df.fillna(method='ffill')
        
        # 线性插�?(适用于连续时间序�?
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df_filled[numeric_cols] = df_filled[numeric_cols].interpolate(method='linear')
        
        # 向后填充剩余缺失�?
        df_filled = df_filled.fillna(method='bfill')
        
        return df_filled
```

## 5. 数据分类与维度划�?

### 5.1 分类体系设计

#### 5.1.1 按数据类型分�?
```
数据分类体系:
├── 行情数据
�?  ├── 日线数据 (daily)
�?  �?  ├── 未复�?(raw)
�?  �?  ├── 前复�?(qfq)
�?  �?  └── 后复�?(hfq)
�?  ├── 周线数据 (weekly)
�?  ├── 月线数据 (monthly)
�?  └── 分钟数据 (intraday)
�?      ├── 5分钟 (5min)
�?      ├── 15分钟 (15min)
�?      ├── 30分钟 (30min)
�?      └── 60分钟 (60min)
├── 财务数据
�?  ├── 资产负债表 (balance_sheet)
�?  ├── 利润�?(income_statement)
�?  ├── 现金流量�?(cash_flow)
�?  └── 财务比率 (financial_ratios)
├── 基础信息数据
�?  ├── 股票列表 (stock_list)
�?  ├── 行业分类 (industry)
�?  └── 指数成分 (index_constituents)
└── 衍生数据
    ├── 技术指�?(technical_indicators)
    ├── 因子数据 (factors)
    └── 回测结果 (backtest_results)
```

#### 5.1.2 按时间维度分�?
- **历史全量数据**: 所有历史数据，用于模型训练
- **滚动窗口数据**: 最近N年数据，用于实时分析
- **季度切片数据**: 按财务季度划分，用于季报分析
- **年度汇总数�?*: 按年度汇总，用于年度对比

### 5.2 分类处理实现

```python
class DataClassifier:
    def __init__(self):
        self.classification_rules = self._load_classification_rules()
        
    def classify_by_frequency(self, df, date_col='date'):
        """按频率分类数�?""
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
            elif mode_interval.total_seconds() <= 3600:  # 1小时以内
                return 'intraday'
                
        return 'unknown'
        
    def classify_by_content(self, df):
        """按内容分类数�?""
        column_set = set(df.columns)
        
        # 财务数据特征�?
        financial_keywords = ['资产', '负�?, '利润', '收入', '现金�?, '比率']
        financial_cols = [col for col in column_set 
                         if any(keyword in str(col) for keyword in financial_keywords)]
        
        # 行情数据特征�?
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
        """按时间周期分割数�?""
        df[date_col] = pd.to_datetime(df[date_col])
        
        if period == 'year':
            df['period'] = df[date_col].dt.year
        elif period == 'quarter':
            df['period'] = df[date_col].dt.to_period('Q')
        elif period == 'month':
            df['period'] = df[date_col].dt.to_period('M')
            
        # 返回按周期分组的数据字典
        return {period: group.drop('period', axis=1) 
                for period, group in df.groupby('period')}
```

## 6. 数据库存储方�?

### 6.1 存储架构设计

#### 6.1.1 混合存储策略
```
存储架构:
├── SQLite数据�?(轻量级，用于元数据和查询)
�?  ├── metadata.db    # 元数据表
�?  ├── stock_info.db  # 股票基本信息
�?  └── index_info.db  # 指数信息
├── Parquet文件存储 (高性能，用于大量行情数�?
�?  ├── daily/        # 日线数据
�?  ├── weekly/       # 周线数据
�?  ├── monthly/      # 月线数据
�?  └── intraday/     # 分钟数据
└── HDF5文件存储 (可选，用于复杂财务数据)
    ├── financial/    # 财务数据
    └── factors/      # 因子数据
```

#### 6.1.2 表结构设�?

**1. 元数据表 (metadata)**
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

**2. 股票基本信息�?(stock_info)**
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

**3. 日线数据表结�?(示例)**
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

### 6.2 数据写入实现

```python
class DatabaseManager:
    def __init__(self, db_path='zephyr_alpha.db', parquet_dir='data/parquet'):
        self.db_path = Path(db_path)
        self.parquet_dir = Path(parquet_dir)
        self.parquet_dir.mkdir(parents=True, exist_ok=True)
        
    def save_market_data(self, df, frequency='daily', adj_type='raw'):
        """保存行情数据到混合存�?""
        if df.empty:
            return
            
        # 1. 保存到Parquet文件
        parquet_path = self._save_to_parquet(df, frequency, adj_type)
        
        # 2. 更新元数据表
        self._update_metadata(df, frequency, adj_type, parquet_path)
        
        # 3. 可选：保存到SQLite（用于小规模查询�?
        if frequency == 'daily':
            self._save_to_sqlite(df, 'daily_market_data')
            
    def _save_to_parquet(self, df, frequency, adj_type):
        """保存到Parquet文件"""
        # 按股票代码分区存�?
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
        """更新元数据表"""
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
        
        # 插入或更新元数据
        # ... 具体实现
        
        conn.close()
        
    def save_financial_data(self, df):
        """保存财务数据"""
        # 财务数据更适合保存为Parquet + 单独的表
        file_path = self.parquet_dir / 'financial' / 'quarterly'
        file_path.mkdir(parents=True, exist_ok=True)
        
        # 按报告期和股票代码分�?
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
        # 1. 从元数据表查找文件位�?
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

## 7. 完整处理流水线实�?

### 7.1 主处理流�?

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
        self.csv_reader = CSVReader(self.source_dir / "CSV行情数据")
        self.financial_reader = FinancialDataReader(
            self.source_dir / "上市公司财务信息" / "历史详细数据"
        )
        self.cleaner = DataCleaner()
        self.classifier = DataClassifier()
        self.db_manager = DatabaseManager(
            db_path=self.output_dir / "database" / "zephyr_alpha.db",
            parquet_dir=self.output_dir / "parquet_data"
        )
        
    def run_full_pipeline(self):
        """运行完整处理流水�?""
        print("=" * 60)
        print("A股数据处理流水线启动")
        print("=" * 60)
        
        # 步骤1: 提取解压
        print("\n[1/5] 提取和解压数�?..")
        self.extractor.extract_all(force=False)
        
        # 步骤2: 读取原始数据
        print("\n[2/5] 读取原始数据...")
        market_data = self.csv_reader.read_all_files(pattern="*.csv")
        financial_data = self.financial_reader.read_quarterly_data()
        
        # 步骤3: 数据清洗
        print("\n[3/5] 数据清洗和标准化...")
        cleaned_market = self.cleaner.clean_market_data(market_data)
        cleaned_financial = self.cleaner.clean_financial_data(financial_data)
        
        # 步骤4: 数据分类
        print("\n[4/5] 数据分类和维度划�?..")
        market_classified = self.classifier.classify_by_frequency(cleaned_market)
        financial_classified = self.classifier.classify_by_content(cleaned_financial)
        
        # 步骤5: 存储到数据库
        print("\n[5/5] 存储到数据库...")
        self.db_manager.save_market_data(cleaned_market, frequency='daily')
        self.db_manager.save_financial_data(cleaned_financial)
        
        # 生成处理报告
        self._generate_report(cleaned_market, cleaned_financial)
        
        print("\n" + "=" * 60)
        print("处理完成�?)
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
            
        print(f"处理报告已保�? {report_path}")
```

### 7.2 增量更新机制

```python
class IncrementalUpdater:
    def __init__(self, pipeline):
        self.pipeline = pipeline
        self.last_update_file = pipeline.output_dir / "last_update.json"
        
    def check_for_updates(self):
        """检查是否有新数据需要更�?""
        # 检查ZIP文件是否有更�?
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
            
        print(f"发现 {len(new_files)} 个新文件需要处�?)
        
        # 只处理新文件
        for zip_file in new_files:
            print(f"处理新文�? {zip_file.name}")
            # 解压新文�?
            # 读取新数�?
            # 清洗和标准化
            # 增量更新数据�?
            
        # 更新最后处理时�?
        self._save_last_update_time()
        
    def _load_last_update_time(self):
        """加载最后更新时�?""
        if self.last_update_file.exists():
            with open(self.last_update_file, 'r') as f:
                data = json.load(f)
                return data.get('last_update_time', 0)
        return 0
        
    def _save_last_update_time(self):
        """保存最后更新时�?""
        data = {
            'last_update_time': time.time(),
            'update_date': datetime.now().isoformat()
        }
        with open(self.last_update_file, 'w') as f:
            json.dump(data, f)
```

## 8. 部署与运行指�?

### 8.1 环境要求
```yaml
python_version: ">=3.8"
dependencies:
  - pandas>=1.3.0
  - numpy>=1.21.0
  - sqlite3 (内置)
  - pyarrow>=6.0.0  # Parquet支持
  - openpyxl>=3.0.0  # Excel支持
  - tqdm>=4.62.0    # 进度�?
```

### 8.2 配置文件示例
```yaml
# config.yaml
data_pipeline:
  source_dir: "D:/ZephyrAlpha/A股数�?量化交易数据"
  output_dir: "D:/ZephyrAlpha/processed_data"
  
  processing:
    max_workers: 4           # 并行处理�?
    chunk_size: 100000       # 分块大小
    memory_limit_gb: 8       # 内存限制
    
  cleaning:
    price_range: [0, 10000]  # 价格合理范围
    volume_threshold: 1e9    # 成交量异常阈�?
    pct_chg_limit: 0.2       # 涨跌幅限�?
    
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
    # 加载配置
    config_path = Path("config.yaml")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 初始化流水线
    pipeline = AShareDataPipeline(
        source_dir=config['data_pipeline']['source_dir'],
        output_dir=config['data_pipeline']['output_dir']
    )
    
    # 运行完整流水�?
    pipeline.run_full_pipeline()
    
    # 或运行增量更�?
    # updater = IncrementalUpdater(pipeline)
    # updater.incremental_update()

if __name__ == "__main__":
    main()
```

### 8.4 监控与维�?
```python
# monitor.py
class PipelineMonitor:
    def __init__(self, pipeline):
        self.pipeline = pipeline
        
    def check_data_quality(self):
        """检查数据质�?""
        quality_report = {
            'completeness': self._check_completeness(),
            'consistency': self._check_consistency(),
            'accuracy': self._check_accuracy(),
            'timeliness': self._check_timeliness()
        }
        return quality_report
        
    def get_storage_usage(self):
        """获取存储使用情况"""
        # 检查数据库大小
        # 检查Parquet文件大小
        # 检查磁盘空�?
        pass
        
    def cleanup_old_data(self, days_to_keep=365):
        """清理旧数�?""
        # 删除超过指定天数的临时文�?
        # 归档历史数据
        pass
```

## 9. 性能优化建议

### 9.1 内存优化
1. **分块处理**: 大文件分块读取，避免内存溢出
2. **数据类型优化**: 使用合适的数值类型（float32 vs float64�?
3. **及时释放内存**: 处理完成后及时删除不需要的数据

### 9.2 存储优化
1. **列式存储**: Parquet格式天然适合列式查询
2. **分区存储**: 按时间、股票代码分区，提高查询效率
3. **压缩选择**: Snappy压缩速度快，Gzip压缩率高

### 9.3 处理速度优化
1. **并行处理**: 多进程处理不同股票或时间�?
2. **向量化操�?*: 使用pandas向量化函数，避免循环
3. **缓存机制**: 缓存频繁访问的元数据和基础信息

## 10. 故障恢复与备�?

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
2. **每周全量备份**: 备份整个数据�?
3. **异地备份**: 重要数据备份到不同磁盘或云存�?

---

## 总结

这个蓝图提供了一个完整的A股历史数据处理方案，从原始数据提取到数据库存储的完整流程。方案特点：

1. **全面�?*: 覆盖行情数据、财务数据、分钟数据等多种数据类型
2. **实用�?*: 提供即用的代码示例和配置模板
3. **可扩展�?*: 模块化设计，易于扩展新的数据类型
4. **高效�?*: 采用混合存储策略，平衡查询效率和存储成本
5. **健壮�?*: 包含错误处理、检查点、备份恢复机�?

您可以根据这个蓝图逐步实现数据处理系统，也可以根据实际需求调整各个模块。建议先从核心的日线数据处理开始，逐步扩展到其他数据类型�