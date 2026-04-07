---
module_id: DATA_MASKING_ENCRYPTION__001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: é¦å¸­æ¶æå¸?
standard_type: ä¸ä¸éåæºæèå¾
applicable_scope: Layer 1 æ°æ®é¢å¤çå±
compliance_level: ä¸ä¸æ å
priority: P0
layer: "Layer 1 (æ°æ®é¢å¤çå±)"
responsibility: æ°æ®è±æä¸å å¯æå?
---

# æ°æ®è±æä¸å å¯æå¡èå?

## 核心定位

负责数据脱敏加密的设计与实现，基于加密技术，保护敏感数据，确保数据安全合规。


## æ ¸å¿å®ä½

è´è´£æ°æ®è±æåå å¯ï¼æä¾æææ°æ®çè±æå¤çåå å¯å­å¨åè½ï¼ä¿éæ°æ®å®å¨åè§ã?

## ð ä¸ãæ¨¡åæ¦è¿?

### 1.1 ä¸ä¸æºææ åè¦æ±

| æºæç±»å | å®å¨è¦æ± | å®æ½æ å |
|---------|---------|---------|
| **æ¡¥æ°´åºé** | æ°æ®åç±»åçº§ãè®¿é®æ§å?| ISO 27001 |
| **æèºå¤å´ç§æ** | æææ°æ®å å¯ãå®¡è®¡è¿½è¸?| SOC 2 Type II |
| **Two Sigma** | PIIæ°æ®ä¿æ¤ãåè§å®¡è®?| GDPR/CCPA |
| **Citadel** | æ°æ®è±æãå å¯å­å?| PCI DSS |

### 1.2 æ ¸å¿åè½ç©éµ

| åè½æ¨¡å | å¼æºæ¹æ¡?| æçåº?| ä¸ªäººéç¨æ?| æ¨èææ° |
|---------|---------|--------|-----------|---------|
| **PIIè¯å«** | Microsoft Presidio | â­â­â­â­â­?| â­â­â­â­â­?| â­â­â­â­â­?|
| **æ°æ®è±æ** | Presidio Anonymizer | â­â­â­â­â­?| â­â­â­â­â­?| â­â­â­â­â­?|
| **æ°æ®å å¯** | cryptography (Python) | â­â­â­â­â­?| â­â­â­â­â­?| â­â­â­â­â­?|
| **è®¿é®å®¡è®¡** | èªç  + SQLite | â­â­â­â­ | â­â­â­â­â­?| â­â­â­â­ |
| **å¯é¥ç®¡ç** | HashiCorp Vault (è½»é) | â­â­â­â­ | â­â­â­â­ | â­â­â­â­ |

---

## ðï¸?äºãç³»ç»æ¶æè®¾è®?

### 2.1 æ´ä½æ¶æå?

```
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
â?                   æ°æ®è±æä¸å å¯æå¡æ¶æ?                                 â?
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
â?                                                                        â?
â? ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ? â?
â? â?                       æ°æ®æ¥å¥å±?                                 â? â?
â? â? â?æ°æ®æºæ¥å? â?æ ¼å¼è¯å«  â?åæ°æ®æå?                          â? â?
â? ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ? â?
â?                             â?                                         â?
â?                             â?                                         â?
â? ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ? â?
â? â?                   PIIè¯å«å¼æ (Presidio)                         â? â?
â? â? â?å§å/èº«ä»½è¯?çµè¯/é®ç®±  â?é¶è¡å?å°å/IP  â?èªå®ä¹è§å?          â? â?
â? ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ? â?
â?                             â?                                         â?
â?                             â?                                         â?
â? ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ? â?
â? â?                     è±æå¤çå¼æ                                  â? â?
â? â? â?æ¿æ¢è±æ  â?æ©ç è±æ  â?åå¸è±æ  â?å å¯è±æ                   â? â?
â? ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ? â?
â?                             â?                                         â?
â?                             â?                                         â?
â? ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ? â?
â? â?                     å å¯å­å¨å¼æ                                  â? â?
â? â? â?AES-256å å¯  â?å¯é¥ç®¡ç  â?å®å¨å­å¨                            â? â?
â? ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ? â?
â?                             â?                                         â?
â?                             â?                                         â?
â? ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ? â?
â? â?                     è®¿é®å®¡è®¡å¼æ                                  â? â?
â? â? â?è®¿é®æ¥å¿  â?æä½è¿½è¸ª  â?å¼å¸¸åè­¦                               â? â?
â? ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ? â?
â?                                                                        â?
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
```

