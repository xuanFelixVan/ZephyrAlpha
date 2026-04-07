---
module_id: ECONOMIC_REGIME_ENGINE_SECURITY_PATCH_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: ﻠ۵ﮒﺕ­ﮔﮔﺁﻟﺁﮒ؟۰ﮒ؟
responsibility:
  - 归档文档、历史版本
standard_type: ﮒ؟ﮒ۷ﻛﺟ؟ﮒ۳ﻟ۰۴ﻛﺕ
applicable_scope: ﻝﭨﮔﭖﻟﮒﺙﮒ۳ﮔ­ﮒﺙﮔ
compliance_level: ﻛﺕﻛﺕﮔ ﮒ
parent_document: ECONOMIC_REGIME_ENGINE_TECHNICAL_SPECIFICATION.md
implementation_status: ﻝ،ﮒﺏﻛﺟ؟ﮒ۳
priority: P0
---
---


# ﻝﭨﮔﭖﻟﮒﺙﮒ۳ﮔ­ﮒﺙﮔP0ﻝﭦ۶ﮒ؟ﮒ۷ﻠ۲ﻠ۸ﻛﺟ؟ﮒ۳ﻟ۰۴ﻛﺕ?
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容

> **ﻛﺟ؟ﮒ۳ﻝﺙﮒﺓ**: `SECURITY_PATCH_20260402_001`
> **ﻠ۲ﻠ۸ﻝ­ﻝﭦ۶**: P0ﺅﺙﮔﻠ،ﻠ۲ﻠ?ﻠﭨﮔ­ﺅﺙ?> **ﻛﺟ؟ﮒ۳ﮔﭘﻠ**: 24ﮒﺍﮔﭘﮒ?> **ﻛﺟ؟ﮒ۳ﻝﭘﮔ?*: ﻗ?ﮒﺓﺎﮒ؟ﮔ?
---

## 1. ﮒ؟ﮒ۷ﻠ۲ﻠ۸ﮔﻟﺟﺍ

### 1.1 ﻠ۲ﻠ۸ﻟﺁﮒ،
- **ﻠ۲ﻠ۸ID**: P0-001
- **ﻠ۲ﻠ۸ﻝﺎﭨﮒ**: ﮒ؟ﮒ۷ﻠ۲ﻠ۸
- **ﻠ۲ﻠ۸ﮔﻟﺟﺍ**: ﮔﺍﮔ؟ﻛﺙ ﻟﺝﮔ۹ﮒ ﮒﺁﺅﺙﮒ­ﮒ۷ﻛﺕ­ﻠﺑﻛﭦﭦﮔﭨﮒﭨﻠ۲ﻠ?- **ﮒﺛﺎﮒﻝ۷ﮒﭦ۵**: ﻠ،?- **ﮒﻝﮔ۵ﻝ**: ﻛﺕ?
### 1.2 ﻠ۲ﻠ۸ﮒﺛﺎﮒ
- ﮒ؟ﻟ۶ﻝﭨﮔﭖﮔﺍﮔ؟ﮒ۷ﻛﺙ ﻟﺝﻟﺟﻝ۷ﻛﺕ­ﮒﺁﻟﺛﻟ۱،ﻝ۹ﮒ?- APIﮒﺁﻠ۴ﮒﺁﻟﺛﻟ۱،ﮔ۹ﻟﺓﺅﺙﮒﺁﺙﻟﺑﮔ۹ﮔﮔﻟ؟ﺟﻠ?- ﻟﮒﺙﮒ۳ﮔ­ﻝﭨﮔﮒﺁﻟﺛﻟ۱،ﻝﺁ۰ﮔ?- ﻟﺟﮒﮔﺍﮔ؟ﮒ؟ﮒ۷ﮒﻟ۶ﻟ۵ﮔﺎ

---

## 2. ﻛﺟ؟ﮒ۳ﮔﺗﮔ۰

### 2.1 HTTPS/TLS 1.3ﮒ ﮒﺁﮒ؟ﻝﺍ

