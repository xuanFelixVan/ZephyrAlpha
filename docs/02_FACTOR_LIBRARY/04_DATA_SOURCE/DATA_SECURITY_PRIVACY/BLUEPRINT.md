---
module_id: DATA_SECURITY_PRIVACY_BP_001
version: 1.0.0
status: Blueprint
created_date: 2026-04-06
last_updated: 2026-04-06
owner: 首席架构师
standard_type: 模块蓝图
applicable_scope: 数据安全与隐私保护系统
compliance_level: 专业标准
parent_document: ./DATA_SOURCE_LAYER_GAP_ANALYSIS_V2.md
dependencies:
  - Microsoft Presidio
  - cryptography
  - python-dotenv
---

# 数据安全与隐私保护蓝图

> **优先级**: 🔴 P0 (必备)
> **实施周期**: 1周
> **开源方案**: Microsoft Presidio + cryptography

---

## 1. 概述

### 1.1 定位与目标

数据安全与隐私保护系统是专业量化机构的**核心基础设施**，用于：
- 自动识别PII（个人身份信息）
- 敏感数据脱敏和匿名化
- 数据加密存储
- 访问审计和合规管理

### 1.2 业务价值

| 价值维度 | 说明 |
|----------|------|
| **合规性** | 满足GDPR、个保法等法规要求 |
| **数据安全** | 防止敏感数据泄露 |
| **信任度** | 提升数据资产可信度 |
| **风险管理** | 降低数据安全风险 |

### 1.3 个人适用性评估

| 维度 | 评分 | 说明 |
|------|------|------|
| **开发复杂度** | ⭐⭐ | 低，Presidio封装完善 |
| **维护成本** | ⭐ | 极低，配置驱动 |
| **学习曲线** | ⭐⭐ | 低，文档完善 |
| **个人可行性** | ⭐⭐⭐⭐⭐ | 高，适合个人项目 |

---

## 2. 架构设计

### 2.1 Layer定位

```
Layer 0: 数据源层
├── 数据采集
├── 数据清洗
├── 数据安全与隐私保护 ← 本模块
│   ├── PII识别
│   ├── 数据脱敏
│   ├── 数据加密
│   └── 访问审计
├── 数据存储
└── 数据质量
```

### 2.2 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                   数据安全与隐私保护系统                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │ 原始数据     │───▶│  Presidio    │───▶│ 安全数据     │ │
│  │ (含PII)      │    │  (识别/脱敏) │    │ (已脱敏)     │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
│         │                   │                    │          │
│         │                   │                    │          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │ PII识别器    │    │ 脱敏策略     │    │ 加密存储     │ │
│  │ (NLP+正则)   │    │ (可配置)     │    │ (AES-256)    │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 开源方案选择

### 3.1 Microsoft Presidio - PII识别与脱敏

**GitHub**: https://github.com/microsoft/presidio
**Stars**: 3.5k+
**许可证**: MIT

**选择理由**:
- ✅ **微软官方**: 企业级解决方案，质量有保障
- ✅ **功能全面**: 支持多种PII类型识别
- ✅ **可扩展**: 支持自定义识别器和脱敏器
- ✅ **Python友好**: 提供Python SDK
- ✅ **开源免费**: MIT许可证，无商业限制

### 3.2 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| **PII识别** | Presidio Analyzer | 识别PII实体 |
| **数据脱敏** | Presidio Anonymizer | 脱敏处理 |
| **数据加密** | cryptography | AES-256加密 |
| **密钥管理** | python-dotenv | 环境变量管理 |

---

## 4. 核心功能设计

### 4.1 PII识别器