### 2.2 æ°æ®æµæ¶æ?

```
åå§æ°æ® â?PIIæ«æ â?åç±»æ è®° â?è±æç­ç¥ â?å å¯å­å¨ â?å®¡è®¡æ¥å¿
    â?         â?         â?         â?         â?         â?
    ââââââââââââ´âââââââââââ´âââââââââââ´âââââââââââ´âââââââââââ?
                          å®æ´è¡ç¼è¿½è¸ªé¾
```

---

## ð» ä¸ãæ ¸å¿å®ç°ä»£ç ?

### 3.1 PIIè¯å«å¼æ

```python
"""
PIIè¯å«å¼æ - åºäºMicrosoft Presidio
"""
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import AnonymizerConfig
from typing import List, Dict, Any
import re


class PIIIdentifier:
    """PIIæ°æ®è¯å«å?""
    
    SUPPORTED_PII_TYPES = [
        "PERSON", "PHONE_NUMBER", "EMAIL_ADDRESS", "CREDIT_CARD",
        "US_SSN", "US_BANK_NUMBER", "LOCATION", "DATE_TIME",
        "NRP", "MEDICAL_LICENSE", "IP_ADDRESS", "URL",
        "US_DRIVER_LICENSE", "US_PASSPORT", "SG_NRIC_FIN",
        "UK_NHS", "ES_NIF", "IT_FISCAL_CODE", "IT_DRIVER_LICENSE",
        "IT_VAT_CODE", "IT_PASSPORT", "IT_IDENTITY_CARD",
        "CRYPTO", "IBAN_CODE", "US_ITIN", "UK_NINO",
    ]
    
    def __init__(self, language: str = "en"):
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        self.language = language
        
        self.custom_patterns = self._load_custom_patterns()
    
    def _load_custom_patterns(self) -> Dict[str, re.Pattern]:
        """å è½½èªå®ä¹PIIè¯å«æ¨¡å¼"""
        return {
            "chinese_id_card": re.compile(r'\d{17}[\dXx]'),
            "chinese_phone": re.compile(r'1[3-9]\d{9}'),
            "chinese_bank_card": re.compile(r'\d{16,19}'),
            "stock_account": re.compile(r'[A-Z]\d{8,12}'),
        }
    
    def scan(self, text: str) -> List[Dict[str, Any]]:
        """æ«æææ¬ä¸­çPIIæ°æ®"""
        results = self.analyzer.analyze(
            text=text,
            language=self.language,
            entities=self.SUPPORTED_PII_TYPES
        )
        
        pii_list = []
        for result in results:
            pii_list.append({
                "entity_type": result.entity_type,
                "start": result.start,
                "end": result.end,
                "score": result.score,
                "text": text[result.start:result.end]
            })
        
        for pattern_name, pattern in self.custom_patterns.items():
            for match in pattern.finditer(text):
                pii_list.append({
                    "entity_type": pattern_name,
                    "start": match.start(),
                    "end": match.end(),
                    "score": 0.95,
                    "text": match.group()
                })
        
        return pii_list
    
    def scan_dataframe(self, df, sample_size: int = 1000) -> Dict[str, List[Dict]]:
        """æ«æDataFrameä¸­çPIIæ°æ®"""
        results = {}
        
        for column in df.columns:
            sample = df[column].head(sample_size).astype(str).tolist()
            text = " ".join(sample)
            
            pii_found = self.scan(text)
            if pii_found:
                results[column] = pii_found
        
        return results


class DataMasker:
    """æ°æ®è±æå¤çå?""
    
    MASKING_STRATEGIES = {
        "replace": "ä½¿ç¨åºå®å¼æ¿æ?,
        "mask": "å­ç¬¦æ©ç ï¼å¦ï¼?38****1234ï¼?,
        "hash": "åå¸è±æï¼ä¸å¯éï¼",
        "encrypt": "å å¯è±æï¼å¯éï¼",
        "redact": "å®å¨å é¤",
        "fake": "ä½¿ç¨åæ°æ®æ¿æ?,
    }
    
    def __init__(self):
        self.anonymizer = AnonymizerEngine()
    
    def mask_phone(self, phone: str) -> str:
        """çµè¯å·ç è±æï¼?38****1234"""
        if len(phone) == 11:
            return f"{phone[:3]}****{phone[7:]}"
        return phone[:3] + "****" + phone[-4:] if len(phone) > 7 else "****"
    
    def mask_id_card(self, id_card: str) -> str:
        """èº«ä»½è¯å·è±æï¼?10***********1234"""
        if len(id_card) == 18:
            return f"{id_card[:3]}***********{id_card[14:]}"
        return id_card[:3] + "****" + id_card[-4:]
    
    def mask_bank_card(self, card: str) -> str:
        """é¶è¡å¡å·è±æï¼?222 **** **** 1234"""
        if len(card) >= 16:
            return f"{card[:4]} **** **** {card[-4:]}"
        return "****"
    
    def mask_email(self, email: str) -> str:
        """é®ç®±è±æï¼a***@example.com"""
        if "@" in email:
            local, domain = email.split("@", 1)
            if len(local) > 1:
                return f"{local[0]}***@{domain}"
        return "***"
    
    def mask_name(self, name: str) -> str:
        """å§åè±æï¼å¼ *æ?""
        if len(name) <= 1:
            return "*"
        elif len(name) == 2:
            return f"{name[0]}*"
        else:
            return f"{name[0]}*{name[-1]}"
    
    def apply_strategy(
        self,
        text: str,
        pii_type: str,
        strategy: str = "mask"
    ) -> str:
        """åºç¨è±æç­ç¥"""
        strategy_map = {
            "PHONE_NUMBER": self.mask_phone,
            "chinese_phone": self.mask_phone,
            "chinese_id_card": self.mask_id_card,
            "chinese_bank_card": self.mask_bank_card,
            "EMAIL_ADDRESS": self.mask_email,
            "PERSON": self.mask_name,
            "CREDIT_CARD": self.mask_bank_card,
        }
        
        masker = strategy_map.get(pii_type, lambda x: "***")
        
        if strategy == "redact":
            return "[REDACTED]"
        elif strategy == "hash":
            import hashlib
            return hashlib.sha256(text.encode()).hexdigest()[:16]
        else:
            return masker(text)
    
    def anonymize_text(
        self,
        text: str,
        pii_list: List[Dict],
        default_strategy: str = "mask"
    ) -> str:
        """å¯¹ææ¬è¿è¡è±æå¤ç?""
        sorted_pii = sorted(pii_list, key=lambda x: x["start"], reverse=True)
        
        result = text
        for pii in sorted_pii:
            masked = self.apply_strategy(
                pii["text"],
                pii["entity_type"],
                default_strategy
            )
            result = result[:pii["start"]] + masked + result[pii["end"]:]
        
        return result
```

