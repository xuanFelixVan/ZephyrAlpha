---
module_id: KE-1105
status: active
title: config/ — 运行时配置目录
category: governance
---

# config/ — 运行时配置目录

config/ — 运行时配置目录

> `config/` 是项目根目录的第三个一级目录（与 `docs/`、`src/` 并列），存放系统运行时的声明式配置 YAML。
> 所有配置文件由对应的 `src/zephyr/` 模块在启动时一次性加载，运行期不再 IO。

```
config/
├── capabilities.yaml           # CBAC 能力注册表（Immutable Core）— AI 权限 ACL 的唯一真源
├── trigger_router.yaml         # M3 触发器路由分派表（Human-Gated）
├── compression/                # DocCompressor 压缩策略
│   └── policy.yaml             #   压缩不变量约束（Immutable Core）
├── risk/                       # （experimentalf/1g 规划中）风控阈值配置
├── drift_thresholds.yaml       # （experimentalf/1g 规划中）RI-07 DriftDetector 阈值
└── app.yaml                    # （beta 规划中）L01 基础设施应用配置
```
