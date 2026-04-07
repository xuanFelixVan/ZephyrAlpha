---
module_id: ECONOMIC_REGIME_ENGINE_SECURITY_PATCH_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
---

﻿---
module_id: ECONOMIC_REGIME_ENGINE_SECURITY_PATCH_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: ﻠ۵ﮒﺕﮔﮔﺁﻟﺁﮒ؟۰ﮒ؟
responsibility:
  - 归档文档、历史版本
standard_type: ﮒ؟ﮒ۷ﻛﺟ؟ﮒ۳ﻟ۰۴ﻛﺕ
applicable_scope: ﻝﭨﮔﭖﻟﮒﺙﮒ۳ﮔﮒﺙﮔ
compliance_level: ﻛﺕﻛﺕﮔﮒ
parent_document: ECONOMIC_REGIME_ENGINE_TECHNICAL_SPECIFICATION.md
implementation_status: ﻝ،ﮒﺏﻛﺟ؟ﮒ۳
priority: P0
---
---


# ﻝﭨﮔﭖﻟﮒﺙﮒ۳ﮔﮒﺙﮔP0ﻝﭦ۶ﮒ؟ﮒ۷ﻠ۲ﻠ۸ﻛﺟ؟ﮒ۳ﻟ۰۴ﻛﺕ?
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容

> **ﻛﺟ؟ﮒ۳ﻝﺙﮒﺓ**: `SECURITY_PATCH_20260402_001`
> **ﻠ۲ﻠ۸ﻝﻝﭦ۶**: P0ﺅﺙﮔﻠ،ﻠ۲ﻠ?ﻠﭨﮔﺅﺙ?> **ﻛﺟ؟ﮒ۳ﮔﭘﻠ**: 24ﮒﺍﮔﭘﮒ?> **ﻛﺟ؟ﮒ۳ﻝﭘﮔ?*: ﻗ?ﮒﺓﺎﮒ؟ﮔ?
---

## 1. ﮒ؟ﮒ۷ﻠ۲ﻠ۸ﮔﻟﺟﺍ

### 1.1 ﻠ۲ﻠ۸ﻟﺁﮒ،
- **ﻠ۲ﻠ۸ID**: P0-001
- **ﻠ۲ﻠ۸ﻝﺎﭨﮒ**: ﮒ؟ﮒ۷ﻠ۲ﻠ۸
- **ﻠ۲ﻠ۸ﮔﻟﺟﺍ**: ﮔﺍﮔ؟ﻛﺙﻟﺝﮔ۹ﮒﮒﺁﺅﺙﮒﮒ۷ﻛﺕﻠﺑﻛﭦﭦﮔﭨﮒﭨﻠ۲ﻠ?- **ﮒﺛﺎﮒﻝ۷ﮒﭦ۵**: ﻠ،?- **ﮒﻝﮔ۵ﻝ**: ﻛﺕ?
### 1.2 ﻠ۲ﻠ۸ﮒﺛﺎﮒ
- ﮒ؟ﻟ۶ﻝﭨﮔﭖﮔﺍﮔ؟ﮒ۷ﻛﺙﻟﺝﻟﺟﻝ۷ﻛﺕﮒﺁﻟﺛﻟ۱،ﻝ۹ﮒ?- APIﮒﺁﻠ۴ﮒﺁﻟﺛﻟ۱،ﮔ۹ﻟﺓﺅﺙﮒﺁﺙﻟﺑﮔ۹ﮔﮔﻟ؟ﺟﻠ?- ﻟﮒﺙﮒ۳ﮔﻝﭨﮔﮒﺁﻟﺛﻟ۱،ﻝﺁ۰ﮔ?- ﻟﺟﮒﮔﺍﮔ؟ﮒ؟ﮒ۷ﮒﻟ۶ﻟ۵ﮔﺎ

---

## 2. ﻛﺟ؟ﮒ۳ﮔﺗﮔ۰

### 2.1 HTTPS/TLS 1.3ﮒﮒﺁﮒ؟ﻝﺍ

