---
ttl: task_bound
title: F105 密钥治理——挖干案卷
session: zc-l10-20260927
---

# F105 · 密钥治理（secrets.py 唯一通道+三道 gate+生命周期）

> 总册行（00_全环节总册.md:180）：built（M3：env 单因子信任绑定待裁）｜上游 —｜下游 全链｜P1｜G9
> 第一证据源：fullflow_mining/m3_governance/01_runtime_guards.md＋04_coverage_gaps.md＋SECRETS.md＋src/zephyr/shared/security/secrets.py

## 一、六向台账（实证锚点）

| 向 | 实测证据（本日复核） |
|---|---|
| 上游输入 | 裁定 #ARCH-SECRETS-GOV-001（S-1 显性化治理/S-3 consistency gate）＋TRAE-031 SEC-001~SEC-006＋config/secret_registry.yaml（结构化密钥声明真源） |
| 下游消费 | 全链读密钥面（secrets.py 542 行唯一接口）；secret_registry_drift reconciler（gov_audit 包内，registry↔.env↔era 三方漂移 post-commit 对账） |
| 自动化触发 | commit-time：三道 in-process gate（--no-verify 不可绕）；post-commit：secret_registry_drift 对账（M3 04 §三"半真空"行）；无运行时拦截 |
| 真源与注册表 | SECRETS.md（密钥管理显性入口，8 个服务文件分布 §1）＋src/zephyr/shared/security/secrets.py（**542 行**）＋config/secret_registry.yaml＋.env.example（模板） |
| 门禁与质量尺 | 三道 gate（SECRETS.md §2.3 实证）：**NO-BARE-GETENV（priority 81，diff-aware 只扫新增行）＋NO-SECRET-HARDCODE（priority 128，扫 .py/.yaml/.yml/.json/.toml）＋secret_registry_consistency_gate（S-3，新增密钥三步同步校验）**；全 fail-closed；豁免=tests//.env.example/扫描脚本自身/docstring/注释/import 行 |
| 当前运行状态 | built（黄）：门+通道+对账三件全在产；运行时侧半真空（os.environ 读无 patch，仅门+事后对账）＋env 授权单因子信任待裁（总册已注记） |

## 二、子模块三级枚举

1. **读取通道（secrets.py，542 行）**：密钥统一读取接口；配套同包 ssot_guard.py（SSoT 守卫）/capability.py/sandbox_executor.py（本日 ls src/zephyr/shared/security/ 实证五件）。
2. **commit 侧三道 gate**：NO-BARE-GETENV（读密钥**方式**违规，diff-aware 检测新增+修改文件 added 行，不触存量基线）｜NO-SECRET-HARDCODE（密钥**值**硬编码，五格式扫描）｜secret_registry_consistency_gate（新增密钥"加 KEY→更 .env.example→更 registry"三步同步校验）。专用补充：zephyr_env_direct_access_gate（ZEPHYR_ENV 改 is_dev/is_prod canonical 入口，SECRETS.md Q&A）。
3. **post-commit 对账**：secret_registry_drift（gov_audit 包，registry↔.env↔era 三方漂移，warn 级，M3 04 §三）。
4. **生命周期面（SECRETS.md）**：三步新增流程＋轮换/era 语义（registry era 字段）＋8 服务文件分布（.env/.env.example/.env.postgres/.env.clickhouse 等）＋AI 冷启动可知性定位（"100% AI 开发场景"卷头）。
5. **关联执法件**：GATE-20（静态 AST 门拦裸调写码，M3 01 §二上游）＋运行时裸调拦截器（LLM 面，非密钥面）。

## 三、接线四态独立复核

- 总册判 **built（env 单因子信任绑定待裁）**：成立——通道/gate/对账三层全实存（542 行+两 gate priority+对账 reconciler 均实证）。
- 独立复核打折点（M3 04 §三矩阵）：**密钥面运行时侧=半真空**——"门+事后对账，无进程内拦截"（os.environ 读无 patch；drift 对账仅 post-commit warn）。与裸 duckdb T1（真空）、LLM T3（4 库覆盖）同谱系的纵深缺口。
- env 授权单因子信任（B5）：FORCE_DELETE/SERIALIZER_MODE/FAST_PATH 三授权 env 无身份绑定——总册"待裁"注记与 M3 01 B5 同源，其中 git_guard_bypass_reconciler 已兜事后对账一半。
- 误报出口健康：豁免清单明确（tests/模板/扫描脚本/docstring）＋Q&A 有 canonical 入口指引——fail-closed 未堵死合法场景。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| G1 | 运行时侧半真空（无 in-process 拦截/审计） | 平移 runtime_interceptor 模式做 audit-only 钩子入 5 既有安装点（M3 04 T2 修法，S-M 工作量） | P1 |
| G2 | env 授权单因子信任（FORCE_DELETE 等三 env） | Owner 裁定身份绑定或审计对账扩面（与 F104 G3 合并呈批） | P1 |
| G3 | NO-BARE-GETENV 只防新增、存量基线不收敛 | 存量清零排程（diff-aware 是务实起步，但需衰减曲线） | P2 |
| G4 | secret_registry era 轮换无自动化演练 | 轮换演练排程（破坏性操作走 Owner 门+三步验证） | P2 |

## 五、自审闸三态

**通道与 gate=挖干可施工**（542 行+priority+豁免+Q&A 全实证）；**运行时钩子=待施工**（G1 有平移范例）；**env 信任绑定=待裁**（Owner 门位）。

## 六、复跑命令

```bash
wc -l src/zephyr/shared/security/secrets.py                          # 542
grep -n "NO-BARE-GETENV\|NO-SECRET-HARDCODE\|consistency_gate" SECRETS.md | head -6
sed -n '99,107p' SECRETS.md                                           # 三道 gate 表
python -c "from zephyr.shared.security import secrets; print('import OK')"  # 通道可用性
grep -rn "secret_registry_drift" src/zephyr/gov_audit/ --include="*.py" -l    # 对账件
```