```python
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.predefined_recognizers import (
    CreditCardRecognizer,
    EmailRecognizer,
    PhoneRecognizer,
    UrlRecognizer,
    IpRecognizer,
    SpacyRecognizer
)
from presidio_analyzer.nlp_engine import NlpEngineProvider
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class PIIIdentifier:
    """PII识别器"""
    
    SUPPORTED_ENTITIES = [
        "CREDIT_CARD",
        "EMAIL_ADDRESS",
        "PHONE_NUMBER",
        "URL",
        "IP_ADDRESS",
        "PERSON",
        "LOCATION",
        "ORGANIZATION",
        "DATE_TIME",
        "NRP",
        "MEDICAL_LICENSE",
        "US_BANK_NUMBER",
        "US_DRIVER_LICENSE",
        "US_PASSPORT",
        "US_SSN",
        "UK_NHS",
        "SG_NRIC_FIN",
        "AU_ABN",
        "AU_ACN",
        "AU_TFN",
        "AU_MEDICARE",
        "IN_PAN",
        "IN_AADHAAR",
        "IN_VEHICLE_REGISTRATION",
        "IT_FISCAL_CODE",
        "IT_DRIVER_LICENSE",
        "IT_VAT_CODE",
        "IT_PASSPORT",
        "IT_IDENTITY_CARD",
        "ES_NIF",
        "ES_NIE",
        "ES_DNI",
        "PL_PESEL",
        "FR_NIR",
        "FR_CNI",
        "FR_PASSESPORT",
        "FR_PERMIS_CONDUIT",
        "FR_SECU_SOCIALE",
        "FR_TVA",
        "FR_SIREN",
        "FR_SIRET",
        "FR_IBAN",
        "FR_PHONE_NUMBER",
        "FR_EMAIL",
        "FR_ADDRESS",
        "FR_ZIP_CODE",
        "FR_DATE_OF_BIRTH",
        "CN_PHONE_NUMBER",
        "CN_ID_CARD",
        "CN_PASSPORT",
        "CN_BANK_CARD",
        "CN_LICENSE_PLATE"
    ]
    
    def __init__(self, language: str = "en"):
        """
        初始化PII识别器
        
        Args:
            language: 语言代码
        """
        self.language = language
        self.analyzer = self._create_analyzer()
        
    def _create_analyzer(self) -> AnalyzerEngine:
        """创建分析器引擎"""
        registry = RecognizerRegistry()
        registry.load_predefined_recognizers()
        
        nlp_configuration = {
            "nlp_engine_name": "spacy",
            "models": [
                {"lang_code": "en", "model_name": "en_core_web_lg"},
                {"lang_code": "zh", "model_name": "zh_core_web_lg"}
            ]
        }
        
        nlp_engine = NlpEngineProvider(nlp_configuration=nlp_configuration).create_engine()
        
        analyzer = AnalyzerEngine(
            registry=registry,
            nlp_engine=nlp_engine,
            supported_languages=["en", "zh"]
        )
        
        return analyzer
    
    def analyze_text(
        self,
        text: str,
        entities: List[str] = None,
        language: str = None,
        score_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        分析文本中的PII
        
        Args:
            text: 待分析文本
            entities: 要识别的实体类型
            language: 语言代码
            score_threshold: 置信度阈值
            
        Returns:
            PII实体列表
        """
        if entities is None:
            entities = self.SUPPORTED_ENTITIES
            
        if language is None:
            language = self.language
            
        results = self.analyzer.analyze(
            text=text,
            entities=entities,
            language=language,
            score_threshold=score_threshold
        )
        
        return [
            {
                "entity_type": result.entity_type,
                "start": result.start,
                "end": result.end,
                "score": result.score,
                "text": text[result.start:result.end]
            }
            for result in results
        ]
    
    def analyze_dataframe(
        self,
        df: 'pd.DataFrame',
        columns: List[str] = None,
        sample_size: int = 100
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        分析DataFrame中的PII
        
        Args:
            df: DataFrame
            columns: 要分析的列
            sample_size: 采样大小
            
        Returns:
            PII分析结果
        """
        import pandas as pd
        
        if columns is None:
            columns = df.select_dtypes(include=['object']).columns.tolist()
            
        results = {}
        
        for col in columns:
            sample = df[col].dropna().head(sample_size).astype(str)
            pii_found = []
            
            for idx, value in enumerate(sample):
                pii_results = self.analyze_text(value)
                if pii_results:
                    pii_found.append({
                        "index": idx,
                        "value": value[:50] + "..." if len(value) > 50 else value,
                        "pii": pii_results
                    })
                    
            if pii_found:
                results[col] = pii_found
                
        return results
```