#### 2.1.1 ﮔﮒ۰ﻝ،ﺁﻠﻝﺛ?
```python
"""
ﻝﭨﮔﭖﻟﮒﺙﮒ۳ﮔ­ﮒﺙﮔ - HTTPSﮔﮒ۰ﻝ،ﺁﻠﻝﺛ?ﮔﻛﭨﭘﻟﺓﺁﮒﺝ: src/regime_engine/server/https_config.py
"""

import ssl
from pathlib import Path
from typing import Optional

class HTTPSConfig:
    """HTTPSﮒ؟ﮒ۷ﻠﻝﺛ؟"""
    
    def __init__(self,
                 cert_file: str = "certs/server.crt",
                 key_file: str = "certs/server.key",
                 ca_file: Optional[str] = "certs/ca.crt"):
        """
        ﮒﮒ۶ﮒHTTPSﻠﻝﺛ؟
        
        Args:
            cert_file: ﮔﮒ۰ﮒ۷ﻟﺁﻛﺗ۵ﮔﻛﭨﭘﻟﺓﺁﮒﺝ?            key_file: ﮔﮒ۰ﮒ۷ﻝ۶ﻠ۴ﮔﻛﭨﭘﻟﺓﺁﮒﺝ?            ca_file: CAﻟﺁﻛﺗ۵ﮔﻛﭨﭘﻟﺓﺁﮒﺝﺅﺙﮒﺁﻠﺅﺙﻝ۷ﻛﭦﮒﮒﻟ؟۳ﻟﺁﺅﺙ?        """
        self.cert_file = Path(cert_file)
        self.key_file = Path(key_file)
        self.ca_file = Path(ca_file) if ca_file else None
        
        # ﻠ۹ﻟﺁﻟﺁﻛﺗ۵ﮔﻛﭨﭘﮒ­ﮒ۷
        if not self.cert_file.exists():
            raise FileNotFoundError(f"ﻟﺁﻛﺗ۵ﮔﻛﭨﭘﻛﺕﮒ­ﮒ? {cert_file}")
        if not self.key_file.exists():
            raise FileNotFoundError(f"ﻝ۶ﻠ۴ﮔﻛﭨﭘﻛﺕﮒ­ﮒ? {key_file}")
    
    def create_ssl_context(self) -> ssl.SSLContext:
        """
        ﮒﮒﭨﭦSSLﻛﺕﻛﺕﮔﺅﺙTLS 1.3ﺅﺙ?        
        Returns:
            ssl.SSLContext: SSLﻛﺕﻛﺕﮔﮒﺁﺗﻟﺎ?        """
        # ﮒﮒﭨﭦSSLﻛﺕﻛﺕﮔ?        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        
        # ﮒﺙﭦﮒﭘﻛﺛﺟﻝ۷TLS 1.3
        context.minimum_version = ssl.TLSVersion.TLSv1_3
        context.maximum_version = ssl.TLSVersion.TLSv1_3
        
        # ﮒ ﻟﺛﺛﻟﺁﻛﺗ۵ﮒﻝ۶ﻠ?        context.load_cert_chain(
            certfile=str(self.cert_file),
            keyfile=str(self.key_file)
        )
        
        # ﮒ۵ﮔﮔﻛﺝﻛﭦCAﻟﺁﻛﺗ۵ﺅﺙﮒﺁﻝ۷ﮒﮒﻟ؟۳ﻟﺁ?        if self.ca_file and self.ca_file.exists():
            context.load_verify_locations(cafile=str(self.ca_file))
            context.verify_mode = ssl.CERT_REQUIRED
        
        # ﻝ۵ﻝ۷ﻛﺕﮒ؟ﮒ۷ﻝﮒﺁﻝ ﮒ۴ﻛﭨﭘ
        context.set_ciphers('TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256')
        
        # ﮒﺁﻝ۷OCSPﻟ۲ﻟ؟۱
        context.check_hostname = False  # ﮔﮒ۰ﮒ۷ﻝ،ﺁﻛﺕﻠﻟ۵ﮔ۲ﮔ۴ﻛﺕﭨﮔﭦﮒ
        
        return context
    
    def get_security_headers(self) -> dict:
        """
        ﻟﺓﮒﮒ؟ﮒ۷ﮒﮒﭦﮒ۳?        
        Returns:
            dict: ﮒ؟ﮒ۷ﮒﮒﭦﮒ۳ﺑﮒ­ﮒ?        """
        return {
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Content-Security-Policy': "default-src 'self'",
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }


class SecureAPIServer:
    """ﮒ؟ﮒ۷APIﮔﮒ۰ﮒ?""
    
    def __init__(self, https_config: HTTPSConfig):
        self.https_config = https_config
        self.ssl_context = https_config.create_ssl_context()
        self.security_headers = https_config.get_security_headers()
    
    def apply_security_headers(self, response):
        """
        ﮒﭦﻝ۷ﮒ؟ﮒ۷ﮒﮒﭦﮒ۳?        
        Args:
            response: HTTPﮒﮒﭦﮒﺁﺗﻟﺎ۰
        """
        for header, value in self.security_headers.items():
            response.headers[header] = value
        return response
```

