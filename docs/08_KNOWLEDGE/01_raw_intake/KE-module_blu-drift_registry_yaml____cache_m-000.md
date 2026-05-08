---
module_id: KE-module_blu-drift_registry_yaml____cache_m-000
title: drift_registry.yaml —— cache_manager.py 自动维护
category: module_blueprint
---

# drift_registry.yaml —— cache_manager.py 自动维护

drift_registry.yaml —— cache_manager.py 自动维护
drift_entries:
  - func: "zephyr.shared.config_loader.load_config"
    fingerprint_history:
      - at: "2025-12-01"
        fingerprint: "sha256:a1b2c3..."
        params: "(str, Dict[str, Any])"
        return_type: "Config"
      - at: "2026-02-15"
        fingerprint: "sha256:d4e5f6..."
        params: "(str, Optional[Dict[str, Any]])"
        return_type: "Optional[Config]"             # ← 类型漂移！
      - at: "2026-05-01"  
        fingerprint: "sha256:g7h8i9..."
        params: "(str, dict[str, Any] | None)"
        return_type: "Config | None"                # ← 再次漂移！
    stability: "UNSTABLE"                            # 3 次扫描 3 个不同指纹
    stage_0_5_action: "SKIP"                         # 签名匹配对此函数关闭
    recommendation: "类型注解仍在重构中——待 API 稳定后手动标记为 STABLE 恢复 Stage 0.5"
```
