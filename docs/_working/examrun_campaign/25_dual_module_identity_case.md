---
ttl: task_bound
title: 同一文件两个模块身份（zephyr.* 与 src.zephyr.*）——空 patch 隐患案卷（转判官域／维护线）
created: "2026-10-13"
sid: st-examrun-20261012
family_id: EXAMRUN-CAMPAIGN-20261012
---

# 一、现象（实测，一行可复算）

本仓 `src/` 目录在测试运行时位于 `sys.path` 上（`conftest`/`pytest` rootdir 注入），
于是同一个物理文件可以**以两个模块身份被导入**：

```
python -c "import importlib; a=importlib.import_module('zephyr.data.ch_writer');
           b=importlib.import_module('src.zephyr.data.ch_writer'); print(a is b, a.http_insert is b.http_insert)"
→ False False        # 同一文件 D:\ZephyrAlpha\src\zephyr\data\ch_writer.py，两个互不相干的模块对象
```

⇒ 对 `zephyr.data.ch_writer.http_insert` 的 patch **不会**影响 `src.zephyr.data.ch_writer.http_insert`，反之亦然。
命名空间包（`src/` 无 `__init__.py` 也能导入）是根因，不是配置意外。

# 二、影响面（本班尺，全量扫 `src`＋`scripts`＋`tests` 的 .py）

| 顶层目录 | 含 `import src.zephyr…` 的文件数 |
|---|---|
| `src/` | **0** |
| `scripts/` | **0** |
| `tests/` | **34**（全部落在 `tests/legacy_zephyr/**`） |

- 生产码与脚本面**只用一个身份**（`zephyr.*`），所以双身份目前只在遗留测试树里。
- 25 个 `tests/**/conftest.py` 里未出现对这些面的 `patch(...)`（自动 fixture 层不掺面）。
- **混面（导入一面、patch 另一面）当前实测 = 0**。

# 三、一次自我撤稿（诚实项，防后人照抄我的错）

本班初扫时用正则 `patch\(\s*["'](src\.)?zephyr` 把"patch 了生产面"的文件数算成 **2**
（`test_ch_writer.py`、`test_data_scheduler.py`）。逐行复核后**该数字作废**：
两文件都是 `from src.zephyr.data.…` ＋ `patch("src.zephyr.data.…")` **同面自洽**——
是我的正则把 `src.zephyr.` 也算进了"生产面"。修正后混面数＝**0**。
教训：判"混面"必须**两侧各自取面再求差集**，不能各用一个宽正则数命中（同族病见班账 §22.4／§25.9）。

# 四、危害模型（为什么现在 0 也要立项）

1. **空 patch＝真写生产库**：谁在 `tests/**` 里"导入 `zephyr.data.ch_writer`、却 patch `src.zephyr.data.ch_writer`"
   （或反向），mock 静默无效——`write_tsv("c1_market.kline_daily", …)`／`delete_where(...)` 会**打到真库**。
   遗留树里已有这种调用形（`tests/legacy_zephyr/data/test_ch_writer.py` 内**直调写口共 7 处**，
   行号 160／167／175／197／291／304 等，含 `write_tsv("c1_market.kline_daily", …)` 与
   `delete_where("c1_market.kline_daily", "date = '2026-07-05'")`），
   今天靠同面自洽才没出事 ⇒ **距离一次生产写事故只差一次复制粘贴**。
2. **模块级状态双份**：`_ch_lock`、HTTP host 失效位、连接/查询缓存、阈值常量各存一份 ⇒
   跨面调用时锁不互斥、失效位不共享，故障表现会"不可复现"。
3. 与本班 CH 破口同族：那次是"测试头自述 vs 真行为"，这次是"patch 面 vs 生效面"——**都是自述类安全声明不被验证**。

# 五、建议两道（归属：判官域／维护线，本班不代改）

- **甲（便宜、先上）静态 lint 或 commit 闸**：对 `tests/**` 逐文件取
  ①导入面集合（`from|import (src\.)?zephyr\.`）②`patch("…zephyr.*"` 的面集合，
  **两侧差集非空即红**；命中信息给出该文件的具体两面。零运行时成本，能挡住"复制粘贴引入混面"。
- **乙（治本）在 `tests/conftest.py` 做 collector-time 断言**：禁止生产包以 `src.` 前缀被导入
  （例如把 `src.zephyr` 加入导入黑名单或在收集阶段断言
  `not any(m.startswith("src.zephyr.") for m in sys.modules)`），
  让"第二个身份"根本无法出现 ⇒ 一旦混面即刻 ImportError 而非静默。
  注意：这会**打红 34 个遗留测试**（全在 `tests/legacy_zephyr/`），需配套一次性改面
  （`src.zephyr.` → `zephyr.`，属机械改名，但**属主是数据域遗留树**，须其班次做，勿由闸侧硬改）。
- 归档关联：与统筹指示的 **CH/PG 双库写口沙箱化**同族（都是"测试与生产共用同一入口而无人验证隔离"），
  建议同一批次实施，护栏一次到位。