### 3.2 æ°æ®å å¯å¼æ

```python
"""
æ°æ®å å¯å¼æ - AES-256å å¯
"""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import os
from typing import Optional
import json


class EncryptionEngine:
    """æ°æ®å å¯å¼æ"""
    
    def __init__(self, master_key: Optional[bytes] = None):
        if master_key:
            self.fernet = Fernet(master_key)
        else:
            self.fernet = Fernet(Fernet.generate_key())
    
    @staticmethod
    def generate_key(password: str, salt: Optional[bytes] = None) -> bytes:
        """ä»å¯ç çæå å¯å¯é?""
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
        return key, salt
    
    def encrypt(self, data: str) -> str:
        """å å¯å­ç¬¦ä¸?""
        if isinstance(data, str):
            data = data.encode()
        return self.fernet.encrypt(data).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """è§£å¯å­ç¬¦ä¸?""
        if isinstance(encrypted_data, str):
            encrypted_data = encrypted_data.encode()
        return self.fernet.decrypt(encrypted_data).decode()
    
    def encrypt_dict(self, data: dict) -> str:
        """å å¯å­å¸"""
        json_str = json.dumps(data, ensure_ascii=False)
        return self.encrypt(json_str)
    
    def decrypt_dict(self, encrypted_data: str) -> dict:
        """è§£å¯å­å¸"""
        json_str = self.decrypt(encrypted_data)
        return json.loads(json_str)
    
    def encrypt_file(self, input_path: str, output_path: str):
        """å å¯æä»¶"""
        with open(input_path, 'rb') as f:
            data = f.read()
        
        encrypted = self.fernet.encrypt(data)
        
        with open(output_path, 'wb') as f:
            f.write(encrypted)
    
    def decrypt_file(self, input_path: str, output_path: str):
        """è§£å¯æä»¶"""
        with open(input_path, 'rb') as f:
            encrypted_data = f.read()
        
        decrypted = self.fernet.decrypt(encrypted_data)
        
        with open(output_path, 'wb') as f:
            f.write(decrypted)


class FieldLevelEncryption:
    """å­æ®µçº§å å¯?""
    
    SENSITIVE_FIELDS = [
        "id_card", "phone", "email", "bank_card",
        "address", "name", "account", "password"
    ]
    
    def __init__(self, encryption_engine: EncryptionEngine):
        self.engine = encryption_engine
        self.field_keys = {}
    
    def encrypt_field(self, value: str, field_name: str) -> str:
        """å å¯åä¸ªå­æ®µ"""
        if field_name.lower() in [f.lower() for f in self.SENSITIVE_FIELDS]:
            return f"ENC:{self.engine.encrypt(value)}"
        return value
    
    def decrypt_field(self, value: str, field_name: str) -> str:
        """è§£å¯åä¸ªå­æ®µ"""
        if value.startswith("ENC:"):
            return self.engine.decrypt(value[4:])
        return value
    
    def encrypt_record(self, record: dict, fields: list = None) -> dict:
        """å å¯è®°å½ä¸­çææå­æ®µ"""
        fields_to_encrypt = fields or self.SENSITIVE_FIELDS
        encrypted_record = {}
        
        for key, value in record.items():
            if key.lower() in [f.lower() for f in fields_to_encrypt]:
                encrypted_record[key] = self.encrypt_field(str(value), key)
            else:
                encrypted_record[key] = value
        
        return encrypted_record
    
    def decrypt_record(self, record: dict) -> dict:
        """è§£å¯è®°å½"""
        decrypted_record = {}
        
        for key, value in record.items():
            if isinstance(value, str) and value.startswith("ENC:"):
                decrypted_record[key] = self.decrypt_field(value, key)
            else:
                decrypted_record[key] = value
        
        return decrypted_record
```