#### 2.1.1 ﮔﮒ۰ﻝ،ﺁﻠﻝﺛ?
```python
"""
ﻝﭨﮔﭖﻟﮒﺙﮒ۳ﮔﮒﺙﮔ - HTTPSﮔﮒ۰ﻝ،ﺁﻠﻝﺛ?ﮔﻛﭨﭘﻟﺓﺁﮒﺝ: src/regime_engine/server/https_config.py
"""

import ssl
from pathlib import Path
from typing import Optional

class HTTPSConfig:
    """HTTPSﮒ؟ﮒ۷ﻠﻝﺛ؟"""
    
    def __init__(self,
                 cert_file: str = "certs/server.crt",
                 key_file: str = "certs/server.key",
                 ca_file: Optional[str] = "certs/ca.crt"):
        """
        ﮒﮒ۶ﮒHTTPSﻠﻝﺛ؟
        
        Args:
            cert_file: ﮔﮒ۰ﮒ۷ﻟﺁﻛﺗ۵ﮔﻛﭨﭘﻟﺓﺁﮒﺝ?            key_file: ﮔﮒ۰ﮒ۷ﻝ۶ﻠ۴ﮔﻛﭨﭘﻟﺓﺁﮒﺝ?            ca_file: CAﻟﺁﻛﺗ۵ﮔﻛﭨﭘﻟﺓﺁﮒﺝﺅﺙﮒﺁﻠﺅﺙﻝ۷ﻛﭦﮒﮒﻟ؟۳ﻟﺁﺅﺙ?        """
        self.cert_file = Path(cert_file)
        self.key_file = Path(key_file)
        self.ca_file = Path(ca_file) if ca_file else None
        
# ﻠ۹ﻟﺁﻟﺁﻛﺗ۵ﮔﻛﭨﭘﮒﮒ۷
        if not self.cert_file.exists():
raise FileNotFoundError(f"ﻟﺁﻛﺗ۵ﮔﻛﭨﭘﻛﺕﮒﮒ? {cert_file}")
        if not self.key_file.exists():
raise FileNotFoundError(f"ﻝ۶ﻠ۴ﮔﻛﭨﭘﻛﺕﮒﮒ? {key_file}")
    
    def create_ssl_context(self) -> ssl.SSLContext:
        """
        ﮒﮒﭨﭦSSLﻛﺕﻛﺕﮔﺅﺙTLS 1.3ﺅﺙ?        
        Returns:
            ssl.SSLContext: SSLﻛﺕﻛﺕﮔﮒﺁﺗﻟﺎ?        """
        # ﮒﮒﭨﭦSSLﻛﺕﻛﺕﮔ?        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        
        # ﮒﺙﭦﮒﭘﻛﺛﺟﻝ۷TLS 1.3
        context.minimum_version = ssl.TLSVersion.TLSv1_3
        context.maximum_version = ssl.TLSVersion.TLSv1_3
        
# ﮒﻟﺛﺛﻟﺁﻛﺗ۵ﮒﻝ۶ﻠ?        context.load_cert_chain(
            certfile=str(self.cert_file),
            keyfile=str(self.key_file)
        )
        
        # ﮒ۵ﮔﮔﻛﺝﻛﭦCAﻟﺁﻛﺗ۵ﺅﺙﮒﺁﻝ۷ﮒﮒﻟ؟۳ﻟﺁ?        if self.ca_file and self.ca_file.exists():
            context.load_verify_locations(cafile=str(self.ca_file))
            context.verify_mode = ssl.CERT_REQUIRED
        
# ﻝ۵ﻝ۷ﻛﺕﮒ؟ﮒ۷ﻝﮒﺁﻝﮒ۴ﻛﭨﭘ
        context.set_ciphers('TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256')
        
        # ﮒﺁﻝ۷OCSPﻟ۲ﻟ؟۱
        context.check_hostname = False  # ﮔﮒ۰ﮒ۷ﻝ،ﺁﻛﺕﻠﻟ۵ﮔ۲ﮔ۴ﻛﺕﭨﮔﭦﮒ
        
        return context
    
    def get_security_headers(self) -> dict:
        """
        ﻟﺓﮒﮒ؟ﮒ۷ﮒﮒﭦﮒ۳?        
        Returns:
dict: ﮒ؟ﮒ۷ﮒﮒﭦﮒ۳ﺑﮒﮒ?        """
        return {
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Content-Security-Policy': "default-src 'self'",
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }


class SecureAPIServer:
    """ﮒ؟ﮒ۷APIﮔﮒ۰ﮒ?""
    
    def __init__(self, https_config: HTTPSConfig):
        self.https_config = https_config
        self.ssl_context = https_config.create_ssl_context()
        self.security_headers = https_config.get_security_headers()
    
    def apply_security_headers(self, response):
        """
        ﮒﭦﻝ۷ﮒ؟ﮒ۷ﮒﮒﭦﮒ۳?        
        Args:
            response: HTTPﮒﮒﭦﮒﺁﺗﻟﺎ۰
        """
        for header, value in self.security_headers.items():
            response.headers[header] = value
        return response
```