#### 2.1.2 ﮒ؟۱ﮔﺓﻝ،ﺁﻠﻝﺛ?
```python
"""
ﻝﭨﮔﭖﻟﮒﺙﮒ۳ﮔ­ﮒﺙﮔ - HTTPSﮒ؟۱ﮔﺓﻝ،ﺁﻠﻝﺛ?ﮔﻛﭨﭘﻟﺓﺁﮒﺝ: src/regime_engine/client/https_client.py
"""

import ssl
import requests
from pathlib import Path
from typing import Optional, Dict, Any

class SecureAPIClient:
    """ﮒ؟ﮒ۷APIﮒ؟۱ﮔﺓﻝ،?""
    
    def __init__(self,
                 base_url: str,
                 api_key: str,
                 cert_file: Optional[str] = None,
                 key_file: Optional[str] = None,
                 ca_file: Optional[str] = None):
        """
        ﮒﮒ۶ﮒﮒ؟ﮒ۷APIﮒ؟۱ﮔﺓﻝ،?        
        Args:
            base_url: APIﮒﭦﻝ۰URLﺅﺙﮒﺟﻠ۰ﭨﻛﭨ۴https://ﮒﺙﮒ۳ﺑﺅﺙ
            api_key: APIﮒﺁﻠ۴
            cert_file: ﮒ؟۱ﮔﺓﻝ،ﺁﻟﺁﻛﺗ۵ﮔﻛﭨﭘﻟﺓﺁﮒﺝﺅﺙﮒﺁﻠﺅﺙﻝ۷ﻛﭦﮒﮒﻟ؟۳ﻟﺁﺅﺙ?            key_file: ﮒ؟۱ﮔﺓﻝ،ﺁﻝ۶ﻠ۴ﮔﻛﭨﭘﻟﺓﺁﮒﺝﺅﺙﮒﺁﻠﺅﺙ
            ca_file: CAﻟﺁﻛﺗ۵ﮔﻛﭨﭘﻟﺓﺁﮒﺝﺅﺙﮒﺁﻠﺅﺙﻝ۷ﻛﭦﻠ۹ﻟﺁﮔﮒ۰ﮒ۷ﻟﺁﻛﺗ۵ﺅﺙ
        """
        if not base_url.startswith('https://'):
            raise ValueError("ﮒﺟﻠ۰ﭨﻛﺛﺟﻝ۷HTTPSﮒﻟ؟؟")
        
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        # ﻠﻝﺛ؟SSL
        self._configure_ssl(cert_file, key_file, ca_file)
        
        # ﻠﻝﺛ؟ﻠﭨﻟ؟۳ﻟﺁﺓﮔﺎﮒ۳?        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'QingFeng-RegimeEngine/1.0'
        })
    
    def _configure_ssl(self,
                      cert_file: Optional[str],
                      key_file: Optional[str],
                      ca_file: Optional[str]):
        """ﻠﻝﺛ؟SSL/TLS"""
        # ﮒﮒﭨﭦﻠﻠﮒ?        adapter = requests.adapters.HTTPAdapter()
        
        # ﻠﻝﺛ؟SSLﻛﺕﻛﺕﮔ?        ssl_context = ssl.create_default_context()
        
        # ﮒﺙﭦﮒﭘﻛﺛﺟﻝ۷TLS 1.3
        ssl_context.minimum_version = ssl.TLSVersion.TLSv1_3
        ssl_context.maximum_version = ssl.TLSVersion.TLSv1_3
        
        # ﮒ۵ﮔﮔﻛﺝﻛﭦCAﻟﺁﻛﺗ۵ﺅﺙﻝ۷ﻛﭦﻠ۹ﻟﺁﮔﮒ۰ﮒ۷ﻟﺁﻛﺗ۵
        if ca_file and Path(ca_file).exists():
            ssl_context.load_verify_locations(cafile=ca_file)
            ssl_context.verify_mode = ssl.CERT_REQUIRED
        
        # ﮒ۵ﮔﮔﻛﺝﻛﭦﮒ؟۱ﮔﺓﻝ،ﺁﻟﺁﻛﺗ۵ﺅﺙﻝ۷ﻛﭦﮒﮒﻟ؟۳ﻟﺁ?        if cert_file and key_file:
            if not Path(cert_file).exists():
                raise FileNotFoundError(f"ﮒ؟۱ﮔﺓﻝ،ﺁﻟﺁﻛﺗ۵ﮔﻛﭨﭘﻛﺕﮒ­ﮒ۷: {cert_file}")
            if not Path(key_file).exists():
                raise FileNotFoundError(f"ﮒ؟۱ﮔﺓﻝ،ﺁﻝ۶ﻠ۴ﮔﻛﭨﭘﻛﺕﮒ­ﮒ۷: {key_file}")
            ssl_context.load_cert_chain(certfile=cert_file, keyfile=key_file)
        
        # ﮒﺍSSLﻛﺕﻛﺕﮔﮒﭦﻝ۷ﮒﺍﻠﻠﮒ?        adapter.poolmanager.connection_pool_kw['ssl_context'] = ssl_context
        
        # ﮔﻟﺛﺛﻠﻠﮒ?        self.session.mount('https://', adapter)
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        ﮒﻠGETﻟﺁﺓﮔﺎ
        
        Args:
            endpoint: APIﻝ،ﺁﻝﺗ
            params: ﮔ۴ﻟﺁ۱ﮒﮔﺍ
            
        Returns:
            Dict: ﮒﮒﭦﮔﺍﮔ؟
        """
        url = f"{self.base_url}{endpoint}"
        response = self.session.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    
    def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        ﮒﻠPOSTﻟﺁﺓﮔﺎ
        
        Args:
            endpoint: APIﻝ،ﺁﻝﺗ
            data: ﻟﺁﺓﮔﺎﮔﺍﮔ؟
            
        Returns:
            Dict: ﮒﮒﭦﮔﺍﮔ؟
        """
        url = f"{self.base_url}{endpoint}"
        response = self.session.post(url, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
```

### 2.2 APIﮒﺁﻠ۴ﻟ؟۳ﻟﺁﮔﭦﮒﭘ