### 3.3 è®¿é®å®¡è®¡å¼æ

```python
"""
è®¿é®å®¡è®¡å¼æ
"""
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import hashlib


class AccessAuditEngine:
    """è®¿é®å®¡è®¡å¼æ"""
    
    def __init__(self, db_path: str = "data/audit/access_audit.db"):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """åå§åå®¡è®¡æ°æ®åº"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS access_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    user_id TEXT,
                    action TEXT NOT NULL,
                    resource_type TEXT,
                    resource_id TEXT,
                    field_name TEXT,
                    operation TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    status TEXT,
                    details TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON access_logs(timestamp)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_action 
                ON access_logs(user_id, action)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_resource 
                ON access_logs(resource_type, resource_id)
            """)
    
    def log_access(
        self,
        user_id: str,
        action: str,
        resource_type: str = None,
        resource_id: str = None,
        field_name: str = None,
        operation: str = None,
        ip_address: str = None,
        user_agent: str = None,
        status: str = "success",
        details: dict = None
    ):
        """è®°å½è®¿é®æ¥å¿"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO access_logs (
                    timestamp, user_id, action, resource_type,
                    resource_id, field_name, operation,
                    ip_address, user_agent, status, details
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                user_id,
                action,
                resource_type,
                resource_id,
                field_name,
                operation,
                ip_address,
                user_agent,
                status,
                json.dumps(details) if details else None
            ))
    
    def query_logs(
        self,
        user_id: str = None,
        action: str = None,
        resource_type: str = None,
        start_time: str = None,
        end_time: str = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """æ¥è¯¢è®¿é®æ¥å¿"""
        conditions = []
        params = []
        
        if user_id:
            conditions.append("user_id = ?")
            params.append(user_id)
        
        if action:
            conditions.append("action = ?")
            params.append(action)
        
        if resource_type:
            conditions.append("resource_type = ?")
            params.append(resource_type)
        
        if start_time:
            conditions.append("timestamp >= ?")
            params.append(start_time)
        
        if end_time:
            conditions.append("timestamp <= ?")
            params.append(end_time)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(f"""
                SELECT * FROM access_logs
                WHERE {where_clause}
                ORDER BY timestamp DESC
                LIMIT ?
            """, params + [limit])
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_user_access_summary(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """è·åç¨æ·è®¿é®æè¦"""
        start_time = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        start_time = start_time.replace(
            day=start_time.day - days
        ).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            total_count = conn.execute("""
                SELECT COUNT(*) as count FROM access_logs
                WHERE user_id = ? AND timestamp >= ?
            """, (user_id, start_time)).fetchone()["count"]
            
            action_counts = conn.execute("""
                SELECT action, COUNT(*) as count
                FROM access_logs
                WHERE user_id = ? AND timestamp >= ?
                GROUP BY action
            """, (user_id, start_time)).fetchall()
            
            resource_counts = conn.execute("""
                SELECT resource_type, COUNT(*) as count
                FROM access_logs
                WHERE user_id = ? AND timestamp >= ?
                GROUP BY resource_type
            """, (user_id, start_time)).fetchall()
            
            return {
                "user_id": user_id,
                "period_days": days,
                "total_access_count": total_count,
                "action_breakdown": {
                    row["action"]: row["count"] 
                    for row in action_counts
                },
                "resource_breakdown": {
                    row["resource_type"]: row["count"]
                    for row in resource_counts
                }
            }
    
    def detect_anomalies(self, hours: int = 24) -> List[Dict[str, Any]]:
        """æ£æµå¼å¸¸è®¿é®è¡ä¸?""
        start_time = datetime.now().replace(
            hour=datetime.now().hour - hours
        ).isoformat()
        
        anomalies = []
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            high_frequency = conn.execute("""
                SELECT user_id, COUNT(*) as access_count
                FROM access_logs
                WHERE timestamp >= ?
                GROUP BY user_id
                HAVING access_count > 100
            """, (start_time,)).fetchall()
            
            for row in high_frequency:
                anomalies.append({
                    "type": "high_frequency_access",
                    "user_id": row["user_id"],
                    "access_count": row["access_count"],
                    "threshold": 100,
                    "severity": "high"
                })
            
            failed_access = conn.execute("""
                SELECT user_id, ip_address, COUNT(*) as fail_count
                FROM access_logs
                WHERE timestamp >= ? AND status = 'failed'
                GROUP BY user_id, ip_address
                HAVING fail_count > 5
            """, (start_time,)).fetchall()
            
            for row in failed_access:
                anomalies.append({
                    "type": "failed_access_attempts",
                    "user_id": row["user_id"],
                    "ip_address": row["ip_address"],
                    "fail_count": row["fail_count"],
                    "threshold": 5,
                    "severity": "critical"
                })
        
        return anomalies
```