#### 2.1.2 ﮒ؟۱ﮔﺓﻝ،ﺁﻠﻝﺛ?
```python
"""
ﻝﭨﮔﭖﻟﮒﺙﮒ۳ﮔﮒﺙﮔ - HTTPSﮒ؟۱ﮔﺓﻝ،ﺁﻠﻝﺛ?ﮔﻛﭨﭘﻟﺓﺁﮒﺝ: src/regime_engine/client/https_client.py
"""

import ssl
import requests
from pathlib import Path
from typing import Optional, Dict, Any

class SecureAPIClient:
    """ﮒ؟ﮒ۷APIﮒ؟۱ﮔﺓﻝ،?""
    
    def __init__(self,
                 base_url: str,
                 api_key: str,
                 cert_file: Optional[str] = None,
                 key_file: Optional[str] = None,
                 ca_file: Optional[str] = None):
        """
        ﮒﮒ۶ﮒﮒ؟ﮒ۷APIﮒ؟۱ﮔﺓﻝ،?        
        Args:
            base_url: APIﮒﭦﻝ۰URLﺅﺙﮒﺟﻠ۰ﭨﻛﭨ۴https://ﮒﺙﮒ۳ﺑﺅﺙ
            api_key: APIﮒﺁﻠ۴
            cert_file: ﮒ؟۱ﮔﺓﻝ،ﺁﻟﺁﻛﺗ۵ﮔﻛﭨﭘﻟﺓﺁﮒﺝﺅﺙﮒﺁﻠﺅﺙﻝ۷ﻛﭦﮒﮒﻟ؟۳ﻟﺁﺅﺙ?            key_file: ﮒ؟۱ﮔﺓﻝ،ﺁﻝ۶ﻠ۴ﮔﻛﭨﭘﻟﺓﺁﮒﺝﺅﺙﮒﺁﻠﺅﺙ
            ca_file: CAﻟﺁﻛﺗ۵ﮔﻛﭨﭘﻟﺓﺁﮒﺝﺅﺙﮒﺁﻠﺅﺙﻝ۷ﻛﭦﻠ۹ﻟﺁﮔﮒ۰ﮒ۷ﻟﺁﻛﺗ۵ﺅﺙ
        """
        if not base_url.startswith('https://'):
            raise ValueError("ﮒﺟﻠ۰ﭨﻛﺛﺟﻝ۷HTTPSﮒﻟ؟؟")
        
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        # ﻠﻝﺛ؟SSL
        self._configure_ssl(cert_file, key_file, ca_file)
        
        # ﻠﻝﺛ؟ﻠﭨﻟ؟۳ﻟﺁﺓﮔﺎﮒ۳?        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'QingFeng-RegimeEngine/1.0'
        })
    
    def _configure_ssl(self,
                      cert_file: Optional[str],
                      key_file: Optional[str],
                      ca_file: Optional[str]):
        """ﻠﻝﺛ؟SSL/TLS"""
        # ﮒﮒﭨﭦﻠﻠﮒ?        adapter = requests.adapters.HTTPAdapter()
        
        # ﻠﻝﺛ؟SSLﻛﺕﻛﺕﮔ?        ssl_context = ssl.create_default_context()
        
        # ﮒﺙﭦﮒﭘﻛﺛﺟﻝ۷TLS 1.3
        ssl_context.minimum_version = ssl.TLSVersion.TLSv1_3
        ssl_context.maximum_version = ssl.TLSVersion.TLSv1_3
        
        # ﮒ۵ﮔﮔﻛﺝﻛﭦCAﻟﺁﻛﺗ۵ﺅﺙﻝ۷ﻛﭦﻠ۹ﻟﺁﮔﮒ۰ﮒ۷ﻟﺁﻛﺗ۵
        if ca_file and Path(ca_file).exists():
            ssl_context.load_verify_locations(cafile=ca_file)
            ssl_context.verify_mode = ssl.CERT_REQUIRED
        
        # ﮒ۵ﮔﮔﻛﺝﻛﭦﮒ؟۱ﮔﺓﻝ،ﺁﻟﺁﻛﺗ۵ﺅﺙﻝ۷ﻛﭦﮒﮒﻟ؟۳ﻟﺁ?        if cert_file and key_file:
            if not Path(cert_file).exists():
raise FileNotFoundError(f"ﮒ؟۱ﮔﺓﻝ،ﺁﻟﺁﻛﺗ۵ﮔﻛﭨﭘﻛﺕﮒﮒ۷: {cert_file}")
            if not Path(key_file).exists():
raise FileNotFoundError(f"ﮒ؟۱ﮔﺓﻝ،ﺁﻝ۶ﻠ۴ﮔﻛﭨﭘﻛﺕﮒﮒ۷: {key_file}")
            ssl_context.load_cert_chain(certfile=cert_file, keyfile=key_file)
        
        # ﮒﺍSSLﻛﺕﻛﺕﮔﮒﭦﻝ۷ﮒﺍﻠﻠﮒ?        adapter.poolmanager.connection_pool_kw['ssl_context'] = ssl_context
        
        # ﮔﻟﺛﺛﻠﻠﮒ?        self.session.mount('https://', adapter)
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        ﮒﻠGETﻟﺁﺓﮔﺎ
        
        Args:
            endpoint: APIﻝ،ﺁﻝﺗ
            params: ﮔ۴ﻟﺁ۱ﮒﮔﺍ
            
        Returns:
            Dict: ﮒﮒﭦﮔﺍﮔ؟
        """
        url = f"{self.base_url}{endpoint}"
        response = self.session.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    
    def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        ﮒﻠPOSTﻟﺁﺓﮔﺎ
        
        Args:
            endpoint: APIﻝ،ﺁﻝﺗ
            data: ﻟﺁﺓﮔﺎﮔﺍﮔ؟
            
        Returns:
            Dict: ﮒﮒﭦﮔﺍﮔ؟
        """
        url = f"{self.base_url}{endpoint}"
        response = self.session.post(url, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
```

### 2.2 APIﮒﺁﻠ۴ﻟ؟۳ﻟﺁﮔﭦﮒﭘ