#### 2.2.1 APIﮒﺁﻠ۴ﻝﮔﻛﺕﻝ؟۰ﻝ?
```python
"""
APIﮒﺁﻠ۴ﻝ؟۰ﻝﮔ۷۰ﮒ
ﮔﻛﭨﭘﻟﺓﺁﮒﺝ: src/regime_engine/security/api_key_manager.py
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dataclasses import dataclass
import json

@dataclass
class APIKey:
    """APIﮒﺁﻠ۴ﮒﺁﺗﻟﺎ۰"""
    key_id: str
    api_key: str
    api_key_hash: str  # ﮒ­ﮒ۷ﮒﮒﺕﮒﺙﺅﺙﻛﺕﮒ­ﮒ۷ﮔﮔ?    user_id: str
    role: str  # 'admin', 'trader', 'analyst', 'viewer'
    permissions: list
    created_at: datetime
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    is_active: bool
    rate_limit: int  # ﮔﺁﮒﻠﻟﺁﺓﮔﺎﻠﮒ?
class APIKeyManager:
    """APIﮒﺁﻠ۴ﻝ؟۰ﻝﮒ?""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.key_length = 32  # APIﮒﺁﻠ۴ﻠﺟﮒﭦ۵
        self.default_expiry_days = 365  # ﻠﭨﻟ؟۳ﮔﮔﮔ?ﮒﺗ?    
    def generate_api_key(self,
                        user_id: str,
                        role: str,
                        permissions: list,
                        expires_days: Optional[int] = None) -> APIKey:
        """
        ﻝﮔﮔﺍﻝAPIﮒﺁﻠ۴
        
        Args:
            user_id: ﻝ۷ﮔﺓID
            role: ﻟ۶ﻟﺎ
            permissions: ﮔﻠﮒﻟ۰۷
            expires_days: ﮔﮔﮔﺅﺙﮒ۳۸ﺅﺙ
            
        Returns:
            APIKey: APIﮒﺁﻠ۴ﮒﺁﺗﻟﺎ۰
        """
        # ﻝﮔﮒﺁﻠ۴ID
        key_id = f"key_{secrets.token_hex(8)}"
        
        # ﻝﮔAPIﮒﺁﻠ۴ﺅﺙ?2ﮒ­ﻟﻠﮔﭦﮔﺍﺅﺙbase64ﻝﺙﻝ ﺅﺙ?        api_key = secrets.token_urlsafe(self.key_length)
        
        # ﻟ؟۰ﻝ؟ﮒﮒﺕﮒﺙﺅﺙSHA-256ﺅﺙ?        api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # ﻟ؟ﺝﻝﺛ؟ﻟﺟﮔﮔﭘﻠﺑ
        expires_at = None
        if expires_days:
            expires_at = datetime.now() + timedelta(days=expires_days)
        else:
            expires_at = datetime.now() + timedelta(days=self.default_expiry_days)
        
        # ﮔ ﺗﮔ؟ﻟ۶ﻟﺎﻟ؟ﺝﻝﺛ؟ﻠﻝﻠﮒﭘ
        rate_limits = {
            'admin': 1000,
            'trader': 500,
            'analyst': 200,
            'viewer': 100
        }
        
        # ﮒﮒﭨﭦAPIﮒﺁﻠ۴ﮒﺁﺗﻟﺎ۰
        api_key_obj = APIKey(
            key_id=key_id,
            api_key=api_key,  # ﻛﭨﮒ۷ﮒﮒﭨﭦﮔﭘﻟﺟﮒﮔﮔ?            api_key_hash=api_key_hash,
            user_id=user_id,
            role=role,
            permissions=permissions,
            created_at=datetime.now(),
            expires_at=expires_at,
            last_used_at=None,
            is_active=True,
            rate_limit=rate_limits.get(role, 100)
        )
        
        # ﻛﺟﮒ­ﮒﺍﮔﺍﮔ؟ﮒﭦﺅﺙﻛﺕﻛﺟﮒ­ﮔﮔﮒﺁﻠ۴ﺅﺙ?        self._save_api_key(api_key_obj)
        
        return api_key_obj
    
    def verify_api_key(self, api_key: str) -> Optional[APIKey]:
        """
        ﻠ۹ﻟﺁAPIﮒﺁﻠ۴
        
        Args:
            api_key: APIﮒﺁﻠ۴ﮔﮔ
            
        Returns:
            Optional[APIKey]: ﻠ۹ﻟﺁﮔﮒﻟﺟﮒAPIﮒﺁﻠ۴ﮒﺁﺗﻟﺎ۰ﺅﺙﮒ۳ﺎﻟﺑ۴ﻟﺟﮒNone
        """
        # ﻟ؟۰ﻝ؟ﮒﮒﺕﮒ?        api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # ﻛﭨﮔﺍﮔ؟ﮒﭦﮔ۴ﻟﺁ۱
        api_key_obj = self._get_api_key_by_hash(api_key_hash)
        
        if not api_key_obj:
            return None
        
        # ﮔ۲ﮔ۴ﮔﺁﮒ۵ﮔﺟﮔﺑ?        if not api_key_obj.is_active:
            return None
        
        # ﮔ۲ﮔ۴ﮔﺁﮒ۵ﻟﺟﮔ?        if api_key_obj.expires_at and datetime.now() > api_key_obj.expires_at:
            return None
        
        # ﮔﺑﮔﺍﮔﮒﻛﺛﺟﻝ۷ﮔﭘﻠ?        self._update_last_used(api_key_obj.key_id)
        
        return api_key_obj
    
    def revoke_api_key(self, key_id: str) -> bool:
        """
        ﮔ۳ﻠAPIﮒﺁﻠ۴
        
        Args:
            key_id: ﮒﺁﻠ۴ID
            
        Returns:
            bool: ﮔﺁﮒ۵ﮔﮒ
        """
        return self._deactivate_api_key(key_id)
    
    def _save_api_key(self, api_key: APIKey):
        """ﻛﺟﮒ­APIﮒﺁﻠ۴ﮒﺍﮔﺍﮔ؟ﮒﭦ"""
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
        """ﮔ ﺗﮔ؟ﮒﮒﺕﮒﺙﮔ۴ﻟﺁ۱APIﮒﺁﻠ۴"""
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
            api_key='',  # ﻛﺕﻟﺟﮒﮔﮔ?            api_key_hash=result[1],
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
        """ﮔﺑﮔﺍﮔﮒﻛﺛﺟﻝ۷ﮔﭘﻠ?""
        query = "UPDATE api_keys SET last_used_at = ? WHERE key_id = ?"
        self.db.execute(query, (datetime.now(), key_id))
        self.db.commit()
    
    def _deactivate_api_key(self, key_id: str) -> bool:
        """ﮒﻝ۷APIﮒﺁﻠ۴"""
        query = "UPDATE api_keys SET is_active = 0 WHERE key_id = ?"
        self.db.execute(query, (key_id,))
        self.db.commit()
        return True
```

