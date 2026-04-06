---
module_id: A_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 文档管理员
layer: Layer 2 (Alpha因子层)
standard_type: 专业量化机构蓝图
applicable_scope: 全系统
compliance_level: 专业标准
---

﻿---
standard_type: èå¾æ å
applicable_scope: å¨ç³»ç»?
compliance_level: åå§æ å
parent_document: ../INDEX.md
implementation_status: è®¾è®¡é¶æ®µ
owner: ææ¡£ç»´æ¤è?
version: 1.0.0
module_id: DOC_TEMP_A_STOCK_BLUEPRI
created_date: 2026-04-01
last_updated: 2026-04-02
---
# Aè¡åå²æ°æ®å¤çä¸æ°æ®åºéæèå?

## 1. æ°æ®ç°ç¶åæ

### 1.1 ç®å½ç»ææ¦è§
```
D:\ZephyrAlpha\Aè¡æ°æ®\éåäº¤ææ°æ®\
âââ Aè¡_åæ¶æ°æ®/           # åéçº§è¡ææ°æ?(5åéã?5åéã?0åéã?0åé)
âââ Aè¡æ°æ?               # åå§æ°æ®ï¼å¯è½ä¸ºå¤ä»½ææªåç±»æ°æ®ï¼?
âââ Aè¡æ°æ®_zip/           # åç¼©çè¡ææ°æ®æä»?
â?  âââ daily.zip         # æ¥çº¿æ°æ®ï¼æªå¤æï¼?
â?  âââ daily_qfq.zip     # æ¥çº¿æ°æ®ï¼åå¤æï¼?
â?  âââ daily_hfq.zip     # æ¥çº¿æ°æ®ï¼åå¤æï¼?
â?  âââ weekly.zip        # å¨çº¿æ°æ®
â?  âââ monthly.zip       # æçº¿æ°æ®
â?  âââ ...å¶ä»é¢çæ°æ®
âââ CSVè¡ææ°æ®/           # å·²è§£åçCSVæ ¼å¼è¡ææ°æ®
â?  âââ 000002.csv        # ååªè¡ç¥¨æ¥çº¿æ°æ®
â?  âââ 000858_5min.csv   # ååªè¡ç¥¨5åéæ°æ®
â?  âââ ...å¶ä»è¡ç¥¨æä»¶
âââ ä¸å¸å¬å¸è´¢å¡ä¿¡æ¯/       # è´¢å¡æ°æ®
â?  âââ åå²è¯¦ç»æ°æ®/
â?  â?  âââ å¨é¨ä¸å¸å¬å¸è´¢å¡ä¿¡æ¯_20250930.xlsx
â?  â?  âââ å¨é¨ä¸å¸å¬å¸è´¢å¡ä¿¡æ¯_20250630.xlsx
â?  â?  âââ ...åå²å­£åº¦æ°æ®
â?  âââ ææ°æ°æ?
âââ å¤æå å­/              # å¤æè®¡ç®ç¸å³èæ¬åæ°æ?
```

### 1.2 æ°æ®æ ¼å¼ä¸ç¹å¾?

#### 1.2.1 è¡ææ°æ®æ ¼å¼
**æ¥çº¿æ°æ® (000002.csv)**:
```csv
date,code,open,high,low,close,pre_close,change,pct_chg,vol,amount,adj_factor,turnover_rate,pe_ttm,pb,ps,pcf,is_st
2025-10-15,sz000002,12.34,12.56,12.12,12.45,12.30,0.15,1.22,1234567,15432100,1.0,0.85,8.76,1.23,2.34,5.67,0
```

**5åéæ°æ® (000858_5min.csv)**:
```csv
date,open,high,low,close,volume,code
2025-10-14 10:15:00,120.49,120.65,120.41,120.65,455272,sz000858
```

#### 1.2.2 è´¢å¡æ°æ®æ ¼å¼
**Excelæ ¼å¼è´¢å¡æ°æ®**:
- æä»¶: `å¨é¨ä¸å¸å¬å¸è´¢å¡ä¿¡æ¯_20250930.xlsx`
- æ°æ®é? 250+ è´¢å¡ææ å­æ®µ
- åå«: èµäº§è´åºè¡¨ãå©æ¶¦è¡¨ãç°éæµéè¡¨ãè´¢å¡æ¯çãä¼°å¼ææ ç­
- æ¶é´è·¨åº¦: åå²å­£åº¦æ°æ®ï¼æå­£åº¦æä»¶å­å¨ï¼?