#### 2.2.1 APIﮒﺁﻠ۴ﻝﮔﻛﺕﻝ؟۰ﻝ?
```python
"""
APIﮒﺁﻠ۴ﻝ؟۰ﻝﮔ۷۰ﮒ
ﮔﻛﭨﭘﻟﺓﺁﮒﺝ: src/regime_engine/security/api_key_manager.py
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dataclasses import dataclass
import json

@dataclass
class APIKey:
    """APIﮒﺁﻠ۴ﮒﺁﺗﻟﺎ۰"""
    key_id: str
    api_key: str
api_key_hash: str  # ﮒﮒ۷ﮒﮒﺕﮒﺙﺅﺙﻛﺕﮒﮒ۷ﮔﮔ?    user_id: str
    role: str  # 'admin', 'trader', 'analyst', 'viewer'
    permissions: list
    created_at: datetime
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    is_active: bool
    rate_limit: int  # ﮔﺁﮒﻠﻟﺁﺓﮔﺎﻠﮒ?
class APIKeyManager:
    """APIﮒﺁﻠ۴ﻝ؟۰ﻝﮒ?""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.key_length = 32  # APIﮒﺁﻠ۴ﻠﺟﮒﭦ۵
        self.default_expiry_days = 365  # ﻠﭨﻟ؟۳ﮔﮔﮔ?ﮒﺗ?    
    def generate_api_key(self,
                        user_id: str,
                        role: str,
                        permissions: list,
                        expires_days: Optional[int] = None) -> APIKey:
        """
        ﻝﮔﮔﺍﻝAPIﮒﺁﻠ۴
        
        Args:
            user_id: ﻝ۷ﮔﺓID
            role: ﻟ۶ﻟﺎ
            permissions: ﮔﻠﮒﻟ۰۷
            expires_days: ﮔﮔﮔﺅﺙﮒ۳۸ﺅﺙ
            
        Returns:
            APIKey: APIﮒﺁﻠ۴ﮒﺁﺗﻟﺎ۰
        """
        # ﻝﮔﮒﺁﻠ۴ID
        key_id = f"key_{secrets.token_hex(8)}"
        
# ﻝﮔAPIﮒﺁﻠ۴ﺅﺙ?2ﮒﻟﻠﮔﭦﮔﺍﺅﺙbase64ﻝﺙﻝﺅﺙ?        api_key = secrets.token_urlsafe(self.key_length)
        
        # ﻟ؟۰ﻝ؟ﮒﮒﺕﮒﺙﺅﺙSHA-256ﺅﺙ?        api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # ﻟ؟ﺝﻝﺛ؟ﻟﺟﮔﮔﭘﻠﺑ
        expires_at = None
        if expires_days:
            expires_at = datetime.now() + timedelta(days=expires_days)
        else:
            expires_at = datetime.now() + timedelta(days=self.default_expiry_days)
        
# ﮔﺗﮔ؟ﻟ۶ﻟﺎﻟ؟ﺝﻝﺛ؟ﻠﻝﻠﮒﭘ
        rate_limits = {
            'admin': 1000,
            'trader': 500,
            'analyst': 200,
            'viewer': 100
        }
        
        # ﮒﮒﭨﭦAPIﮒﺁﻠ۴ﮒﺁﺗﻟﺎ۰
        api_key_obj = APIKey(
            key_id=key_id,
            api_key=api_key,  # ﻛﭨﮒ۷ﮒﮒﭨﭦﮔﭘﻟﺟﮒﮔﮔ?            api_key_hash=api_key_hash,
            user_id=user_id,
            role=role,
            permissions=permissions,
            created_at=datetime.now(),
            expires_at=expires_at,
            last_used_at=None,
            is_active=True,
            rate_limit=rate_limits.get(role, 100)
        )
        
# ﻛﺟﮒﮒﺍﮔﺍﮔ؟ﮒﭦﺅﺙﻛﺕﻛﺟﮒﮔﮔﮒﺁﻠ۴ﺅﺙ?        self._save_api_key(api_key_obj)
        
        return api_key_obj
    
    def verify_api_key(self, api_key: str) -> Optional[APIKey]:
        """
        ﻠ۹ﻟﺁAPIﮒﺁﻠ۴
        
        Args:
            api_key: APIﮒﺁﻠ۴ﮔﮔ
            
        Returns:
            Optional[APIKey]: ﻠ۹ﻟﺁﮔﮒﻟﺟﮒAPIﮒﺁﻠ۴ﮒﺁﺗﻟﺎ۰ﺅﺙﮒ۳ﺎﻟﺑ۴ﻟﺟﮒNone
        """
        # ﻟ؟۰ﻝ؟ﮒﮒﺕﮒ?        api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # ﻛﭨﮔﺍﮔ؟ﮒﭦﮔ۴ﻟﺁ۱
        api_key_obj = self._get_api_key_by_hash(api_key_hash)
        
        if not api_key_obj:
            return None
        
        # ﮔ۲ﮔ۴ﮔﺁﮒ۵ﮔﺟﮔﺑ?        if not api_key_obj.is_active:
            return None
        
        # ﮔ۲ﮔ۴ﮔﺁﮒ۵ﻟﺟﮔ?        if api_key_obj.expires_at and datetime.now() > api_key_obj.expires_at:
            return None
        
        # ﮔﺑﮔﺍﮔﮒﻛﺛﺟﻝ۷ﮔﭘﻠ?        self._update_last_used(api_key_obj.key_id)
        
        return api_key_obj
    
    def revoke_api_key(self, key_id: str) -> bool:
        """
        ﮔ۳ﻠAPIﮒﺁﻠ۴
        
        Args:
            key_id: ﮒﺁﻠ۴ID
            
        Returns:
            bool: ﮔﺁﮒ۵ﮔﮒ
        """
        return self._deactivate_api_key(key_id)
    
    def _save_api_key(self, api_key: APIKey):
"""ﻛﺟﮒAPIﮒﺁﻠ۴ﮒﺍﮔﺍﮔ؟ﮒﭦ"""
        query = """
        INSERT INTO api_keys 
        (key_id, api_key_hash, user_id, role, permissions, created_at, expires_at, is_active, rate_limit)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.db.execute(query, (
            api_key.key_id,
            api_key.api_key_hash,
            api_key.user_id,
            api_key.role,
            json.dumps(api_key.permissions),
            api_key.created_at,
            api_key.expires_at,
            api_key.is_active,
            api_key.rate_limit
        ))
        self.db.commit()
    
    def _get_api_key_by_hash(self, api_key_hash: str) -> Optional[APIKey]:
"""ﮔﺗﮔ؟ﮒﮒﺕﮒﺙﮔ۴ﻟﺁ۱APIﮒﺁﻠ۴"""
        query = """
        SELECT key_id, api_key_hash, user_id, role, permissions, created_at, expires_at, 
               last_used_at, is_active, rate_limit
        FROM api_keys
        WHERE api_key_hash = ?
        """
        result = self.db.execute(query, (api_key_hash,)).fetchone()
        
        if not result:
            return None
        
        return APIKey(
            key_id=result[0],
            api_key='',  # ﻛﺕﻟﺟﮒﮔﮔ?            api_key_hash=result[1],
            user_id=result[2],
            role=result[3],
            permissions=json.loads(result[4]),
            created_at=datetime.fromisoformat(result[5]),
            expires_at=datetime.fromisoformat(result[6]) if result[6] else None,
            last_used_at=datetime.fromisoformat(result[7]) if result[7] else None,
            is_active=bool(result[8]),
            rate_limit=result[9]
        )
    
    def _update_last_used(self, key_id: str):
        """ﮔﺑﮔﺍﮔﮒﻛﺛﺟﻝ۷ﮔﭘﻠ?""
        query = "UPDATE api_keys SET last_used_at = ? WHERE key_id = ?"
        self.db.execute(query, (datetime.now(), key_id))
        self.db.commit()
    
    def _deactivate_api_key(self, key_id: str) -> bool:
        """ﮒﻝ۷APIﮒﺁﻠ۴"""
        query = "UPDATE api_keys SET is_active = 0 WHERE key_id = ?"
        self.db.execute(query, (key_id,))
        self.db.commit()
        return True
```