# 六、验收法（给实施班）

1. 复算本件二/三节两张表（命令照抄即可）；
2. 甲闸上线后**反向自证**：造一个混面样本文件（一面导入、另一面 patch），闸必须红；
   再把样本改成同面，闸必须绿——不红即白；
3. 乙上线后再跑 `tests/legacy_zephyr/data/test_ch_writer.py` 全目录一次，
   跑前跑后各取 `system.query_log` 中 `c1_market.kline_daily` 的 INSERT/DELETE 计数，**必须都是 0**（这才算证伪"会写库"）。

出处：班账 `docs/_working/examrun_campaign/00_ledger.md` §卅四；
同族案卷 `docs/_working/examrun_campaign/22_landing_test_isolation_dossier.md`、名单 `23_ch_writing_test_nodeids.md`。

# 七、§三"混面 0"作废：精确尺抓到 2 个混面文件，其中 1 个是**现行空 patch**（03:0x 更正）

撤稿后再撤一次——本次是**我错在尺不够准**：§三用"逐文件两面各用一个宽正则数命中"的粗尺，
换成**按模块根（`src` vs 包内）对导入面与 patch 面做集合差**后，结果从 0 变成 **2**。

| 文件 | 导入面 | patch 面 | 定性 |
|---|---|---|---|
| `tests/legacy_zephyr/data/test_source_circuit_breaker.py` | 包内面（`from zephyr.data.scheduler import IntegratorScheduler`） | `BufferedWriter.add/flush` 打在 **`src.` 面**（296/297 行） | **现行空 patch**：被测真身持有的是包内面对象，桩未落在它身上；`BufferedWriter.flush()` 下游是 `ch_writer.write_tsv_outcome`（`buffered_writer.py:186`），该文件 fixture 配置目标表＝**生产表 `c1_market.kline_daily`**（254 行），且 `pyproject.toml:154` 的 `norecursedirs` **未排除** `tests/legacy_zephyr` ⇒ **在默认收集面内** |
| `tests/legacy_zephyr/data/test_ch_writer.py` | `src.` 面 | 2 处打在包内面（`zephyr.data.local_replay.save_fallback`） | **不构成生产写**：`ch_writer.py:902` 是**函数内** `from zephyr.data.local_replay import save_fallback`，调用时才解析到包内面 ⇒ 该 patch 恰好有效；属"两面在此处等效"的**假警报**，我在 §七 明标以免后人误读 §三 |

- **已证**：两面同存且不同模块对象（`a is b = False`、`http_insert` 不同体）；circuit_breaker 的桩打在非被测面上；
  该文件被默认收集；其目标表为生产表；`flush()` 下游函数确为 CH 写口。
- **未证**（不含糊）：这些用例真跑时是否**真的落了库**——取决于喂入 rows 是否非空、`http_insert` 是否在别处已被桩、
  列校验是否先失败。本班**不自行跑它做实验**（那正是今晚已罚过一次的动作类型）。
- **实施协议（统筹 03:1x 批准为协议）**：先上乙（conftest 禁 `src.` 面导入生产包，或先给 `ch_writer` 写口注入
  fail-closed 护栏）→ 再单跑该文件 → 跑前跑后各取 `system.query_log` 中 `c1_market.kline_daily` 的 INSERT 计数，
  **两侧都必为 0 才算证伪**；未做这一步之前，任何人不得用"它本来就该红/该写"来定性。
- **定级改**：混面闸 P2 → **P1 的一项**（现行空 patch ＋ 生产表目标 ＋ 默认收集面）；
  两案顺序不变（甲先行、乙随后），但乙的修点重点清单里**先做这 2 个文件**（`circuit_breaker` 优先），
  余下 32 个遗留文件按批改面。

# 八、判据脚本与反向自证（实施班可直接抄）

```python
IMP   = re.compile(r"^\s*(?:from|import)\s+((?:src\.)?zephyr(?:\.[a-zA-Z0-9_]+)*)", re.M)
PATCH = re.compile(r"""patch\(\s*["']((?:src\.)?zephyr(?:\.[a-zA-Z0-9_]+)*)\.""", re.M)
def roots(fs): return {"src" if f.startswith("src.") else "pkg" for f in fs}
# 判据：导入面根集合 与 patch 面根集合 不相等 ⇒ 混面（红）
```

- 全仓实跑（`src`＋`scripts`＋`tests`）：**扫描 4036 文件、用 `src.` 面者 34、混面 2**（即 §七 两个）。
- **反向自证**（样本造在仓外 `.runtime/tmp/.../mf_sample/`，绝不落进 `tests/`）：
  `evil_mixed.py`（导入 `src.` 面、patch 包内面）⇒ **被抓红**；
  `good_same.py`（两面同为包内面）⇒ **不报**；
  ⇒ 判据方向正确，甲闸上线后请以同样两件样本再验一次（红/绿各一，缺一即闸无效）。