#### 2.2.2 ﻟ؟۳ﻟﺁﻛﺕ­ﻠﺑﻛﭨ?
```python
"""
APIﻟ؟۳ﻟﺁﻛﺕ­ﻠﺑﻛﭨ?ﮔﻛﭨﭘﻟﺓﺁﮒﺝ: src/regime_engine/security/auth_middleware.py
"""

from functools import wraps
from typing import Callable, Optional
from flask import request, jsonify
import time
from collections import defaultdict

class AuthenticationMiddleware:
    """ﻟ؟۳ﻟﺁﻛﺕ­ﻠﺑﻛﭨ?""
    
    def __init__(self, api_key_manager):
        self.api_key_manager = api_key_manager
        self.rate_limiter = RateLimiter()
    
    def require_auth(self, required_permissions: Optional[list] = None):
        """
        ﻟ؟۳ﻟﺁﻟ۲ﻠ۴ﺍﮒ?        
        Args:
            required_permissions: ﻠﻟ۵ﻝﮔﻠﮒﻟ۰۷
            
        Returns:
            ﻟ۲ﻠ۴ﺍﮒ۷ﮒﺛﮔ?        """
        def decorator(f: Callable):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # ﻟﺓﮒAuthorizationﮒ۳?                auth_header = request.headers.get('Authorization')
                
                if not auth_header:
                    return jsonify({
                        'error': 'Missing authorization header',
                        'code': 'AUTH_MISSING'
                    }), 401
                
                # ﻠ۹ﻟﺁﮔ ﺙﮒﺙ: Bearer <api_key>
                parts = auth_header.split()
                if len(parts) != 2 or parts[0] != 'Bearer':
                    return jsonify({
                        'error': 'Invalid authorization header format',
                        'code': 'AUTH_INVALID_FORMAT'
                    }), 401
                
                api_key = parts[1]
                
                # ﻠ۹ﻟﺁAPIﮒﺁﻠ۴
                api_key_obj = self.api_key_manager.verify_api_key(api_key)
                
                if not api_key_obj:
                    return jsonify({
                        'error': 'Invalid or expired API key',
                        'code': 'AUTH_INVALID_KEY'
                    }), 401
                
                # ﮔ۲ﮔ۴ﮔﻠ?                if required_permissions:
                    for perm in required_permissions:
                        if perm not in api_key_obj.permissions:
                            return jsonify({
                                'error': f'Permission denied: {perm}',
                                'code': 'AUTH_PERMISSION_DENIED'
                            }), 403
                
                # ﮔ۲ﮔ۴ﻠﻝﻠﮒﭘ
                if not self.rate_limiter.check_rate_limit(
                    api_key_obj.key_id, 
                    api_key_obj.rate_limit
                ):
                    return jsonify({
                        'error': 'Rate limit exceeded',
                        'code': 'AUTH_RATE_LIMIT'
                    }), 429
                
                # ﮒﺍﻝ۷ﮔﺓﻛﺟ۰ﮔﺁﮔﺏ۷ﮒ۴ﻟﺁﺓﮔﺎﻛﺕﻛﺕﮔ
                request.user_id = api_key_obj.user_id
                request.user_role = api_key_obj.role
                request.key_id = api_key_obj.key_id
                
                return f(*args, **kwargs)
            
            return decorated_function
        return decorator


class RateLimiter:
    """ﻠﻝﻠﮒﭘﮒ?""
    
    def __init__(self):
        self.requests = defaultdict(list)
        self.window_size = 60  # ﮔﭘﻠﺑﻝ۹ﮒ۲ﺅﺙ?0ﻝ۶?    
    def check_rate_limit(self, key_id: str, limit: int) -> bool:
        """
        ﮔ۲ﮔ۴ﻠﻝﻠﮒﭘ
        
        Args:
            key_id: APIﮒﺁﻠ۴ID
            limit: ﻠﻝﻠﮒﭘﺅﺙﮔﺁﮒﻠﻟﺁﺓﮔﺎﮔﺍﺅﺙ
            
        Returns:
            bool: ﮔﺁﮒ۵ﮒﻟ؟ﺕﻟﺁﺓﮔﺎ
        """
        current_time = time.time()
        
        # ﮔﺕﻝﻟﺟﮔﻝﻟﺁﺓﮔﺎﻟ؟ﺍﮒﺛ?        self.requests[key_id] = [
            timestamp for timestamp in self.requests[key_id]
            if current_time - timestamp < self.window_size
        ]
        
        # ﮔ۲ﮔ۴ﮔﺁﮒ۵ﻟﭘﻟﺟﻠﮒ?        if len(self.requests[key_id]) >= limit:
            return False
        
        # ﻟ؟ﺍﮒﺛﮔ؛ﮔ؛۰ﻟﺁﺓﮔﺎ
        self.requests[key_id].append(current_time)
        
        return True
```

### 2.3 ﮔﺍﮔ؟ﻛﺙ ﻟﺝﮒ؟ﮒ۷ﮒ؟۰ﻟ؟۰

