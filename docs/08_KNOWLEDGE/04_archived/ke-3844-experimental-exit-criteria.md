---
module_id: KE-3693
title: experimental exit_criteria
category: governance
---

# experimental exit_criteria

experimental exit_criteria

| ID | 描述 | 校验方式 |
|----|------|---------|
| EXIT-1-01 | 5 大服务的 InProcess* 实现全部落地，进程内库形态 | `pytest tests/integration/services/` |
| EXIT-1-02 | 5 大服务的 `protocol.py` 抽象基类全部就位 | `grep Protocol src/zephyr/*/protocol.py` |
| EXIT-1-03 | `bootstrap.py` wiring 完成，依赖注入跑通 | `pytest tests/integration/bootstrap/` |
| EXIT-1-04 | 单元测试覆盖率 ≥ 70% | `pytest --cov=src/zephyr --cov-fail-under=70` |
| EXIT-1-05 | 冷启动 SLO 达标（VMS bootstrap 200 份 < 60s）| 性能基准测试 |