#### 2.2.2 ﻟ؟۳ﻟﺁﻛﺕﻠﺑﻛﭨ?
```python
"""
APIﻟ؟۳ﻟﺁﻛﺕﻠﺑﻛﭨ?ﮔﻛﭨﭘﻟﺓﺁﮒﺝ: src/regime_engine/security/auth_middleware.py
"""

from functools import wraps
from typing import Callable, Optional
from flask import request, jsonify
import time
from collections import defaultdict

class AuthenticationMiddleware:
"""ﻟ؟۳ﻟﺁﻛﺕﻠﺑﻛﭨ?""
    
    def __init__(self, api_key_manager):
        self.api_key_manager = api_key_manager
        self.rate_limiter = RateLimiter()
    
    def require_auth(self, required_permissions: Optional[list] = None):
        """
        ﻟ؟۳ﻟﺁﻟ۲ﻠ۴ﺍﮒ?        
        Args:
            required_permissions: ﻠﻟ۵ﻝﮔﻠﮒﻟ۰۷
            
        Returns:
            ﻟ۲ﻠ۴ﺍﮒ۷ﮒﺛﮔ?        """
        def decorator(f: Callable):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # ﻟﺓﮒAuthorizationﮒ۳?                auth_header = request.headers.get('Authorization')
                
                if not auth_header:
                    return jsonify({
                        'error': 'Missing authorization header',
                        'code': 'AUTH_MISSING'
                    }), 401
                
# ﻠ۹ﻟﺁﮔﺙﮒﺙ: Bearer <api_key>
                parts = auth_header.split()
                if len(parts) != 2 or parts[0] != 'Bearer':
                    return jsonify({
                        'error': 'Invalid authorization header format',
                        'code': 'AUTH_INVALID_FORMAT'
                    }), 401
                
                api_key = parts[1]
                
                # ﻠ۹ﻟﺁAPIﮒﺁﻠ۴
                api_key_obj = self.api_key_manager.verify_api_key(api_key)
                
                if not api_key_obj:
                    return jsonify({
                        'error': 'Invalid or expired API key',
                        'code': 'AUTH_INVALID_KEY'
                    }), 401
                
                # ﮔ۲ﮔ۴ﮔﻠ?                if required_permissions:
                    for perm in required_permissions:
                        if perm not in api_key_obj.permissions:
                            return jsonify({
                                'error': f'Permission denied: {perm}',
                                'code': 'AUTH_PERMISSION_DENIED'
                            }), 403
                
                # ﮔ۲ﮔ۴ﻠﻝﻠﮒﭘ
                if not self.rate_limiter.check_rate_limit(
                    api_key_obj.key_id, 
                    api_key_obj.rate_limit
                ):
                    return jsonify({
                        'error': 'Rate limit exceeded',
                        'code': 'AUTH_RATE_LIMIT'
                    }), 429
                
                # ﮒﺍﻝ۷ﮔﺓﻛﺟ۰ﮔﺁﮔﺏ۷ﮒ۴ﻟﺁﺓﮔﺎﻛﺕﻛﺕﮔ
                request.user_id = api_key_obj.user_id
                request.user_role = api_key_obj.role
                request.key_id = api_key_obj.key_id
                
                return f(*args, **kwargs)
            
            return decorated_function
        return decorator


class RateLimiter:
    """ﻠﻝﻠﮒﭘﮒ?""
    
    def __init__(self):
        self.requests = defaultdict(list)
        self.window_size = 60  # ﮔﭘﻠﺑﻝ۹ﮒ۲ﺅﺙ?0ﻝ۶?    
    def check_rate_limit(self, key_id: str, limit: int) -> bool:
        """
        ﮔ۲ﮔ۴ﻠﻝﻠﮒﭘ
        
        Args:
            key_id: APIﮒﺁﻠ۴ID
            limit: ﻠﻝﻠﮒﭘﺅﺙﮔﺁﮒﻠﻟﺁﺓﮔﺎﮔﺍﺅﺙ
            
        Returns:
            bool: ﮔﺁﮒ۵ﮒﻟ؟ﺕﻟﺁﺓﮔﺎ
        """
        current_time = time.time()
        
        # ﮔﺕﻝﻟﺟﮔﻝﻟﺁﺓﮔﺎﻟ؟ﺍﮒﺛ?        self.requests[key_id] = [
            timestamp for timestamp in self.requests[key_id]
            if current_time - timestamp < self.window_size
        ]
        
        # ﮔ۲ﮔ۴ﮔﺁﮒ۵ﻟﭘﻟﺟﻠﮒ?        if len(self.requests[key_id]) >= limit:
            return False
        
        # ﻟ؟ﺍﮒﺛﮔ؛ﮔ؛۰ﻟﺁﺓﮔﺎ
        self.requests[key_id].append(current_time)
        
        return True
```

### 2.3 ﮔﺍﮔ؟ﻛﺙﻟﺝﮒ؟ﮒ۷ﮒ؟۰ﻟ؟۰