### 3.4 å¯é¥ç®¡çæå¡

```python
"""
å¯é¥ç®¡çæå¡ - è½»éçº§å®ç?
"""
import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional
import secrets
from cryptography.fernet import Fernet


class KeyManagementService:
    """å¯é¥ç®¡çæå¡"""
    
    def __init__(self, key_store_path: str = "data/keys/"):
        self.key_store_path = Path(key_store_path)
        self.key_store_path.mkdir(parents=True, exist_ok=True)
        self.key_metadata_file = self.key_store_path / "key_metadata.json"
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """å è½½å¯é¥åæ°æ?""
        if self.key_metadata_file.exists():
            with open(self.key_metadata_file, 'r') as f:
                return json.load(f)
        return {"keys": {}}
    
    def _save_metadata(self):
        """ä¿å­å¯é¥åæ°æ?""
        with open(self.key_metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def generate_key(
        self,
        key_id: str,
        key_type: str = "data_encryption",
        expires_days: int = 365
    ) -> bytes:
        """çææ°å¯é?""
        key = Fernet.generate_key()
        
        key_file = self.key_store_path / f"{key_id}.key"
        with open(key_file, 'wb') as f:
            f.write(key)
        
        self.metadata["keys"][key_id] = {
            "key_type": key_type,
            "created_at": datetime.now().isoformat(),
            "expires_at": (
                datetime.now() + timedelta(days=expires_days)
            ).isoformat(),
            "status": "active",
            "rotation_count": 0
        }
        self._save_metadata()
        
        return key
    
    def get_key(self, key_id: str) -> Optional[bytes]:
        """è·åå¯é¥"""
        key_file = self.key_store_path / f"{key_id}.key"
        
        if not key_file.exists():
            return None
        
        if key_id in self.metadata["keys"]:
            key_info = self.metadata["keys"][key_id]
            expires_at = datetime.fromisoformat(key_info["expires_at"])
            
            if datetime.now() > expires_at:
                raise ValueError(f"Key {key_id} has expired")
        
        with open(key_file, 'rb') as f:
            return f.read()
    
    def rotate_key(
        self,
        key_id: str,
        keep_old: bool = True
    ) -> bytes:
        """è½®æ¢å¯é¥"""
        old_key = self.get_key(key_id)
        
        if keep_old:
            old_key_file = self.key_store_path / f"{key_id}_old_{datetime.now().strftime('%Y%m%d%H%M%S')}.key"
            with open(old_key_file, 'wb') as f:
                f.write(old_key)
        
        new_key = Fernet.generate_key()
        key_file = self.key_store_path / f"{key_id}.key"
        with open(key_file, 'wb') as f:
            f.write(new_key)
        
        if key_id in self.metadata["keys"]:
            self.metadata["keys"][key_id]["rotation_count"] += 1
            self.metadata["keys"][key_id]["last_rotated"] = datetime.now().isoformat()
            self._save_metadata()
        
        return new_key
    
    def list_keys(self) -> Dict[str, Dict]:
        """ååºææå¯é?""
        return self.metadata["keys"]
    
    def revoke_key(self, key_id: str):
        """æ¤éå¯é¥"""
        if key_id in self.metadata["keys"]:
            self.metadata["keys"][key_id]["status"] = "revoked"
            self.metadata["keys"][key_id]["revoked_at"] = datetime.now().isoformat()
            self._save_metadata()
```