### 4.2 数据脱敏器

```python
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import (
    RecognizerResult,
    AnonymizerConfig,
    OperatorConfig
)
from typing import List, Dict, Any, Optional
import hashlib
import secrets

class DataAnonymizer:
    """数据脱敏器"""
    
    OPERATORS = {
        "replace": OperatorConfig("replace", {"new_value": "<REDACTED>"}),
        "mask": OperatorConfig("mask", {"masking_char": "*", "chars_to_mask": 4, "from_end": False}),
        "hash": OperatorConfig("hash", {"hash_type": "sha256"}),
        "redact": OperatorConfig("redact"),
        "encrypt": OperatorConfig("encrypt", {"key": secrets.token_bytes(32)}),
        "fake": OperatorConfig("fake", {"fake_value": "fake_value"}),
        "custom": None
    }
    
    def __init__(self):
        """初始化数据脱敏器"""
        self.anonymizer = AnonymizerEngine()
        
    def anonymize_text(
        self,
        text: str,
        analyzer_results: List[Dict[str, Any]],
        operator: str = "replace"
    ) -> str:
        """
        脱敏文本
        
        Args:
            text: 原始文本
            analyzer_results: 分析结果
            operator: 脱敏操作符
            
        Returns:
            脱敏后的文本
        """
        recognizer_results = [
            RecognizerResult(
                entity_type=r["entity_type"],
                start=r["start"],
                end=r["end"],
                score=r["score"]
            )
            for r in analyzer_results
        ]
        
        operator_config = self.OPERATORS.get(operator, self.OPERATORS["replace"])
        
        result = self.anonymizer.anonymize(
            text=text,
            analyzer_results=recognizer_results,
            operators={"DEFAULT": operator_config}
        )
        
        return result.text
    
    def anonymize_dataframe(
        self,
        df: 'pd.DataFrame',
        pii_analysis: Dict[str, List[Dict[str, Any]]],
        operator: str = "mask"
    ) -> 'pd.DataFrame':
        """
        脱敏DataFrame
        
        Args:
            df: DataFrame
            pii_analysis: PII分析结果
            operator: 脱敏操作符
            
        Returns:
            脱敏后的DataFrame
        """
        import pandas as pd
        
        df_anonymized = df.copy()
        
        for col, pii_list in pii_analysis.items():
            for pii_info in pii_list:
                idx = pii_info["index"]
                original_value = str(df_anonymized.loc[idx, col])
                
                analyzer_results = pii_info["pii"]
                anonymized_value = self.anonymize_text(
                    original_value,
                    analyzer_results,
                    operator
                )
                
                df_anonymized.loc[idx, col] = anonymized_value
                
        return df_anonymized
    
    @staticmethod
    def mask_credit_card(card_number: str) -> str:
        """脱敏信用卡号"""
        if len(card_number) < 8:
            return "*" * len(card_number)
        return card_number[:4] + "*" * (len(card_number) - 8) + card_number[-4:]
    
    @staticmethod
    def mask_email(email: str) -> str:
        """脱敏邮箱"""
        if "@" not in email:
            return email
        local, domain = email.split("@", 1)
        if len(local) <= 2:
            return "*" * len(local) + "@" + domain
        return local[0] + "*" * (len(local) - 2) + local[-1] + "@" + domain
    
    @staticmethod
    def mask_phone(phone: str) -> str:
        """脱敏电话号码"""
        digits = ''.join(filter(str.isdigit, phone))
        if len(digits) < 7:
            return "*" * len(phone)
        return phone[:3] + "*" * (len(phone) - 6) + phone[-3:]
    
    @staticmethod
    def mask_id_card(id_number: str) -> str:
        """脱敏身份证号"""
        if len(id_number) < 10:
            return "*" * len(id_number)
        return id_number[:3] + "*" * (len(id_number) - 6) + id_number[-3:]
```

