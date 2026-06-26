---
module_id: KE-1296
status: active
title: 1. Zone Crossing 校验
category: module_blueprint
ttl: permanent
---

# 1. Zone Crossing 校验

1. Zone Crossing 校验

```python
def _validate_zone_crossing(
    source_module: str,      # 当前模块ID
    target_module: str,      # 目标模块ID
    artifacts: list[PipelineArtifact]
) -> bool:
    """
    A区产出(M1-M5) → B区消费(M6-M11) 必须经过M5打包+M6边界标记
    任何直通路径 = ABORT
    """
    # 如果源在A区、目标在B区
    source_zone = "A" if source_module in A_ZONE else "B"
    target_zone = "A" if target_module in A_ZONE else "B"

    if source_zone == "A" and target_zone == "B":
        # 跨区必须经过M5→M6
        if not all(a.has_boundary_stamp("M6") for a in artifacts):
            raise ZoneCrossingViolation("A→B跨区未经M5打包+M6边界标记")

    return True
```