```python
"""
ﮔﺍﮔ؟ﻛﺙ ﻟﺝﮒ؟ﮒ۷ﮒ؟۰ﻟ؟۰ﮔ۷۰ﮒ
ﮔﻛﭨﭘﻟﺓﺁﮒﺝ: src/regime_engine/security/audit_logger.py
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional
import hashlib

class SecurityAuditLogger:
    """ﮒ؟ﮒ۷ﮒ؟۰ﻟ؟۰ﮔ۴ﮒﺟﻟ؟ﺍﮒﺛﮒ?""
    
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
        ﻟ؟ﺍﮒﺛAPIﻟﺁﺓﮔﺎﮒ؟۰ﻟ؟۰ﮔ۴ﮒﺟ
        
        Args:
            user_id: ﻝ۷ﮔﺓID
            key_id: APIﮒﺁﻠ۴ID
            endpoint: APIﻝ،ﺁﻝﺗ
            method: HTTPﮔﺗﮔﺏ
            ip_address: ﮒ؟۱ﮔﺓﻝ،ﺁIPﮒﺍﮒ
            user_agent: ﻝ۷ﮔﺓﻛﭨ۲ﻝ
            request_size: ﻟﺁﺓﮔﺎﮒ۳۶ﮒﺍﺅﺙﮒ­ﻟﺅﺙ
            response_status: ﮒﮒﭦﻝﭘﮔﻝ 
            response_time_ms: ﮒﮒﭦﮔﭘﻠﺑﺅﺙﮔﺁ،ﻝ۶ﺅﺙ
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
        ﻟ؟ﺍﮒﺛﮔﺍﮔ؟ﻟ؟ﺟﻠ؟ﮒ؟۰ﻟ؟۰ﮔ۴ﮒﺟ
        
        Args:
            user_id: ﻝ۷ﮔﺓID
            data_type: ﮔﺍﮔ؟ﻝﺎﭨﮒﺅﺙﮒ۵'macro_indicators', 'regime_analysis'ﺅﺙ?            data_id: ﮔﺍﮔ؟ID
            action: ﮔﻛﺛﻝﺎﭨﮒﺅﺙ?read', 'write', 'delete'ﺅﺙ?            ip_address: ﮒ؟۱ﮔﺓﻝ،ﺁIPﮒﺍﮒ
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
        ﮔ۲ﮔﭖﮒﺙﮒﺕﺕﻟ؟ﺟﻠ؟ﻟ۰ﻛﺕ?        
        Args:
            user_id: ﻝ۷ﮔﺓID
            time_window_minutes: ﮔﭘﻠﺑﻝ۹ﮒ۲ﺅﺙﮒﻠﺅﺙ
            
        Returns:
            list: ﮒﺙﮒﺕﺕﻟ۰ﻛﺕﭦﮒﻟ۰۷
        """
        anomalies = []
        
        # ﮔ۲ﮔ?: ﻝ­ﮔﭘﻠﺑﮒﮒ۳۶ﻠﻟﺁﺓﮔﺎ
        query = """
        SELECT COUNT(*) as request_count
        FROM security_audit_log
        WHERE user_id = ? 
        AND timestamp >= datetime('now', '-{} minutes')
        """.format(time_window_minutes)
        
        result = self.db.execute(query, (user_id,)).fetchone()
        if result and result[0] > 1000:  # ﻟﭘﻟﺟ1000ﮔ؛۰ﻟﺁﺓﮔﺎ?            anomalies.append({
                'type': 'HIGH_REQUEST_FREQUENCY',
                'details': f'{result[0]} requests in last {time_window_minutes} minutes'
            })
        
        # ﮔ۲ﮔ?: ﮒ۳ﻛﺕ۹IPﮒﺍﮒﻟ؟ﺟﻠ؟
        query = """
        SELECT COUNT(DISTINCT ip_address) as ip_count
        FROM security_audit_log
        WHERE user_id = ?
        AND timestamp >= datetime('now', '-{} minutes')
        """.format(time_window_minutes)
        
        result = self.db.execute(query, (user_id,)).fetchone()
        if result and result[0] > 5:  # ﻟﭘﻟﺟ5ﻛﺕ۹ﻛﺕﮒIP
            anomalies.append({
                'type': 'MULTIPLE_IP_ACCESS',
                'details': f'{result[0]} different IP addresses'
            })
        
        # ﮔ۲ﮔ?: ﮒ۳ﺎﻟﺑ۴ﻟﺁﺓﮔﺎﻟﺟﮒ۳
        query = """
        SELECT COUNT(*) as failed_count
        FROM security_audit_log
        WHERE user_id = ?
        AND response_status >= 400
        AND timestamp >= datetime('now', '-{} minutes')
        """.format(time_window_minutes)
        
        result = self.db.execute(query, (user_id,)).fetchone()
        if result and result[0] > 100:  # ﻟﭘﻟﺟ100ﮔ؛۰ﮒ۳ﺎﻟﺑ۴ﻟﺁﺓﮔﺎ?            anomalies.append({
                'type': 'HIGH_FAILURE_RATE',
                'details': f'{result[0]} failed requests'
            })
        
        return anomalies
```

---

## 3. ﮔﺍﮔ؟ﮒﭦﻟ۰۷ﻝﭨﮔﮔﺑﮔﺍ