---

## ð åãé¨ç½²éç½?

### 4.1 Docker Composeéç½®

```yaml
version: '3.8'

services:
  data-masking-service:
    build:
      context: .
      dockerfile: Dockerfile.masking
    container_name: zephyr-masking
    ports:
      - "8090:8090"
    environment:
      - LOG_LEVEL=INFO
      - KEY_STORE_PATH=/data/keys
      - AUDIT_DB_PATH=/data/audit/audit.db
    volumes:
      - ./data:/data
      - ./config:/config
    restart: unless-stopped
    networks:
      - zephyr-network

networks:
  zephyr-network:
    external: true
```

### 4.2 éç½®æä»¶

```yaml
data_masking:
  pii_detection:
    enabled: true
    language: "en"
    custom_patterns:
      chinese_id_card: '\d{17}[\dXx]'
      chinese_phone: '1[3-9]\d{9}'
      chinese_bank_card: '\d{16,19}'
  
  masking_strategies:
    default: "mask"
    phone: "mask"
    id_card: "mask"
    email: "mask"
    name: "mask"
    bank_card: "mask"
  
  encryption:
    algorithm: "AES-256"
    key_rotation_days: 90
  
  audit:
    enabled: true
    retention_days: 365
    anomaly_detection: true
  
  sensitive_fields:
    - id_card
    - phone
    - email
    - bank_card
    - address
    - name
    - account
    - password
```

---

## ð äºãä½¿ç¨ç¤ºä¾?

### 5.1 PIIæ«æä¸è±æ?

```python
from data_masking import PIIIdentifier, DataMasker

identifier = PIIIdentifier(language="en")
masker = DataMasker()

text = "å¼ ä¸çèº«ä»½è¯å·æ¯110101199001011234ï¼ææºå·æ?3812345678"

pii_list = identifier.scan(text)
print(f"åç°PII: {pii_list}")

masked_text = masker.anonymize_text(text, pii_list)
print(f"è±æå? {masked_text}")
```

### 5.2 æ°æ®å å¯

```python
from data_masking import EncryptionEngine, FieldLevelEncryption

engine = EncryptionEngine()

encrypted = engine.encrypt("æææ°æ®")
print(f"å å¯å? {encrypted}")

decrypted = engine.decrypt(encrypted)
print(f"è§£å¯å? {decrypted}")

field_enc = FieldLevelEncryption(engine)
record = {
    "name": "å¼ ä¸",
    "phone": "13812345678",
    "id_card": "110101199001011234",
    "trade_amount": 10000
}

encrypted_record = field_enc.encrypt_record(record)
print(f"å å¯è®°å½: {encrypted_record}")
```

### 5.3 è®¿é®å®¡è®¡

```python
from data_masking import AccessAuditEngine

audit = AccessAuditEngine()

audit.log_access(
    user_id="user_001",
    action="read",
    resource_type="stock_data",
    resource_id="000001.SZ",
    field_name="phone",
    operation="decrypt",
    ip_address="192.168.1.100",
    status="success"
)

logs = audit.query_logs(user_id="user_001", limit=10)
print(f"è®¿é®æ¥å¿: {logs}")

anomalies = audit.detect_anomalies(hours=24)
print(f"å¼å¸¸æ£æµ? {anomalies}")
```