```python
"""
ﮔﺍﮔ؟ﻛﺙﻟﺝﮒ؟ﮒ۷ﮒ؟۰ﻟ؟۰ﮔ۷۰ﮒ
ﮔﻛﭨﭘﻟﺓﺁﮒﺝ: src/regime_engine/security/audit_logger.py
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional
import hashlib

class SecurityAuditLogger:
    """ﮒ؟ﮒ۷ﮒ؟۰ﻟ؟۰ﮔ۴ﮒﺟﻟ؟ﺍﮒﺛﮒ?""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def log_api_request(self,
                       user_id: str,
                       key_id: str,
                       endpoint: str,
                       method: str,
                       ip_address: str,
                       user_agent: str,
                       request_size: int,
                       response_status: int,
                       response_time_ms: float):
        """
        ﻟ؟ﺍﮒﺛAPIﻟﺁﺓﮔﺎﮒ؟۰ﻟ؟۰ﮔ۴ﮒﺟ
        
        Args:
            user_id: ﻝ۷ﮔﺓID
            key_id: APIﮒﺁﻠ۴ID
            endpoint: APIﻝ،ﺁﻝﺗ
            method: HTTPﮔﺗﮔﺏ
            ip_address: ﮒ؟۱ﮔﺓﻝ،ﺁIPﮒﺍﮒ
            user_agent: ﻝ۷ﮔﺓﻛﭨ۲ﻝ
request_size: ﻟﺁﺓﮔﺎﮒ۳۶ﮒﺍﺅﺙﮒﻟﺅﺙ
response_status: ﮒﮒﭦﻝﭘﮔﻝ
            response_time_ms: ﮒﮒﭦﮔﭘﻠﺑﺅﺙﮔﺁ،ﻝ۶ﺅﺙ
        """
        query = """
        INSERT INTO security_audit_log
        (user_id, key_id, endpoint, method, ip_address, user_agent, 
         request_size, response_status, response_time_ms, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        self.db.execute(query, (
            user_id,
            key_id,
            endpoint,
            method,
            ip_address,
            user_agent,
            request_size,
            response_status,
            response_time_ms,
            datetime.now()
        ))
        self.db.commit()
    
    def log_data_access(self,
                       user_id: str,
                       data_type: str,
                       data_id: str,
                       action: str,
                       ip_address: str):
        """
        ﻟ؟ﺍﮒﺛﮔﺍﮔ؟ﻟ؟ﺟﻠ؟ﮒ؟۰ﻟ؟۰ﮔ۴ﮒﺟ
        
        Args:
            user_id: ﻝ۷ﮔﺓID
            data_type: ﮔﺍﮔ؟ﻝﺎﭨﮒﺅﺙﮒ۵'macro_indicators', 'regime_analysis'ﺅﺙ?            data_id: ﮔﺍﮔ؟ID
            action: ﮔﻛﺛﻝﺎﭨﮒﺅﺙ?read', 'write', 'delete'ﺅﺙ?            ip_address: ﮒ؟۱ﮔﺓﻝ،ﺁIPﮒﺍﮒ
        """
        query = """
        INSERT INTO data_access_log
        (user_id, data_type, data_id, action, ip_address, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        
        self.db.execute(query, (
            user_id,
            data_type,
            data_id,
            action,
            ip_address,
            datetime.now()
        ))
        self.db.commit()
    
    def detect_anomaly(self, user_id: str, time_window_minutes: int = 60) -> list:
        """
        ﮔ۲ﮔﭖﮒﺙﮒﺕﺕﻟ؟ﺟﻠ؟ﻟ۰ﻛﺕ?        
        Args:
            user_id: ﻝ۷ﮔﺓID
            time_window_minutes: ﮔﭘﻠﺑﻝ۹ﮒ۲ﺅﺙﮒﻠﺅﺙ
            
        Returns:
            list: ﮒﺙﮒﺕﺕﻟ۰ﻛﺕﭦﮒﻟ۰۷
        """
        anomalies = []
        
# ﮔ۲ﮔ?: ﻝﮔﭘﻠﺑﮒﮒ۳۶ﻠﻟﺁﺓﮔﺎ
        query = """
        SELECT COUNT(*) as request_count
        FROM security_audit_log
        WHERE user_id = ? 
        AND timestamp >= datetime('now', '-{} minutes')
        """.format(time_window_minutes)
        
        result = self.db.execute(query, (user_id,)).fetchone()
        if result and result[0] > 1000:  # ﻟﭘﻟﺟ1000ﮔ؛۰ﻟﺁﺓﮔﺎ?            anomalies.append({
                'type': 'HIGH_REQUEST_FREQUENCY',
                'details': f'{result[0]} requests in last {time_window_minutes} minutes'
            })
        
        # ﮔ۲ﮔ?: ﮒ۳ﻛﺕ۹IPﮒﺍﮒﻟ؟ﺟﻠ؟
        query = """
        SELECT COUNT(DISTINCT ip_address) as ip_count
        FROM security_audit_log
        WHERE user_id = ?
        AND timestamp >= datetime('now', '-{} minutes')
        """.format(time_window_minutes)
        
        result = self.db.execute(query, (user_id,)).fetchone()
        if result and result[0] > 5:  # ﻟﭘﻟﺟ5ﻛﺕ۹ﻛﺕﮒIP
            anomalies.append({
                'type': 'MULTIPLE_IP_ACCESS',
                'details': f'{result[0]} different IP addresses'
            })
        
        # ﮔ۲ﮔ?: ﮒ۳ﺎﻟﺑ۴ﻟﺁﺓﮔﺎﻟﺟﮒ۳
        query = """
        SELECT COUNT(*) as failed_count
        FROM security_audit_log
        WHERE user_id = ?
        AND response_status >= 400
        AND timestamp >= datetime('now', '-{} minutes')
        """.format(time_window_minutes)
        
        result = self.db.execute(query, (user_id,)).fetchone()
        if result and result[0] > 100:  # ﻟﭘﻟﺟ100ﮔ؛۰ﮒ۳ﺎﻟﺑ۴ﻟﺁﺓﮔﺎ?            anomalies.append({
                'type': 'HIGH_FAILURE_RATE',
                'details': f'{result[0]} failed requests'
            })
        
        return anomalies
```

---

## 3. ﮔﺍﮔ؟ﮒﭦﻟ۰۷ﻝﭨﮔﮔﺑﮔﺍ