### 4.3 数据加密器

```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import os
from typing import Union
import logging

logger = logging.getLogger(__name__)

class DataEncryptor:
    """数据加密器"""
    
    def __init__(self, password: str = None, key: bytes = None):
        """
        初始化数据加密器
        
        Args:
            password: 密码（用于派生密钥）
            key: 直接提供的密钥
        """
        if key:
            self.fernet = Fernet(key)
        elif password:
            self.fernet = Fernet(self._derive_key(password))
        else:
            self.fernet = Fernet(Fernet.generate_key())
            
    def _derive_key(self, password: str, salt: bytes = None) -> bytes:
        """
        从密码派生密钥
        
        Args:
            password: 密码
            salt: 盐值
            
        Returns:
            派生密钥
        """
        if salt is None:
            salt = os.urandom(16)
            
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt(self, data: Union[str, bytes]) -> bytes:
        """
        加密数据
        
        Args:
            data: 待加密数据
            
        Returns:
            加密后的数据
        """
        if isinstance(data, str):
            data = data.encode()
        return self.fernet.encrypt(data)
    
    def decrypt(self, encrypted_data: bytes) -> str:
        """
        解密数据
        
        Args:
            encrypted_data: 加密数据
            
        Returns:
            解密后的数据
        """
        return self.fernet.decrypt(encrypted_data).decode()
    
    def encrypt_file(self, input_path: str, output_path: str):
        """
        加密文件
        
        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
        """
        with open(input_path, 'rb') as f:
            data = f.read()
            
        encrypted_data = self.fernet.encrypt(data)
        
        with open(output_path, 'wb') as f:
            f.write(encrypted_data)
            
        logger.info(f"Encrypted file: {input_path} -> {output_path}")
    
    def decrypt_file(self, input_path: str, output_path: str):
        """
        解密文件
        
        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
        """
        with open(input_path, 'rb') as f:
            encrypted_data = f.read()
            
        data = self.fernet.decrypt(encrypted_data)
        
        with open(output_path, 'wb') as f:
            f.write(data)
            
        logger.info(f"Decrypted file: {input_path} -> {output_path}")
    
    @staticmethod
    def generate_key() -> bytes:
        """生成新密钥"""
        return Fernet.generate_key()
```

### 4.4 安全审计日志

```python
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import json
from pathlib import Path

class SecurityAuditLogger:
    """安全审计日志记录器"""
    
    def __init__(self, log_dir: str = "logs/security"):
        """
        初始化审计日志记录器
        
        Args:
            log_dir: 日志目录
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("security_audit")
        self.logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler(
            self.log_dir / f"audit_{datetime.now().strftime('%Y%m%d')}.log"
        )
        handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s'
        ))
        self.logger.addHandler(handler)
        
    def log_access(
        self,
        user: str,
        resource: str,
        action: str,
        result: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        记录访问日志
        
        Args:
            user: 用户
            resource: 资源
            action: 操作
            result: 结果
            details: 详情
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user,
            "resource": resource,
            "action": action,
            "result": result,
            "details": details or {}
        }
        
        self.logger.info(json.dumps(log_entry))
        
    def log_pii_detection(
        self,
        source: str,
        pii_types: list,
        count: int,
        action_taken: str
    ):
        """
        记录PII检测日志
        
        Args:
            source: 数据源
            pii_types: PII类型
            count: 数量
            action_taken: 采取的操作
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": "pii_detection",
            "source": source,
            "pii_types": pii_types,
            "count": count,
            "action_taken": action_taken
        }
        
        self.logger.warning(json.dumps(log_entry))
        
    def log_encryption(
        self,
        resource: str,
        operation: str,
        success: bool
    ):
        """
        记录加密操作日志
        
        Args:
            resource: 资源
            operation: 操作
            success: 是否成功
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": "encryption",
            "resource": resource,
            "operation": operation,
            "success": success
        }
        
        self.logger.info(json.dumps(log_entry))
```

