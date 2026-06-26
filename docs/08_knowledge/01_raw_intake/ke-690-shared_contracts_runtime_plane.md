---
module_id: KE-618
status: active
title: shared/contracts/runtime_plane_tag.py (v1.0.0 contract-only, J1 批次 G 落盘)
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# shared/contracts/runtime_plane_tag.py (v1.0.0 contract-only, J1 批次 G 落盘)

shared/contracts/runtime_plane_tag.py (v1.0.0 contract-only, J1 批次 G 落盘)
from enum import Enum

class RuntimePlane(Enum):
    """
    运行平面标签 — 正交于 14 层业务分层的执行维度标签。

    用法 1（模块级装饰器）：
        @runtime_plane(RuntimePlane.HOT_PATH)
        class SmartOrderRouter: ...

    用法 2（contract 基类字段）：
        class FactorBase:
            runtime_plane: ClassVar[RuntimePlane] = RuntimePlane.WARM_PATH

    用法 3（frontmatter 声明，对于纯文档 / YAML / Rego）：
        ---
        runtime_plane: warm_path
        ---
    """
    HOT_PATH = "hot_path"   # < 10ms P99, C++/Rust/kernel-bypass
    WARM_PATH = "warm_path" # 10ms-1s P95, Python asyncio
    COLD_PATH = "cold_path" # > 1s batch, Spark/Dask/Airflow

    # 预留未来子档
    ULTRA_HOT = "ultra_hot"  # < 100µs, FPGA (T-ULTRA 激活后启用)
```

**预留原则**：
- enum 定义落盘但**不强制任何现有模块立即标注**（避免波动）
- Sprint 0+ 施工时强制**新增子模块必须标注**（OQ-083 关闭时已登记为"未来标注义务"）
- 03-AA §4.1 `runtime_plane` 列作为**主真源**；装饰器 / frontmatter 作为**代码级辅助标注**（J1 批次 C 落盘）

---
