---
module_id: KE-1934--------watcher---watcher---000
status: active
title: 2.7 自漂移检测——Watcher 的 Watcher（决策 D-023-07）
category: module_blueprint
ttl: permanent
---

# 2.7 自漂移检测——Watcher 的 Watcher（决策 D-023-07）

2.7 自漂移检测——Watcher 的 Watcher（决策 D-023-07）

> **决策 D-023-07**：Drift detector 自身不能成为漂移盲区。定期对 drift detector 的配置文件和检测器注册表做 checksum 验证。自漂移检测使用最小独立逻辑（纯 stdlib，零依赖），确保即使 drift detector 本身损坏也能自检。
>
> **决策依据**：Watcher 的 Watcher 是分布式系统的经典难题。最小自检必须是独立逻辑——不能用 drift detector 的代码检测 drift detector 自身。

```yaml
self_drift:
  checks:
    - target: "_detector-registry.yaml"
      method: "SHA256 checksum vs 上次已知值"
      frequency: "每次 scan 前执行"
    - target: "drift-detector.py"
      method: "SHA256 checksum vs git HEAD 版本"
      frequency: "每次 scan 前执行"
    - target: "reconciler.py"
      method: "SHA256 checksum vs git HEAD 版本"
      frequency: "每次 scan 前执行"

  bootstrap_self_check:
    description: "最小自检——纯 stdlib，独立于 drift detector 主逻辑"
    method: "验证核心文件存在性 + SHA256 完整性 + _detector-registry.yaml 可解析性"
    on_failure: "P0 告警——drift detector 自身可能已被损坏"
    code_path: "src/zephyr/drift-detector/self_check.py"
    constraint: "self_check.py 只导入 stdlib（pathlib + hashlib + yaml 安全解析），不导入 zephyr 任何模块"

  immutable_manifest:
    description: "drift detector 自身的不可变清单——存在 Git 中，定期对比"
    files:
      - "src/zephyr/drift-detector/_detector-registry.yaml"
      - "src/zephyr/drift-detector/self_check.py"
```