---

## 5. 实施路径

### Phase 1: PII识别（2天）

**任务清单**:
- [ ] 安装Presidio
- [ ] 配置NLP模型
- [ ] 测试PII识别

**验收标准**:
- ✅ 支持中英文PII识别
- ✅ 识别准确率>90%

### Phase 2: 数据脱敏（2天）

**任务清单**:
- [ ] 实现脱敏策略
- [ ] 集成到数据管道
- [ ] 测试脱敏效果

**验收标准**:
- ✅ 支持多种脱敏策略
- ✅ 脱敏后数据不可逆

### Phase 3: 加密与审计（3天）

**任务清单**:
- [ ] 实现数据加密
- [ ] 配置审计日志
- [ ] 集成测试

**验收标准**:
- ✅ 数据加密存储
- ✅ 审计日志完整

---

## 6. 配置文件

```yaml
# config/security.yaml
pii_detection:
  enabled: true
  language: "zh"
  entities:
    - CREDIT_CARD
    - EMAIL_ADDRESS
    - PHONE_NUMBER
    - IP_ADDRESS
    - CN_PHONE_NUMBER
    - CN_ID_CARD
    - CN_BANK_CARD
  score_threshold: 0.5
  
anonymization:
  default_operator: "mask"
  operators:
    CREDIT_CARD: "mask"
    EMAIL_ADDRESS: "mask"
    PHONE_NUMBER: "mask"
    CN_ID_CARD: "mask"
    
encryption:
  enabled: true
  algorithm: "AES-256"
  key_file: ".keys/encryption.key"
  
audit:
  enabled: true
  log_dir: "logs/security"
  retention_days: 90
```

---

## 7. 与现有系统集成

### 7.1 与数据采集集成

```python
# 在数据采集时自动检测PII
def secure_data_collection(data: pd.DataFrame) -> pd.DataFrame:
    """安全数据采集"""
    identifier = PIIIdentifier()
    anonymizer = DataAnonymizer()
    
    pii_analysis = identifier.analyze_dataframe(data)
    
    if pii_analysis:
        logger.warning(f"PII detected in data: {list(pii_analysis.keys())}")
        data = anonymizer.anonymize_dataframe(data, pii_analysis)
        
    return data
```

### 7.2 与权限管理集成

```python
# 在权限检查时记录审计日志
audit_logger = SecurityAuditLogger()

def check_permission_with_audit(user: str, resource: str, action: str) -> bool:
    """带审计的权限检查"""
    has_permission = permission_manager.check_permission(user, resource, action)
    
    audit_logger.log_access(
        user=user,
        resource=resource,
        action=action,
        result="GRANTED" if has_permission else "DENIED"
    )
    
    return has_permission
```

---

## 8. 维护成本评估

| 维护项 | 频率 | 时间 | 说明 |
|--------|------|------|------|
| **PII规则更新** | 每月 | 30分钟 | 更新识别规则 |
| **密钥轮换** | 每季度 | 15分钟 | 轮换加密密钥 |
| **审计日志检查** | 每周 | 15分钟 | 检查异常访问 |

**总维护成本**: 约 **1小时/月**

---

## 9. 风险评估

| 风险 | 等级 | 影响 | 缓解措施 |
|------|------|------|----------|
| **PII识别遗漏** | P1 | 数据泄露 | 多层检测 + 人工审核 |
| **密钥丢失** | P0 | 数据不可用 | 密钥备份 + 多地存储 |
| **性能影响** | P2 | 处理缓慢 | 异步处理 + 批量检测 |

---

## 10. 参考资料

- [Microsoft Presidio官方文档](https://microsoft.github.io/presidio/)
- [Presidio GitHub](https://github.com/microsoft/presidio)
- [cryptography文档](https://cryptography.io/)

---

**版本**: 1.0
**创建日期**: 2026-04-06
**状态**: Blueprint