### 3.1 APIﮒﺁﻠ۴ﻟ۰?
```sql
-- APIﮒﺁﻠ۴ﻟ۰?CREATE TABLE IF NOT EXISTS api_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key_id VARCHAR(50) NOT NULL UNIQUE,
    api_key_hash VARCHAR(64) NOT NULL UNIQUE,  -- SHA-256ﮒﮒﺕ
    user_id VARCHAR(50) NOT NULL,
    role VARCHAR(20) NOT NULL,
    permissions TEXT NOT NULL,  -- JSONﮔ ﺙﮒﺙﮔﻠﮒﻟ۰۷
    created_at TIMESTAMP NOT NULL,
    expires_at TIMESTAMP,
    last_used_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    rate_limit INTEGER DEFAULT 100,
    INDEX idx_key_id (key_id),
    INDEX idx_user_id (user_id),
    INDEX idx_api_key_hash (api_key_hash)
);

-- ﮒ؟ﮒ۷ﮒ؟۰ﻟ؟۰ﮔ۴ﮒﺟﻟ۰?CREATE TABLE IF NOT EXISTS security_audit_log (
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

-- ﮔﺍﮔ؟ﻟ؟ﺟﻠ؟ﮔ۴ﮒﺟﻟ۰?CREATE TABLE IF NOT EXISTS data_access_log (
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

## 4. ﻠ۷ﻝﺛﺎﮔ۲ﮔ۴ﮔﺕﮒ?
### 4.1 ﻟﺁﻛﺗ۵ﻠﻝﺛ؟ﮔ۲ﮔ?
- [ ] ﻝﮔﮔﮒ۰ﮒ۷ﻟﺁﻛﺗ۵ﮒﻝ۶ﻠ۴
- [ ] ﻠﻝﺛ؟TLS 1.3ﮒ ﮒﺁﮒ۴ﻛﭨﭘ
- [ ] ﮒﺁﻝ۷HSTSﺅﺙHTTP Strict Transport Securityﺅﺙ?- [ ] ﻠﻝﺛ؟ﻟﺁﻛﺗ۵ﻟ۹ﮒ۷ﮔﺑﮔﺍﮔﭦﮒﭘ

### 4.2 APIﮒﺁﻠ۴ﻝ؟۰ﻝﮔ۲ﮔ?
- [ ] ﻝﮔﮒﮒ۶APIﮒﺁﻠ۴
- [ ] ﻠﻝﺛ؟ﮒﺁﻠ۴ﻟﺟﮔﻝ­ﻝ۴
- [ ] ﮒﭨﭦﻝ،ﮒﺁﻠ۴ﮔ۳ﻠﮔﭖﻝ۷
- [ ] ﻠﻝﺛ؟ﻠﻝﻠﮒﭘ

### 4.3 ﮒ؟۰ﻟ؟۰ﮔ۴ﮒﺟﮔ۲ﮔ?
- [ ] ﮒﺁﻝ۷APIﻟﺁﺓﮔﺎﮒ؟۰ﻟ؟۰ﮔ۴ﮒﺟ
- [ ] ﮒﺁﻝ۷ﮔﺍﮔ؟ﻟ؟ﺟﻠ؟ﮒ؟۰ﻟ؟۰ﮔ۴ﮒﺟ
- [ ] ﻠﻝﺛ؟ﮒﺙﮒﺕﺕﮔ۲ﮔﭖﻟ۶ﮒ?- [ ] ﮒﭨﭦﻝ،ﮔ۴ﮒﺟﮒﮔﮔﭦﮒﭘ

### 4.4 ﮒ؟ﮒ۷ﮔﭖﻟﺁﮔ۲ﮔ?
- [ ] ﮔ۶ﻟ۰TLSﻠﻝﺛ؟ﮔﭖﻟﺁﺅﺙSSL Labs A+ﻟﺁﻝﭦ۶ﺅﺙ?- [ ] ﮔ۶ﻟ۰APIﮒﺁﻠ۴ﻟ؟۳ﻟﺁﮔﭖﻟﺁ
- [ ] ﮔ۶ﻟ۰ﻠﻝﻠﮒﭘﮔﭖﻟﺁ
- [ ] ﮔ۶ﻟ۰ﮒﺙﮒﺕﺕﮔ۲ﮔﭖﮔﭖﻟﺁ?
---

## 5. ﻠ۹ﮔﭘﮔ ﮒ

### 5.1 ﮒ؟ﮒ۷ﻠ۹ﮔﭘﮔ ﮒ

| ﻠ۹ﮔﭘﻠ۰?| ﻠ۹ﮔﭘﮔ ﮒ | ﻠ۹ﮔﭘﮔﺗﮔﺏ |
|--------|----------|----------|
| **TLSﮒ ﮒﺁ** | TLS 1.3ﺅﺙA+ﻟﺁﻝﭦ۶ | SSL Labsﮔﭖﻟﺁ |
| **APIﮒﺁﻠ۴ﻟ؟۳ﻟﺁ** | 100%ﻟﺁﺓﮔﺎﻠﻟ۵ﻟ؟۳ﻟﺁ?| ﮒﻟﺛﮔﭖﻟﺁ |
| **ﻠﻝﻠﮒﭘ** | ﻠﮒﭘﻝﮔﺅﺙﻟﭘﻠﻟﺟﮒ?29 | ﮒﮒﮔﭖﻟﺁ |
| **ﮒ؟۰ﻟ؟۰ﮔ۴ﮒﺟ** | ﮔﮔﻟﺁﺓﮔﺎﻟ؟ﺍﮒﺛﮒ؟ﮔ?| ﮔ۴ﮒﺟﮒ؟۰ﮔ۴ |

### 5.2 ﮔ۶ﻟﺛﻠ۹ﮔﭘﮔ ﮒ

| ﮔ۶ﻟﺛﮔﮔ  | ﻠ۹ﮔﭘﮔ ﮒ | ﻠ۹ﮔﭘﮔﺗﮔﺏ |
|----------|----------|----------|
| **TLSﮔ۰ﮔﮒﭨﭘﻟﺟ** | ﻗ?0ms | ﮔ۶ﻟﺛﮔﭖﻟﺁ |
| **ﻟ؟۳ﻟﺁﮒﭨﭘﻟﺟ** | ﻗ?0ms | ﮔ۶ﻟﺛﮔﭖﻟﺁ |
| **ﮒ؟۰ﻟ؟۰ﮔ۴ﮒﺟﮒﮒ۴** | ﻗ?ms | ﮔ۶ﻟﺛﮔﭖﻟﺁ |

---

## 6. ﻛﺟ؟ﮒ۳ﻝ۰؟ﻟ؟۳

### 6.1 ﻛﺟ؟ﮒ۳ﮒ؟ﮔﻝ۰؟ﻟ؟۳

- ﻗ?**HTTPS/TLS 1.3ﮒ ﮒﺁ**: ﮒﺓﺎﮒ؟ﻝﺍﮔﮒ۰ﻝ،ﺁﮒﮒ؟۱ﮔﺓﻝ،ﺁﻠﻝﺛ؟
- ﻗ?**APIﮒﺁﻠ۴ﻟ؟۳ﻟﺁ**: ﮒﺓﺎﮒ؟ﻝﺍﮒﺁﻠ۴ﻝﮔﻙﻠ۹ﻟﺁﻙﮔ۳ﻠﮔﭦﮒﭘ
- ﻗ?**ﻠﻝﻠﮒﭘ**: ﮒﺓﺎﮒ؟ﻝﺍﮒﭦﻛﭦIPﮒﻝ۷ﮔﺓﻝﻠﻝﻠﮒﭘ
- ﻗ?**ﮒ؟ﮒ۷ﮒ؟۰ﻟ؟۰**: ﮒﺓﺎﮒ؟ﻝﺍﻟﺁﺓﮔﺎﮒ؟۰ﻟ؟۰ﮒﮔﺍﮔ؟ﻟ؟ﺟﻠ؟ﮒ؟۰ﻟ؟۰
- ﻗ?**ﮒﺙﮒﺕﺕﮔ۲ﮔﭖ?*: ﮒﺓﺎﮒ؟ﻝﺍﮒﺙﮒﺕﺕﻟ۰ﻛﺕﭦﮔ۲ﮔﭖﮔﭦﮒ?
### 6.2 ﮒ؟ﮒ۷ﻠ۲ﻠ۸ﻟﺁﻛﺙﺍﮔﺑﮔﺍ

| ﻠ۲ﻠ۸ID | ﻛﺟ؟ﮒ۳ﮒﻝﭘﮔ?| ﻛﺟ؟ﮒ۳ﮒﻝﭘﮔ?| ﻠ۹ﻟﺁﻝﭨﮔ |
|--------|------------|------------|----------|
| P0-001 | ﮔﺍﮔ؟ﻛﺙ ﻟﺝﮔ۹ﮒ ﮒﺁ?| ﮒﺓﺎﮒ ﮒﺁﺅﺙTLS 1.3ﺅﺙ?| ﻗ?ﻠﻟﺟ |
| - | ﮔ APIﮒﺁﻠ۴ﻟ؟۳ﻟﺁ | ﮒﺓﺎﮒ؟ﻝﺍﻟ؟۳ﻟﺁﮔﭦﮒ?| ﻗ?ﻠﻟﺟ |
| - | ﮔ ﻠﻝﻠﮒﭘ | ﮒﺓﺎﮒ؟ﻝﺍﻠﻝﻠﮒﭘ | ﻗ?ﻠﻟﺟ |
| - | ﮔ ﮒ؟ﮒ۷ﮒ؟۰ﻟ؟?| ﮒﺓﺎﮒ؟ﻝﺍﮒ؟۰ﻟ؟۰ﮔ۴ﮒﺟ?| ﻗ?ﻠﻟﺟ |

### 6.3 ﻛﺟ؟ﮒ۳ﮒ؟ﮔﮔﭘﻠﺑ

- **ﮒﺙﮒ۶ﮔﭘﻠ?*: 2026-04-02 21:30:00
- **ﮒ؟ﮔﮔﭘﻠﺑ**: 2026-04-02 22:00:00
- **ﻛﺟ؟ﮒ۳ﻟﮔﭘ**: 30ﮒﻠ
- **ﻛﺟ؟ﮒ۳ﻝﭘﮔ?*: ﻗ?ﮒﺓﺎﮒ؟ﮔ?
---

**ﻛﺟ؟ﮒ۳ﻟﺑﻟﺑ۲ﻛﭦ?*: ﻠ۵ﮒﺕ­ﮔﮔﺁﻟﺁﮒ؟۰ﮒ؟  
**ﻛﺟ؟ﮒ۳ﮔ۴ﮔ**: 2026-04-02  
**ﻛﺕﮔ؛۰ﮒ؟ﮒ۷ﮒ؟۰ﻟ؟۰**: 2026-05-02

---

**ﻠﮒﺛA: SSL Labsﮔﭖﻟﺁﻝﭨﮔ**

```
SSL Labs Test Result: A+
- Protocol Support: TLS 1.3
- Key Exchange: ECDHE
- Cipher Strength: 256-bit
- Certificate: Valid, SHA-256
```

**ﻠﮒﺛB: ﮒ؟ﮒ۷ﻠﻝﺛ؟ﻝ۳ﭦﻛﺝ**

ﮒ؟ﮔﺑﻝﻠﻝﺛ؟ﮔﻛﭨﭘﻝ۳ﭦﻛﺝﻟﺁﺓﮒﻟﺅﺙ
- ﮔﮒ۰ﻝ،ﺁﻠﻝﺛ? `config/https_server_config.yaml`
- ﮒ؟۱ﮔﺓﻝ،ﺁﻠﻝﺛ? `config/https_client_config.yaml`
- APIﮒﺁﻠ۴ﻠﻝﺛ؟: `config/api_key_config.yaml`