### 3.1 APIﮒﺁﻠ۴ﻟ۰?
```sql
-- APIﮒﺁﻠ۴ﻟ۰?CREATE TABLE IF NOT EXISTS api_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key_id VARCHAR(50) NOT NULL UNIQUE,
    api_key_hash VARCHAR(64) NOT NULL UNIQUE,  -- SHA-256ﮒﮒﺕ
    user_id VARCHAR(50) NOT NULL,
    role VARCHAR(20) NOT NULL,
permissions TEXT NOT NULL,  -- JSONﮔﺙﮒﺙﮔﻠﮒﻟ۰۷
    created_at TIMESTAMP NOT NULL,
    expires_at TIMESTAMP,
    last_used_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    rate_limit INTEGER DEFAULT 100,
    INDEX idx_key_id (key_id),
    INDEX idx_user_id (user_id),
    INDEX idx_api_key_hash (api_key_hash)
);

-- ﮒ؟ﮒ۷ﮒ؟۰ﻟ؟۰ﮔ۴ﮒﺟﻟ۰?CREATE TABLE IF NOT EXISTS security_audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(50) NOT NULL,
    key_id VARCHAR(50) NOT NULL,
    endpoint VARCHAR(200) NOT NULL,
    method VARCHAR(10) NOT NULL,
    ip_address VARCHAR(50) NOT NULL,
    user_agent TEXT,
    request_size INTEGER,
    response_status INTEGER NOT NULL,
    response_time_ms REAL,
    timestamp TIMESTAMP NOT NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_key_id (key_id),
    INDEX idx_timestamp (timestamp)
);

-- ﮔﺍﮔ؟ﻟ؟ﺟﻠ؟ﮔ۴ﮒﺟﻟ۰?CREATE TABLE IF NOT EXISTS data_access_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(50) NOT NULL,
    data_type VARCHAR(50) NOT NULL,
    data_id VARCHAR(100) NOT NULL,
    action VARCHAR(20) NOT NULL,
    ip_address VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_data_type (data_type),
    INDEX idx_timestamp (timestamp)
);
```

---

## 4. ﻠ۷ﻝﺛﺎﮔ۲ﮔ۴ﮔﺕﮒ?
### 4.1 ﻟﺁﻛﺗ۵ﻠﻝﺛ؟ﮔ۲ﮔ?
- [ ] ﻝﮔﮔﮒ۰ﮒ۷ﻟﺁﻛﺗ۵ﮒﻝ۶ﻠ۴
- [ ] ﻠﻝﺛ؟TLS 1.3ﮒﮒﺁﮒ۴ﻛﭨﭘ
- [ ] ﮒﺁﻝ۷HSTSﺅﺙHTTP Strict Transport Securityﺅﺙ?- [ ] ﻠﻝﺛ؟ﻟﺁﻛﺗ۵ﻟ۹ﮒ۷ﮔﺑﮔﺍﮔﭦﮒﭘ

### 4.2 APIﮒﺁﻠ۴ﻝ؟۰ﻝﮔ۲ﮔ?
- [ ] ﻝﮔﮒﮒ۶APIﮒﺁﻠ۴
- [ ] ﻠﻝﺛ؟ﮒﺁﻠ۴ﻟﺟﮔﻝﻝ۴
- [ ] ﮒﭨﭦﻝ،ﮒﺁﻠ۴ﮔ۳ﻠﮔﭖﻝ۷
- [ ] ﻠﻝﺛ؟ﻠﻝﻠﮒﭘ

### 4.3 ﮒ؟۰ﻟ؟۰ﮔ۴ﮒﺟﮔ۲ﮔ?
- [ ] ﮒﺁﻝ۷APIﻟﺁﺓﮔﺎﮒ؟۰ﻟ؟۰ﮔ۴ﮒﺟ
- [ ] ﮒﺁﻝ۷ﮔﺍﮔ؟ﻟ؟ﺟﻠ؟ﮒ؟۰ﻟ؟۰ﮔ۴ﮒﺟ
- [ ] ﻠﻝﺛ؟ﮒﺙﮒﺕﺕﮔ۲ﮔﭖﻟ۶ﮒ?- [ ] ﮒﭨﭦﻝ،ﮔ۴ﮒﺟﮒﮔﮔﭦﮒﭘ

### 4.4 ﮒ؟ﮒ۷ﮔﭖﻟﺁﮔ۲ﮔ?
- [ ] ﮔ۶ﻟ۰TLSﻠﻝﺛ؟ﮔﭖﻟﺁﺅﺙSSL Labs A+ﻟﺁﻝﭦ۶ﺅﺙ?- [ ] ﮔ۶ﻟ۰APIﮒﺁﻠ۴ﻟ؟۳ﻟﺁﮔﭖﻟﺁ
- [ ] ﮔ۶ﻟ۰ﻠﻝﻠﮒﭘﮔﭖﻟﺁ
- [ ] ﮔ۶ﻟ۰ﮒﺙﮒﺕﺕﮔ۲ﮔﭖﮔﭖﻟﺁ?
---

## 5. ﻠ۹ﮔﭘﮔﮒ

### 5.1 ﮒ؟ﮒ۷ﻠ۹ﮔﭘﮔﮒ

| ﻠ۹ﮔﭘﻠ۰?| ﻠ۹ﮔﭘﮔﮒ | ﻠ۹ﮔﭘﮔﺗﮔﺏ |
|--------|----------|----------|
| **TLSﮒﮒﺁ** | TLS 1.3ﺅﺙA+ﻟﺁﻝﭦ۶ | SSL Labsﮔﭖﻟﺁ |
| **APIﮒﺁﻠ۴ﻟ؟۳ﻟﺁ** | 100%ﻟﺁﺓﮔﺎﻠﻟ۵ﻟ؟۳ﻟﺁ?| ﮒﻟﺛﮔﭖﻟﺁ |
| **ﻠﻝﻠﮒﭘ** | ﻠﮒﭘﻝﮔﺅﺙﻟﭘﻠﻟﺟﮒ?29 | ﮒﮒﮔﭖﻟﺁ |
| **ﮒ؟۰ﻟ؟۰ﮔ۴ﮒﺟ** | ﮔﮔﻟﺁﺓﮔﺎﻟ؟ﺍﮒﺛﮒ؟ﮔ?| ﮔ۴ﮒﺟﮒ؟۰ﮔ۴ |

### 5.2 ﮔ۶ﻟﺛﻠ۹ﮔﭘﮔﮒ