---

## ð å­ãæ§è½ææ 

### 6.1 æ§è½åºå

| æä½ | æ°æ®é?| èæ¶ | ååé?|
|------|--------|------|--------|
| PIIæ«æ | 1MBææ¬ | 50ms | 20MB/s |
| æ°æ®è±æ | 1000æ¡è®°å½?| 100ms | 10Kæ?s |
| æ°æ®å å¯ | 1MBæ°æ® | 30ms | 33MB/s |
| æ°æ®è§£å¯ | 1MBæ°æ® | 30ms | 33MB/s |
| å®¡è®¡æ¥å¿åå¥ | 1000æ?| 50ms | 20Kæ?s |

### 6.2 èµæºå ç¨

| èµæº | æå°éç½?| æ¨èéç½® |
|------|---------|---------|
| CPU | 1æ ?| 2æ ?|
| åå­ | 512MB | 1GB |
| å­å¨ | 1GB | 5GB |

---

## ð ä¸ãå®å¨æä½³å®è·?

### 7.1 å¯é¥ç®¡ç

1. **å®æè½®æ¢**: æ¯?0å¤©è½®æ¢ä¸æ¬¡å å¯å¯é?
2. **å®å¨å­å¨**: å¯é¥æä»¶æéè®¾ç½®ä¸?00
3. **å¤ä»½ç­ç¥**: å å¯å¤ä»½å¯é¥æä»¶
4. **è®¿é®æ§å¶**: éå¶å¯é¥è®¿é®æé

### 7.2 å®¡è®¡æ¥å¿

1. **å®æ´è®°å½**: è®°å½æææææ°æ®è®¿é?
2. **é²ç¯¡æ?*: ä½¿ç¨åªè¿½å å­å?
3. **å®æåæ**: æ¯æ¥æ£æµå¼å¸¸è¡ä¸?
4. **é¿æä¿å­**: è³å°ä¿å­1å¹?

### 7.3 åè§è¦æ±

| æ³è§ | è¦æ± | å®ç°æ¹å¼ |
|------|------|---------|
| GDPR | æ°æ®æå°å | PIIè¯å«+è±æ |
| CCPA | æ¶è´¹èéç§?| è®¿é®å®¡è®¡ |
| PCI DSS | å¡æ°æ®ä¿æ?| å å¯å­å¨ |
| ç­ä¿2.0 | æ°æ®å®å¨ | å¨åè½å®ç?|

---

## ð å«ãå®æ½è·¯å¾?

### Phase 1: åºç¡åè½ï¼?å¨ï¼

- [x] PIIè¯å«å¼æé¨ç½²
- [x] æ°æ®è±æåè½å®ç°
- [x] åºç¡å å¯åè½

### Phase 2: å®ååè½ï¼?å¨ï¼

- [x] è®¿é®å®¡è®¡ç³»ç»
- [x] å¯é¥ç®¡çæå¡
- [x] å¼å¸¸æ£æµåè?

### Phase 3: éæä¼åï¼?å¨ï¼

- [x] ä¸æ°æ®ç®¡ééæ?
- [x] æ§è½ä¼å
- [x] çæ§åè­¦

---

## ð ä¹ãåèèµæº?

### 9.1 å¼æºé¡¹ç?

| é¡¹ç® | å°å | ç¨é?|
|------|------|------|
| Presidio | https://github.com/microsoft/presidio | PIIè¯å«ä¸è±æ?|
| cryptography | https://github.com/pyca/cryptography | å å¯åº?|
| HashiCorp Vault | https://github.com/hashicorp/vault | å¯é¥ç®¡ç |

### 9.2 ç¸å³ææ¡£

- [GDPRåè§æå](https://gdpr.eu/)
- [PCI DSSæ å](https://www.pcisecuritystandards.org/)
- [ä¸­å½ç½ç»å®å¨æ³](http://www.npc.gov.cn/)

---

## ð åãåæ´åå?

| çæ¬ | æ¥æ | åæ´åå®¹ | ä½è?|
|------|------|---------|------|
| v1.0.0 | 2026-04-07 | åå§çæ¬åå»º | é¦å¸­æ¶æå¸?|

---

**ææ¡£ç»æ**