#### 1.2.3 åç¼©æ°æ®æ ¼å¼
**ZIPæä»¶ç»æ**:
- `daily.zip`: æ¥çº¿æªå¤ææ°æ?
- `daily_qfq.zip`: æ¥çº¿åå¤ææ°æ? 
- `daily_hfq.zip`: æ¥çº¿åå¤ææ°æ?
- `weekly.zip`: å¨çº¿æ°æ®
- `monthly.zip`: æçº¿æ°æ®

## 2. æ»ä½å¤çæ¶æè®¾è®¡

### 2.1 åå±å¤çæµæ°´çº?
```
åå§æ°æ®å±?â?æåè§£åå±?â?æ¸æ´æ ååå± â?åç±»å­å¨å±?â?æ°æ®åºå±
    â?            â?             â?             â?           â?
   CSV/ZIP    æ°æ®è§£å      æ°æ®æ¸æ´        æ°æ®åç±»      SQLite/Parquet
   Excel      æ ¼å¼è½¬æ¢      å¼å¸¸å¤ç        ç»´åº¦åå      æ°æ®ä»åº
```

### 2.2 ææ¯æ éæ©
| ç»ä»¶ | ææ¯éæ© | çç± |
|------|----------|------|
| **æ°æ®æå** | Python `zipfile`, `pandas` | åçæ¯æï¼åå­æçé« |
| **æ°æ®æ¸æ´** | `pandas`, `numpy` | å¼ºå¤§çæ°æ®æä½è½å?|
| **æ°æ®å­å¨** | **SQLite** (åæ°æ? + **Parquet** (è¡ææ°æ®) | æ¥è¯¢æç+å­å¨åç¼© |
| **ä»»å¡è°åº¦** | Python `multiprocessing` | ç®åæç¨ï¼éåä¸ªäººå¼å?|
| **çæ§æ¥å¿** | Python `logging` + è¿åº¦æ?| å®æ¶åé¦ï¼æäºè°è¯?|

## 3. æ°æ®æåä¸è§£åæ¹æ¡?

### 3.1 æåç­ç¥

#### 3.1.1 ZIPæä»¶æ¹éè§£å
```python
import zipfile
import os
from pathlib import Path

class ZipExtractor:
    def __init__(self, zip_dir, output_dir):
        self.zip_dir = Path(zip_dir)
        self.output_dir = Path(output_dir)
        
    def extract_all(self, force=False):
        """æ¹éè§£åææZIPæä»¶"""
        zip_files = list(self.zip_dir.glob("*.zip"))
        
        for zip_file in zip_files:
            output_subdir = self.output_dir / zip_file.stem
            if output_subdir.exists() and not force:
                print(f"è·³è¿å·²è§£å? {zip_file.name}")
                continue
                
            print(f"è§£å: {zip_file.name}")
            with zipfile.ZipFile(zip_file, 'r') as zf:
                zf.extractall(output_subdir)
                
    def get_extracted_structure(self):
        """è·åè§£ååçæä»¶ç»æ"""
        structure = {}
        for item in self.output_dir.rglob("*"):
            if item.is_file():
                rel_path = item.relative_to(self.output_dir)
                structure.setdefault(rel_path.parent, []).append(rel_path.name)
        return structure
```

#### 3.1.2 CSVæä»¶æ¹éè¯»å
```python
import pandas as pd
from concurrent.futures import ProcessPoolExecutor

class CSVReader:
    def __init__(self, csv_dir):
        self.csv_dir = Path(csv_dir)
        
    def read_single_file(self, csv_path):
        """è¯»ååä¸ªCSVæä»¶"""
        try:
            df = pd.read_csv(csv_path)
            # æ·»å æä»¶åä½ä¸ºæ°æ®æ¥æºæ è®?
            df['source_file'] = csv_path.name
            return df
        except Exception as e:
            print(f"è¯»åå¤±è´¥ {csv_path}: {e}")
            return None
            
    def read_all_files(self, pattern="*.csv", max_workers=4):
        """å¹¶è¡è¯»åææCSVæä»¶"""
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

#### 3.1.3 Excelè´¢å¡æ°æ®è¯»å
```python
class FinancialDataReader:
    def __init__(self, excel_dir):
        self.excel_dir = Path(excel_dir)
        
    def read_quarterly_data(self):
        """è¯»åææå­£åº¦è´¢å¡æ°æ?""
        quarter_files = sorted(self.excel_dir.glob("å¨é¨ä¸å¸å¬å¸è´¢å¡ä¿¡æ¯_*.xlsx"))
        all_data = []
        
        for file_path in quarter_files:
            # ä»æä»¶åæåå­£åº¦ä¿¡æ¯
            quarter_str = file_path.stem.split('_')[-1]  # å¦?20250930
            quarter_date = pd.to_datetime(quarter_str, format='%Y%m%d')
            
            print(f"è¯»å: {file_path.name}")
            df = pd.read_excel(file_path, dtype={'è¡ç¥¨ä»£ç ': str})
            df['report_date'] = quarter_date
            df['data_type'] = 'financial'
            
            all_data.append(df)
            
        return pd.concat(all_data, ignore_index=True)
```

### 3.2 è§£åç®å½ç»æè§å
```
processed_data/
âââ extracted/                    # è§£ååçåå§æä»¶
â?  âââ daily/                   # æ¥çº¿æ°æ®
â?  âââ daily_qfq/              # åå¤ææ¥çº?
â?  âââ daily_hfq/              # åå¤ææ¥çº?
â?  âââ weekly/                 # å¨çº¿æ°æ®
â?  âââ monthly/                # æçº¿æ°æ®
âââ raw_csv/                     # åå§CSVæ°æ®ï¼ä¿æåæ ·ï¼
âââ raw_financial/               # åå§è´¢å¡æ°æ®ï¼ä¿æåæ ·ï¼
âââ metadata/                    # åæ°æ®æä»?
    âââ file_index.json         # æä»¶ç´¢å¼
    âââ data_schema.json        # æ°æ®æ¨¡å¼å®ä¹
    âââ extraction_log.csv      # æåæ¥å¿
```

## 4. æ°æ®æ¸æ´ä¸æ ååæµç¨

### 4.1 æ¸æ´è§åå®ä¹

#### 4.1.1 è¡ææ°æ®æ¸æ´è§å
| å­æ®µ | æ¸æ´è§å | å¼å¸¸å¤ç |
|------|----------|----------|
| **date** | è½¬æ¢ä¸ºdatetimeæ ¼å¼ï¼éªè¯æ¥ææææ?| æ ææ¥ææ è®°ä¸ºNaTï¼å¯æå?|
| **code** | æ ååä¸º`äº¤ææ.ä»£ç `æ ¼å¼ (å¦`SZ.000002`) | æ æä»£ç å é¤æ´è¡ |
| **price** | ä»·æ ¼>0ï¼å¼çâ¤æé«â¥æä½â¤æ¶ç | ä»·æ ¼å¼å¸¸æ è®°å¹¶æå?|
| **volume** | æäº¤éâ¥0 | è´å¼è®¾ä¸? |
| **amount** | æäº¤é¢â¥0ï¼ä¸ä»·æ ¼*volumeä¸è?| ä¸ä¸è´æ¶éæ°è®¡ç® |
| **pct_chg** | æ¶¨è·å¹å¨[-10%, 10%]åçèå´ | è¶åºèå´ä½¿ç¨åå¼å¡«å?|

#### 4.1.2 è´¢å¡æ°æ®æ¸æ´è§å
| å­æ®µç±»å | æ¸æ´è§å | è¯´æ |
|----------|----------|------|
| **ä»£ç å­æ®µ** | ç»ä¸ä¸?ä½æ°å­ä»£ç ï¼è¡¥åå¯? | ä¾¿äºå³èè¡ææ°æ® |
| **æ°å¼å­æ®?* | æ¿æ¢"NaN"ã?-"ãç©ºå¼ä¸ºnp.nan | ä¿ææ°æ®ä¸è´æ?|
| **ææ¬å­æ®µ** | å»é¤é¦å°¾ç©ºæ ¼ï¼ç»ä¸ç¼ç ä¸ºUTF-8 | é¿åç¼ç é®é¢ |
| **æ¥æå­æ®µ** | è½¬æ¢ä¸ºdatetimeæ ¼å¼ | ç»ä¸æ¶é´å¤ç |

### 4.2 æ ååå¤çç±»

```python
class DataCleaner:
    def __init__(self):
        self.rules = self._load_cleaning_rules()
        
    def clean_market_data(self, df):
        """æ¸æ´è¡ææ°æ®"""
        # 1. ä»£ç æ åå?
        df['code'] = df['code'].apply(self._standardize_code)
        
        # 2. æ¥ææ åå?
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # 3. ä»·æ ¼æ°æ®éªè¯
        price_cols = ['open', 'high', 'low', 'close']
        for col in price_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            # ä»·æ ¼å¿é¡»ä¸ºæ­£æ?
            df.loc[df[col] <= 0, col] = np.nan
            
        # 4. é»è¾å³ç³»éªè¯
        df = self._validate_price_logic(df)
        
        # 5. ç¼ºå¤±å¼å¤ç?
        df = self._handle_missing_values(df)
        
        return df
        
    def clean_financial_data(self, df):
        """æ¸æ´è´¢å¡æ°æ®"""
        # 1. ä»£ç æ åå?
        if 'è¡ç¥¨ä»£ç ' in df.columns:
            df['stock_code'] = df['è¡ç¥¨ä»£ç '].astype(str).str.zfill(6)
            
        # 2. æ°å¼å­æ®µå¤ç?
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        # 3. ææ¬å­æ®µå¤ç
        text_cols = df.select_dtypes(include=[object]).columns
        for col in text_cols:
            df[col] = df[col].astype(str).str.strip()
            
        # 4. å»é¤å¨ä¸ºNaNçè¡
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
            # åè®¾6ä½æ°å­ä»£ç ï¼èªå¨æ·»å äº¤ææ
            if len(code_str) == 6:
                if code_str.startswith(('0', '3')):
                    return f"SZ.{code_str}"
                elif code_str.startswith(('6', '9')):
                    return f"SH.{code_str}"
            return code_str
```

### 4.3 å¼å¸¸æ£æµä¸å¤ç

```python
class AnomalyDetector:
    def detect_price_anomalies(self, df):
        """æ£æµä»·æ ¼å¼å¸?""
        anomalies = []
        
        # 1. ä»·æ ¼è·³å¨æ£æµ?(æ¥åæ¶¨è·å¹è¿å¤?
        df['pct_change'] = df['close'].pct_change()
        large_jumps = df[abs(df['pct_change']) > 0.2]  # 20%ä»¥ä¸è·³å¨
        
        # 2. æäº¤éå¼å¸¸æ£æµ?
        volume_mean = df['volume'].rolling(20).mean()
        volume_std = df['volume'].rolling(20).std()
        volume_anomalies = df[df['volume'] > (volume_mean + 3 * volume_std)]
        
        # 3. ä»·æ ¼å³ç³»å¼å¸¸ (å¼ç?æé«? æä½?æ¶çç­?
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
        # ååå¡«å (éç¨äºäº¤ææ¥æ°æ®)
        df_filled = df.fillna(method='ffill')
        
        # çº¿æ§æå?(éç¨äºè¿ç»­æ¶é´åºå?
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df_filled[numeric_cols] = df_filled[numeric_cols].interpolate(method='linear')
        
        # ååå¡«åå©ä½ç¼ºå¤±å?
        df_filled = df_filled.fillna(method='bfill')
        
        return df_filled
```

## 5. æ°æ®åç±»ä¸ç»´åº¦åå?

### 5.1 åç±»ä½ç³»è®¾è®¡

#### 5.1.1 ææ°æ®ç±»ååç±?
```
æ°æ®åç±»ä½ç³»:
âââ è¡ææ°æ®
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
âââ è´¢å¡æ°æ®
â?  âââ èµäº§è´åºè¡¨ (balance_sheet)
â?  âââ å©æ¶¦è¡?(income_statement)
â?  âââ ç°éæµéè¡?(cash_flow)
â?  âââ è´¢å¡æ¯ç (financial_ratios)
âââ åºç¡ä¿¡æ¯æ°æ®
â?  âââ è¡ç¥¨åè¡¨ (stock_list)
â?  âââ è¡ä¸åç±» (industry)
â?  âââ ææ°æå (index_constituents)
âââ è¡çæ°æ®
    âââ ææ¯ææ ?(technical_indicators)
    âââ å å­æ°æ® (factors)
    âââ åæµç»æ (backtest_results)
```

#### 5.1.2 ææ¶é´ç»´åº¦åç±?
- **åå²å¨éæ°æ®**: ææåå²æ°æ®ï¼ç¨äºæ¨¡åè®­ç»
- **æ»å¨çªå£æ°æ®**: æè¿Nå¹´æ°æ®ï¼ç¨äºå®æ¶åæ
- **å­£åº¦åçæ°æ®**: æè´¢å¡å­£åº¦ååï¼ç¨äºå­£æ¥åæ
- **å¹´åº¦æ±æ»æ°æ?*: æå¹´åº¦æ±æ»ï¼ç¨äºå¹´åº¦å¯¹æ¯

### 5.2 åç±»å¤çå®ç°

```python
class DataClassifier:
    def __init__(self):
        self.classification_rules = self._load_classification_rules()
        
    def classify_by_frequency(self, df, date_col='date'):
        """æé¢çåç±»æ°æ?""
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col])
        
        # è®¡ç®æ¶é´é´é
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
        """æåå®¹åç±»æ°æ?""
        column_set = set(df.columns)
        
        # è´¢å¡æ°æ®ç¹å¾å?
        financial_keywords = ['èµäº§', 'è´å?, 'å©æ¶¦', 'æ¶å¥', 'ç°éæµ?, 'æ¯ç']
        financial_cols = [col for col in column_set 
                         if any(keyword in str(col) for keyword in financial_keywords)]
        
        # è¡ææ°æ®ç¹å¾å?
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
            
        # è¿åæå¨æåç»çæ°æ®å­å¸
        return {period: group.drop('period', axis=1) 
                for period, group in df.groupby('period')}
```

## 6. æ°æ®åºå­å¨æ¹æ¡?

### 6.1 å­å¨æ¶æè®¾è®¡

#### 6.1.1 æ··åå­å¨ç­ç¥
```
å­å¨æ¶æ:
âââ SQLiteæ°æ®åº?(è½»éçº§ï¼ç¨äºåæ°æ®åæ¥è¯¢)
â?  âââ metadata.db    # åæ°æ®è¡¨
â?  âââ stock_info.db  # è¡ç¥¨åºæ¬ä¿¡æ¯
â?  âââ index_info.db  # ææ°ä¿¡æ¯
âââ Parquetæä»¶å­å¨ (é«æ§è½ï¼ç¨äºå¤§éè¡ææ°æ?
â?  âââ daily/        # æ¥çº¿æ°æ®
â?  âââ weekly/       # å¨çº¿æ°æ®
â?  âââ monthly/      # æçº¿æ°æ®
â?  âââ intraday/     # åéæ°æ®
âââ HDF5æä»¶å­å¨ (å¯éï¼ç¨äºå¤æè´¢å¡æ°æ®)
    âââ financial/    # è´¢å¡æ°æ®
    âââ factors/      # å å­æ°æ®
```

#### 6.1.2 è¡¨ç»æè®¾è®?

**1. åæ°æ®è¡¨ (metadata)**
```sql
CREATE TABLE metadata (
    id INTEGER PRIMARY KEY,
    data_type TEXT NOT NULL,      -- 'market', 'financial', 'intraday'
    frequency TEXT,               -- 'daily', 'weekly', 'monthly', '5min'
    stock_code TEXT NOT NULL,
    start_date DATE,
    end_date DATE,
    file_path TEXT,               -- Parquetæä»¶è·¯å¾
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
    is_st INTEGER,               -- æ¯å¦ST
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

### 6.2 æ°æ®åå¥å®ç°

```python
class DatabaseManager:
    def __init__(self, db_path='zephyr_alpha.db', parquet_dir='data/parquet'):
        self.db_path = Path(db_path)
        self.parquet_dir = Path(parquet_dir)
        self.parquet_dir.mkdir(parents=True, exist_ok=True)
        
    def save_market_data(self, df, frequency='daily', adj_type='raw'):
        """ä¿å­è¡ææ°æ®å°æ··åå­å?""
        if df.empty:
            return
            
        # 1. ä¿å­å°Parquetæä»¶
        parquet_path = self._save_to_parquet(df, frequency, adj_type)
        
        # 2. æ´æ°åæ°æ®è¡¨
        self._update_metadata(df, frequency, adj_type, parquet_path)
        
        # 3. å¯éï¼ä¿å­å°SQLiteï¼ç¨äºå°è§æ¨¡æ¥è¯¢ï¼?
        if frequency == 'daily':
            self._save_to_sqlite(df, 'daily_market_data')
            
    def _save_to_parquet(self, df, frequency, adj_type):
        """ä¿å­å°Parquetæä»¶"""
        # æè¡ç¥¨ä»£ç ååºå­å?
        partition_cols = ['stock_code'] if 'stock_code' in df.columns else ['code']
        
        # æå»ºæä»¶è·¯å¾
        file_path = self.parquet_dir / frequency / adj_type
        file_path.mkdir(parents=True, exist_ok=True)
        
        # ä¿å­ä¸ºParquet
        df.to_parquet(
            file_path / f"{frequency}_{adj_type}.parquet",
            partition_cols=partition_cols,
            compression='snappy'
        )
        
        return str(file_path)
        
    def _update_metadata(self, df, frequency, adj_type, file_path):
        """æ´æ°åæ°æ®è¡¨"""
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
        
        # æå¥ææ´æ°åæ°æ®
        # ... å·ä½å®ç°
        
        conn.close()
        
    def save_financial_data(self, df):
        """ä¿å­è´¢å¡æ°æ®"""
        # è´¢å¡æ°æ®æ´éåä¿å­ä¸ºParquet + åç¬çè¡¨
        file_path = self.parquet_dir / 'financial' / 'quarterly'
        file_path.mkdir(parents=True, exist_ok=True)
        
        # ææ¥åæåè¡ç¥¨ä»£ç åå?
        df.to_parquet(
            file_path / "financial_data.parquet",
            partition_cols=['report_date', 'stock_code'],
            compression='snappy'
        )
```

### 6.3 æ°æ®æ¥è¯¢æ¥å£

```python
class DataQuery:
    def __init__(self, db_manager):
        self.db = db_manager
        
    def get_stock_data(self, stock_codes, start_date, end_date, frequency='daily'):
        """è·åè¡ç¥¨æ°æ®"""
        # 1. ä»åæ°æ®è¡¨æ¥æ¾æä»¶ä½ç½?
        parquet_files = self._locate_parquet_files(stock_codes, frequency)
        
        # 2. ä»Parquetæä»¶è¯»åæ°æ®
        data_frames = []
        for file_path in parquet_files:
            df = pd.read_parquet(file_path)
            # ç­éæ¶é´åè¡ç¥¨ä»£ç 
            mask = (df['date'] >= start_date) & (df['date'] <= end_date)
            if stock_codes:
                mask = mask & df['code'].isin(stock_codes)
            filtered_df = df.loc[mask]
            data_frames.append(filtered_df)
            
        return pd.concat(data_frames, ignore_index=True) if data_frames else pd.DataFrame()
        
    def get_financial_data(self, stock_codes, report_date=None):
        """è·åè´¢å¡æ°æ®"""
        # ç±»ä¼¼é»è¾ï¼ä»Parquetæä»¶è¯»å
        pass
        
    def get_stock_info(self, stock_codes=None):
        """è·åè¡ç¥¨åºæ¬ä¿¡æ¯"""
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
        
        # åå§ååç»ä»¶
        self.extractor = ZipExtractor(
            self.source_dir / "Aè¡æ°æ®_zip",
            self.output_dir / "extracted"
        )
        self.csv_reader = CSVReader(self.source_dir / "CSVè¡ææ°æ®")
        self.financial_reader = FinancialDataReader(
            self.source_dir / "ä¸å¸å¬å¸è´¢å¡ä¿¡æ¯" / "åå²è¯¦ç»æ°æ®"
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
        print("Aè¡æ°æ®å¤çæµæ°´çº¿å¯å¨")
        print("=" * 60)
        
        # æ­¥éª¤1: æåè§£å
        print("\n[1/5] æååè§£åæ°æ?..")
        self.extractor.extract_all(force=False)
        
        # æ­¥éª¤2: è¯»ååå§æ°æ®
        print("\n[2/5] è¯»ååå§æ°æ®...")
        market_data = self.csv_reader.read_all_files(pattern="*.csv")
        financial_data = self.financial_reader.read_quarterly_data()
        
        # æ­¥éª¤3: æ°æ®æ¸æ´
        print("\n[3/5] æ°æ®æ¸æ´åæ åå...")
        cleaned_market = self.cleaner.clean_market_data(market_data)
        cleaned_financial = self.cleaner.clean_financial_data(financial_data)
        
        # æ­¥éª¤4: æ°æ®åç±»
        print("\n[4/5] æ°æ®åç±»åç»´åº¦åå?..")
        market_classified = self.classifier.classify_by_frequency(cleaned_market)
        financial_classified = self.classifier.classify_by_content(cleaned_financial)
        
        # æ­¥éª¤5: å­å¨å°æ°æ®åº
        print("\n[5/5] å­å¨å°æ°æ®åº...")
        self.db_manager.save_market_data(cleaned_market, frequency='daily')
        self.db_manager.save_financial_data(cleaned_financial)
        
        # çæå¤çæ¥å
        self._generate_report(cleaned_market, cleaned_financial)
        
        print("\n" + "=" * 60)
        print("å¤çå®æï¼?)
        print("=" * 60)
        
    def _generate_report(self, market_data, financial_data):
        """çæå¤çæ¥å"""
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
        
        # ä¿å­æ¥åä¸ºJSON
        report_path = self.output_dir / "processing_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
            
        print(f"å¤çæ¥åå·²ä¿å­? {report_path}")
```

### 7.2 å¢éæ´æ°æºå¶

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
        """å¢éæ´æ°æ°æ®"""
        new_files = self.check_for_updates()
        
        if not new_files:
            print("æ²¡æåç°æ°æ°æ®ï¼æ éæ´æ°")
            return
            
        print(f"åç° {len(new_files)} ä¸ªæ°æä»¶éè¦å¤ç?)
        
        # åªå¤çæ°æä»¶
        for zip_file in new_files:
            print(f"å¤çæ°æä»? {zip_file.name}")
            # è§£åæ°æä»?
            # è¯»åæ°æ°æ?
            # æ¸æ´åæ åå
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

### 8.1 ç¯å¢è¦æ±
```yaml
python_version: ">=3.8"
dependencies:
  - pandas>=1.3.0
  - numpy>=1.21.0
  - sqlite3 (åç½®)
  - pyarrow>=6.0.0  # Parquetæ¯æ
  - openpyxl>=3.0.0  # Excelæ¯æ
  - tqdm>=4.62.0    # è¿åº¦æ?
```

### 8.2 éç½®æä»¶ç¤ºä¾
```yaml
# config.yaml
data_pipeline:
  source_dir: "D:/ZephyrAlpha/Aè¡æ°æ?éåäº¤ææ°æ®"
  output_dir: "D:/ZephyrAlpha/processed_data"
  
  processing:
    max_workers: 4           # å¹¶è¡å¤çæ?
    chunk_size: 100000       # ååå¤§å°
    memory_limit_gb: 8       # åå­éå¶
    
  cleaning:
    price_range: [0, 10000]  # ä»·æ ¼åçèå´
    volume_threshold: 1e9    # æäº¤éå¼å¸¸éå?
    pct_chg_limit: 0.2       # æ¶¨è·å¹éå?
    
  storage:
    db_path: "zephyr_alpha.db"
    parquet_compression: "snappy"
    hdf5_compression: "gzip"
    
  logging:
    level: "INFO"
    file: "data_pipeline.log"
    max_size_mb: 100
```

### 8.3 è¿è¡èæ¬
```python
# run_pipeline.py
import yaml
from pathlib import Path
from a_share_pipeline import AShareDataPipeline

def main():
    # å è½½éç½®
    config_path = Path("config.yaml")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # åå§åæµæ°´çº¿
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
        """è·åå­å¨ä½¿ç¨æåµ"""
        # æ£æ¥æ°æ®åºå¤§å°
        # æ£æ¥Parquetæä»¶å¤§å°
        # æ£æ¥ç£çç©ºé?
        pass
        
    def cleanup_old_data(self, days_to_keep=365):
        """æ¸çæ§æ°æ?""
        # å é¤è¶è¿æå®å¤©æ°çä¸´æ¶æä»?
        # å½æ¡£åå²æ°æ®
        pass
```

## 9. æ§è½ä¼åå»ºè®®

### 9.1 åå­ä¼å
1. **ååå¤ç**: å¤§æä»¶ååè¯»åï¼é¿ååå­æº¢åº
2. **æ°æ®ç±»åä¼å**: ä½¿ç¨åéçæ°å¼ç±»åï¼float32 vs float64ï¼?
3. **åæ¶éæ¾åå­**: å¤çå®æååæ¶å é¤ä¸éè¦çæ°æ®

### 9.2 å­å¨ä¼å
1. **åå¼å­å¨**: Parquetæ ¼å¼å¤©ç¶éååå¼æ¥è¯¢
2. **ååºå­å¨**: ææ¶é´ãè¡ç¥¨ä»£ç ååºï¼æé«æ¥è¯¢æç
3. **åç¼©éæ©**: Snappyåç¼©éåº¦å¿«ï¼Gzipåç¼©çé«

### 9.3 å¤çéåº¦ä¼å
1. **å¹¶è¡å¤ç**: å¤è¿ç¨å¤çä¸åè¡ç¥¨ææ¶é´æ®?
2. **åéåæä½?*: ä½¿ç¨pandasåéåå½æ°ï¼é¿åå¾ªç¯
3. **ç¼å­æºå¶**: ç¼å­é¢ç¹è®¿é®çåæ°æ®ååºç¡ä¿¡æ¯

## 10. æéæ¢å¤ä¸å¤ä»?

### 10.1 æ£æ¥ç¹æºå¶
```python
class CheckpointManager:
    def __init__(self, checkpoint_dir):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
    def save_checkpoint(self, stage, data):
        """ä¿å­æ£æ¥ç¹"""
        checkpoint_file = self.checkpoint_dir / f"{stage}.checkpoint"
        # ä¿å­å¤çç¶æåæ°æ®
        pass
        
    def load_checkpoint(self, stage):
        """å è½½æ£æ¥ç¹"""
        checkpoint_file = self.checkpoint_dir / f"{stage}.checkpoint"
        if checkpoint_file.exists():
            # ä»æ£æ¥ç¹æ¢å¤
            pass
        return None
        
    def resume_from_checkpoint(self, pipeline):
        """ä»æ£æ¥ç¹æ¢å¤å¤ç"""
        last_stage = self._find_last_checkpoint()
        if last_stage:
            print(f"ä»æ£æ¥ç¹æ¢å¤: {last_stage}")
            # æ¢å¤å¤çæµç¨
            pass
```

### 10.2 å¤ä»½ç­ç¥
1. **æ¯æ¥å¢éå¤ä»½**: å¤ä»½å½æ¥æ°å¢æ°æ®
2. **æ¯å¨å¨éå¤ä»½**: å¤ä»½æ´ä¸ªæ°æ®åº?
3. **å¼å°å¤ä»½**: éè¦æ°æ®å¤ä»½å°ä¸åç£çæäºå­å?

---

## æ»ç»

è¿ä¸ªèå¾æä¾äºä¸ä¸ªå®æ´çAè¡åå²æ°æ®å¤çæ¹æ¡ï¼ä»åå§æ°æ®æåå°æ°æ®åºå­å¨çå®æ´æµç¨ãæ¹æ¡ç¹ç¹ï¼

1. **å¨é¢æ?*: è¦çè¡ææ°æ®ãè´¢å¡æ°æ®ãåéæ°æ®ç­å¤ç§æ°æ®ç±»å
2. **å®ç¨æ?*: æä¾å³ç¨çä»£ç ç¤ºä¾åéç½®æ¨¡æ¿
3. **å¯æ©å±æ?*: æ¨¡ååè®¾è®¡ï¼æäºæ©å±æ°çæ°æ®ç±»å
4. **é«ææ?*: éç¨æ··åå­å¨ç­ç¥ï¼å¹³è¡¡æ¥è¯¢æçåå­å¨ææ¬
5. **å¥å£®æ?*: åå«éè¯¯å¤çãæ£æ¥ç¹ãå¤ä»½æ¢å¤æºå?

æ¨å¯ä»¥æ ¹æ®è¿ä¸ªèå¾éæ­¥å®ç°æ°æ®å¤çç³»ç»ï¼ä¹å¯ä»¥æ ¹æ®å®ééæ±è°æ´åä¸ªæ¨¡åãå»ºè®®åä»æ ¸å¿çæ¥çº¿æ°æ®å¤çå¼å§ï¼éæ­¥æ©å±å°å¶ä»æ°æ®ç±»åã
---

## 11. 文档治理

### 11.1 System_Manifest.md索引

```markdown
#### Layer 0: 系统架构
##### 0.BLUEPRI. Doc Temp A Stock
- **模块ID**: DOC_TEMP_A_STOCK_BLUEPRI
- **蓝图文档**: [A_STOCK_DATA_PROCESSING_BLUEPRINT.md](./06_CONSTRUCTION_DOCS\01_BLUEPRINTS\A_STOCK_DATA_PROCESSING_BLUEPRINT.md)
- **技术规格书**: 待创建
- **职责**: å¨ç³»ç»?
- **状态**: Active
```

### 11.2 模块职责边界

| 模块 | 职责 | 边界 |
|------|------|------|
| **Doc Temp A Stock** | å¨ç³»ç»? | **核心模块** |

### 11.3 版本管理

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-01 | 初始版本创建 | 首席蓝图架构师 |

---

**蓝图版本**: v1.0.0 | **创建日期**: 2026-04-01 | **状态**: Active