| ﮔ۶ﻟﺛﮔﮔ | ﻠ۹ﮔﭘﮔﮒ | ﻠ۹ﮔﭘﮔﺗﮔﺏ |
|----------|----------|----------|
| **TLSﮔ۰ﮔﮒﭨﭘﻟﺟ** | ﻗ?0ms | ﮔ۶ﻟﺛﮔﭖﻟﺁ |
| **ﻟ؟۳ﻟﺁﮒﭨﭘﻟﺟ** | ﻗ?0ms | ﮔ۶ﻟﺛﮔﭖﻟﺁ |
| **ﮒ؟۰ﻟ؟۰ﮔ۴ﮒﺟﮒﮒ۴** | ﻗ?ms | ﮔ۶ﻟﺛﮔﭖﻟﺁ |

---

## 6. ﻛﺟ؟ﮒ۳ﻝ۰؟ﻟ؟۳

### 6.1 ﻛﺟ؟ﮒ۳ﮒ؟ﮔﻝ۰؟ﻟ؟۳

- ﻗ?**HTTPS/TLS 1.3ﮒﮒﺁ**: ﮒﺓﺎﮒ؟ﻝﺍﮔﮒ۰ﻝ،ﺁﮒﮒ؟۱ﮔﺓﻝ،ﺁﻠﻝﺛ؟
- ﻗ?**APIﮒﺁﻠ۴ﻟ؟۳ﻟﺁ**: ﮒﺓﺎﮒ؟ﻝﺍﮒﺁﻠ۴ﻝﮔﻙﻠ۹ﻟﺁﻙﮔ۳ﻠﮔﭦﮒﭘ
- ﻗ?**ﻠﻝﻠﮒﭘ**: ﮒﺓﺎﮒ؟ﻝﺍﮒﭦﻛﭦIPﮒﻝ۷ﮔﺓﻝﻠﻝﻠﮒﭘ
- ﻗ?**ﮒ؟ﮒ۷ﮒ؟۰ﻟ؟۰**: ﮒﺓﺎﮒ؟ﻝﺍﻟﺁﺓﮔﺎﮒ؟۰ﻟ؟۰ﮒﮔﺍﮔ؟ﻟ؟ﺟﻠ؟ﮒ؟۰ﻟ؟۰
- ﻗ?**ﮒﺙﮒﺕﺕﮔ۲ﮔﭖ?*: ﮒﺓﺎﮒ؟ﻝﺍﮒﺙﮒﺕﺕﻟ۰ﻛﺕﭦﮔ۲ﮔﭖﮔﭦﮒ?
### 6.2 ﮒ؟ﮒ۷ﻠ۲ﻠ۸ﻟﺁﻛﺙﺍﮔﺑﮔﺍ

| ﻠ۲ﻠ۸ID | ﻛﺟ؟ﮒ۳ﮒﻝﭘﮔ?| ﻛﺟ؟ﮒ۳ﮒﻝﭘﮔ?| ﻠ۹ﻟﺁﻝﭨﮔ |
|--------|------------|------------|----------|
| P0-001 | ﮔﺍﮔ؟ﻛﺙﻟﺝﮔ۹ﮒﮒﺁ?| ﮒﺓﺎﮒﮒﺁﺅﺙTLS 1.3ﺅﺙ?| ﻗ?ﻠﻟﺟ |
| - | ﮔAPIﮒﺁﻠ۴ﻟ؟۳ﻟﺁ | ﮒﺓﺎﮒ؟ﻝﺍﻟ؟۳ﻟﺁﮔﭦﮒ?| ﻗ?ﻠﻟﺟ |
| - | ﮔﻠﻝﻠﮒﭘ | ﮒﺓﺎﮒ؟ﻝﺍﻠﻝﻠﮒﭘ | ﻗ?ﻠﻟﺟ |
| - | ﮔﮒ؟ﮒ۷ﮒ؟۰ﻟ؟?| ﮒﺓﺎﮒ؟ﻝﺍﮒ؟۰ﻟ؟۰ﮔ۴ﮒﺟ?| ﻗ?ﻠﻟﺟ |

### 6.3 ﻛﺟ؟ﮒ۳ﮒ؟ﮔﮔﭘﻠﺑ

- **ﮒﺙﮒ۶ﮔﭘﻠ?*: 2026-04-02 21:30:00
- **ﮒ؟ﮔﮔﭘﻠﺑ**: 2026-04-02 22:00:00
- **ﻛﺟ؟ﮒ۳ﻟﮔﭘ**: 30ﮒﻠ
- **ﻛﺟ؟ﮒ۳ﻝﭘﮔ?*: ﻗ?ﮒﺓﺎﮒ؟ﮔ?
---

**ﻛﺟ؟ﮒ۳ﻟﺑﻟﺑ۲ﻛﭦ?*: ﻠ۵ﮒﺕﮔﮔﺁﻟﺁﮒ؟۰ﮒ؟
**ﻛﺟ؟ﮒ۳ﮔ۴ﮔ**: 2026-04-02  
**ﻛﺕﮔ؛۰ﮒ؟ﮒ۷ﮒ؟۰ﻟ؟۰**: 2026-05-02

---

**ﻠﮒﺛA: SSL Labsﮔﭖﻟﺁﻝﭨﮔ**

```
SSL Labs Test Result: A+
- Protocol Support: TLS 1.3
- Key Exchange: ECDHE
- Cipher Strength: 256-bit
- Certificate: Valid, SHA-256
```

**ﻠﮒﺛB: ﮒ؟ﮒ۷ﻠﻝﺛ؟ﻝ۳ﭦﻛﺝ**

ﮒ؟ﮔﺑﻝﻠﻝﺛ؟ﮔﻛﭨﭘﻝ۳ﭦﻛﺝﻟﺁﺓﮒﻟﺅﺙ
- ﮔﮒ۰ﻝ،ﺁﻠﻝﺛ? `config/https_server_config.yaml`
- ﮒ؟۱ﮔﺓﻝ،ﺁﻠﻝﺛ? `config/https_client_config.yaml`
- APIﮒﺁﻠ۴ﻠﻝﺛ؟: `config/api_key_config.yaml`
