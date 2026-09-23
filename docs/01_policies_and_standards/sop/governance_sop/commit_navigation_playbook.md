---
ttl: permanent
title: "提交指路指南（机生版）"
doc_type: policy
---

# 提交指路指南（机生版）

> **本文件由生成器产出，禁手改**——改判据请改源头册后重跑生成器。
> 生成器: `python scripts/governance/generators/generate_commit_guide.py` ｜ 生成时刻: 2026-09-23 20:48 UTC
> 源册: gate_digest_registry.yaml（判据蒸馏）/ file_type_checklists_registry.yaml（类型清单）/ death_cases_registry.yaml（死因案例）/ in_process_gate_registry.yaml（在册台目）

锚点约定：gate 卡片标题=`### <GATE_ID>`，类型节=`## FT-<type_id>`；接口按子串检索。

## FT-universal — 每一笔提交的通用前置

1. 会话注册：session_worktree_start() 注册 session（SESSION-REQUIRED 硬拦未注册提交）
1. 改前 claim：lock_files.py acquire <file> <sid>；毕后 release（CLAIM-REQUIRED）
1. 隔离施工：worktree 内改（WORKTREE-REQUIRED：主区+他会话活跃=硬拦；降级直改=显式申请制）
1. 能力反查：写第一行业务代码前 capability_lookup.find()（CAPABILITY-LOOKUP-REQUIRED 查审计日志）
1. 施工登记：新 .py 模块先 apply_depgraph.py --add-design-node；完工 --transition-build-status production
1. 提交正门：python scripts/git_commit.py --session <sid> --files <清单>（禁裸 git commit；[GW:] 标记网关自动追加禁手写）
1. 锁忙改道：LOCK_TIMEOUT 自动入队；失败重试带 --adopt-prior-work；需要同步语义才 --no-auto-enqueue
1. 提交后核账：git log -1 --name-only 核实真实归属（暂存区可能吸收他会话内容）
1. worktree 施工注意假回执：worktree 内 --enqueue 落本区局部队列主带不排——用 --queue-root 主区 --worktree-root 本区；判据只认 git show HEAD:<file>

### SESSION-REQUIRED

- 强度: 硬阻断
- 触发面: 每次 commit
- 判据: session_id 非空且已注册（先 session_worktree_start()）
- 豁免: commit(allow_overlap=True)
- 处方: 会话启动第一步 session_worktree_start()；git_commit.py --session <sid>
- 判据源: `src/zephyr/gov_enforcement/commit_gates/session_required_gate.py`

### CLAIM-REQUIRED

- 强度: 硬阻断
- 触发面: commit 目标 files 清单
- 判据: session 已注册时目标文件必须在 held_files（先 claim 后改后提交）
- 豁免: allow_overlap=True；session 未注册放行（SESSION-REQUIRED 已拦）
- 处方: 提交前 lock_files.py acquire <file> <sid>（或 gateway claim_files）
- 判据源: `src/zephyr/gov_enforcement/commit_gates/claim_required_gate.py`

### WORKTREE-REQUIRED

- 强度: 硬阻断
- 触发面: 每次 commit
- 判据: 非 worktree+有其他活跃 session 即拦（共享区搭便车/黑洞风险）
- 豁免: worktree 内；solo；--allow-non-worktree；--allow-overlap
- 处方: session_worktree_start 隔离施工；逃生后改完即提交不留窗
- 判据源: `src/zephyr/gov_enforcement/commit_gates/worktree_required_gate.py`

### CAPABILITY-LOOKUP-REQUIRED

- 强度: 硬阻断
- 触发面: commit 含 src/zephyr/**.py 业务代码
- 判据: 本 session 审计日志须有 capability_lookup/rule_discovery 调用记录
- 豁免: message [no-lookup:<白名单 reason>]（gate-fix/continuation/mechanical 等 16 项；sweep 两封死因=reason 不在白名单）；env 紧急逃生
- 处方: 写码前 capability_lookup.find()（留审计）；纯机械批用白名单 reason 词；requeue 不改 message——死因是 message 类必须新 enqueue
- 判据源: `src/zephyr/gov_enforcement/commit_gates/capability_lookup_required_gate.py`

### DEPGRAPH-ENFORCEMENT

- 强度: 硬阻断
- 触发面: staged src/zephyr/**.py 带 [TTL] permanent（聚合台）
- 判据: build_status=planned 且实质行数超 50 即阻断（施工完成须转 production）；新文件无 depgraph 记录同拦
- 豁免: task_bound 临时件；DB 不可达 fail-open
- 处方: 先 apply_depgraph.py --add-design-node 登记，完工后 --transition-build-status <node> production
- 判据源: `src/zephyr/gov_enforcement/commit_gates/depgraph_pre_registration_gate.py`

### FORGED-GW-MARKER

- 强度: 硬阻断
- 触发面: commit message 含 [GW: 标记
- 判据: 存在非本 session 的 [GW: 标记=伪造/嫁祸，硬阻断；无标记放行（网关自动追加）
- 豁免: merge commit 的合并标记（session 已注册自然通过）
- 处方: 从 message 移除手写 [GW:] 片段——留痕标记由网关自动追加，永不手写
- 判据源: `src/zephyr/gov_enforcement/commit_gates/forged_gw_marker_gate.py`

### FOREIGN-CHANGE-DETECTION

- 强度: 硬阻断
- 触发面: 目标文件在 claim_files 时有基线快照且他会话 claim 痕迹存在
- 判据: 防搭便车提交他会话 WIP（FOREIGN_CHANGE）
- 豁免: allow_overlap=True；--adopt-prior-work 认领前序工作（失败重提必带，防 staged 差异判外来）
- 处方: 失败提交重试带 --adopt-prior-work；或 --allow-overlap
- 判据源: `src/zephyr/gov_enforcement/commit_gates/foreign_change_gate.py`

### HELD-OVERLAP

- 强度: 硬阻断
- 触发面: 提交目标文件被其他活跃 session 持有（SessionRegistry+.ailocks 双轨）
- 判据: 命中即阻断（搭便车防护）；Path.resolve 归一化比较
- 豁免: commit(allow_overlap=True)（CLI --allow-overlap），message 自动追加重叠标记
- 处方: 等锁释放；确需同窗走 --allow-overlap 逃生（留审计）
- 判据源: `src/zephyr/gov_enforcement/commit_gates/held_overlap_gate.py`

---

## FT-new_src_py — 新建 src/zephyr/ 生产模块

判定口诀: 路径 src/zephyr/** 且新文件且 .py

1. token 先行：batch_creation_tokens.py --prefix <模块目录> 登记（--merge-evaluation 带四判据一句话）；token 与内容同批原子或 token 批先落（队列 gate 读 HEAD，倒序必死）
1. 文件头 30 行 14 字段标注（[BLUEPRINT]/[MODULE]/[DOMAIN]/[DEPENDENCIES]/[CONSUMERS]/[STARTUP]/[MATURITY]/[INVARIANTS]/[MODIFY-GUARD]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]；__init__.py 最低 3 字段）
1. 翻译登记：add_module_translation.py --name-zh --plain-zh（大白话 ≥8 汉字禁模板话）
1. 新类名全仓唯一（同名加 # class-name-alias: <理由> 豁免）；禁纯 shim；禁 governance/ 根新增
1. 模块级可变容器写 Final（__all__: Final = [...]）；异常消息 ASCII 无句号、敏感值走 details
1. 时间一律 now_utc()/datetime.now(UTC)；subprocess 带 CREATE_NO_WINDOW（走 process_pool）；CH 查询走 ch_reader；SQL 提 _SQL_ 常量走 DatabaseService

**本类常见死因**（案例册全量见文末速查）:
- [CREATE-GUARD] 新文件无 token 直提 → 先登记 token 再写文件；登记时带 --merge-evaluation
- [TRANSLATION-COVERAGE] 翻译缺失/模板话（'提供包入口和模块加载功能'） → add_module_translation.py 一条命令；plain_zh 写人话 ≥8 汉字
- [ORPHAN-MODULE] 文件搬运+同批改引用被 ORPHAN/IMPORT 轮番拦死 → 三方（文件+import+名册）同批原子；或迁移延后另案（k4-0007 三连死实证）

### CREATE-GUARD

- 强度: 硬阻断
- 触发面: staged 新增的 .py/.yaml/.md/.sh/.ps1/.mmd/.json（非 tests/）
- 判据: 六道链——creation_token 精确路径匹配（7 格式）；merge_evaluation 缺失 warn；.py 头 30 行 14 字段（__init__ 3 字段）；governance/ 根禁新增；类名跨模块唯一；basename 碰撞（含未注册 basename 面）
- 豁免: tests/ 全豁免；rules/ .yaml 走命名检查不走 token；codegen（BEGIN CODEGEN）豁免字段头；类名豁免标记 class-name-alias
- 处方: 先 python scripts/governance/d3_metadata/batch_creation_tokens.py --prefix <目录> --created-by <sid> --capability <名> --merge-evaluation <四判据一句话> 登记，再写文件；token 与内容同批原子或 token 批先行（队列 gate 读 HEAD，倒序必死）
- 判据源: `src/zephyr/gov_enforcement/commit_gates/create_guard.py`

### TRANSLATION-COVERAGE

- 强度: 硬阻断
- 触发面: 新增 .py（src/zephyr/ 或 scripts/ 下）
- 判据: 翻译册须有合格条目——存在+非空+CJK 大于等于 8+非通用模板
- 豁免: tests/、demos/、test_ 前缀、*_test.py 后缀、__init__.py、_archive/
- 处方: python scripts/governance/d3_metadata/add_module_translation.py --path <file> --domain <D_*> --name-zh <中文名> --plain-zh <大白话至少 8 汉字>
- 判据源: `src/zephyr/gov_enforcement/commit_gates/translation_coverage_gate.py`

### ORPHAN-MODULE

- 强度: 硬阻断
- 触发面: staged 新增 src/ 下 .py
- 判据: git grep 限 src/**/*.py 面须有 import 引用（scripts/tests 引用不计入；防死代码 on creation）
- 豁免: __main__/__init__/main/conftest；scripts/、bin/ 路径；含 __main__ guard 块
- 处方: 引用方与模块同批；文件搬移+同批改引用形态注意 ORPHAN 门引用检测不含同批新 import 的结构性拦死（k4 三连死实证）——搬移要么三方（文件+import+名册）同批原子，要么延后另案
- 判据源: `src/zephyr/gov_enforcement/commit_gates/orphan_module_gate.py`

### IMPORT-INTEGRITY

- 强度: 硬阻断
- 触发面: 本 session staged .py 的绝对 import
- 判据: 悬空 import 硬阻断（zephyr/scripts 映射路径在 main HEAD+staged 找不到即拦）；撞墙成本次高（P50 148min）
- 豁免: sys.path 注入目录裸模块；相对 import/star import 跳过
- 处方: import 目标与 import 语句同 commit；他会话未 merge 先等或同批建目标模块
- 判据源: `src/zephyr/gov_enforcement/commit_gates/import_integrity_gate.py`

### COMPLEXITY-GUARD

- 强度: 硬阻断
- 触发面: staged .py 真正新增的函数（改签名已有函数不重罚）
- 判据: McCabe 超 15 阻断（5.158）
- 豁免: tests/；AST 失败 fail-open
- 处方: 拆短函数+回归；死信后先核 HEAD 现状再 requeue（入队快照陈旧会判旧单体——q-0005 实案）
- 判据源: `src/zephyr/gov_enforcement/commit_gates/high_complexity_gate.py`

### MUTABLE-CONST-WITHOUT-FINAL

- 强度: 硬阻断
- 触发面: src/zephyr/ .py 新增的模块级可变容器赋值（List/Dict/Set）
- 判据: 须 Final 标注（5.114）
- 豁免: AnnAssign；import/注释/docstring；行级 noqa n114-final
- 处方: 写法改 AnnAssign+Final（如 __all__ 加 Final 注解）；tuple 不检
- 判据源: `src/zephyr/gov_enforcement/commit_gates/mutable_const_without_final_gate.py`

### SSOT-REDEFINITION

- 强度: 硬阻断
- 触发面: staged .py 新增 class 或赋值且符号在 SSoT 清单
- 判据: 已 SSoT 化符号禁止重定义，必须 import/扩展
- 豁免: canonical 文件自身；tests/
- 处方: 查 capability_canonical_file_registry.yaml 找 canonical 文件后 import
- 判据源: `src/zephyr/gov_enforcement/commit_gates/ssot_redefinition_gate.py`

### CAPABILITY-OVERLAP

- 强度: 分级/条件
- 触发面: staged 新建 .py（own-scope）
- 判据: CloneGuard 语义克隆——extract 级（3+ 副本）硬阻断必须合并；review 级 warn
- 豁免: tests/；CloneGuard 不可用降级 warn；触碰税豁免（与 HEAD AST 等价不判本批）
- 处方: 扩展现有函数而非新建；写前预查 clone_guard.check_before_write，合理重复 resolve_finding 标 acknowledged
- 判据源: `src/zephyr/gov_enforcement/commit_gates/capability_overlap_gate.py`

### FILE-COPY

- 强度: 硬阻断
- 触发面: staged 新增 .py 与主仓已有同名 basename 文件比对
- 判据: AST 归一化相似度超 70% 阻断（裁定 221）
- 豁免: 只查新增
- 处方: 扩展现有文件而非复制；空 __init__.py 假阳性先例在案
- 判据源: `src/zephyr/gov_enforcement/commit_gates/file_copy_gate.py`

### FUNCTION-DUP

- 强度: 硬阻断
- 触发面: 新增 .py 顶层函数
- 判据: 同目录他文件同名同 body（去 docstring）阻断
- 豁免: 同名不同实现；类方法不查
- 处方: 扩展而非复制
- 判据源: `src/zephyr/gov_enforcement/commit_gates/function_dup_gate.py`

### MODULE-ID-CONSISTENCY

- 强度: 硬阻断
- 触发面: .py 含 CFG-/MOD-/PS- 三轨道声明头
- 判据: 三轨道 module_id 一致+count 派生匹配+跨文件唯一
- 豁免: none（fail-closed）
- 处方: 对齐三轨道声明；撞车 ID 改名
- 判据源: `src/zephyr/gov_enforcement/commit_gates/module_id_consistency_gate.py`

### BLUEPRINT-FORMAT

- 强度: 硬阻断
- 触发面: .py added 行 [BLUEPRINT] 头（无 tests/ 豁免）
- 判据: module_id 合规（裁定 208 双轨 MOD-/SH- 前缀+格式）；chainpile 盲发循环死因
- 豁免: 存量 grandfather（只检 added 行）
- 处方: 对照裁定 214/208 改 [BLUEPRINT] 头 module_id 格式后再发（盲发重发=白死三连实证）
- 判据源: `src/zephyr/gov_enforcement/commit_gates/blueprint_format_gate.py`

### BLUEPRINT-HEADER

- 强度: 硬阻断
- 触发面: .py added 行 [A_module] module_id 与 [BLUEPRINT] 头（聚合台含双头一致性）
- 判据: 禁 malformation（层码后下划线+小写）；同文件双头 normalize 后相等的不同拼写拦
- 豁免: tests/；docstring 行；行级 noqa blueprint-amodule-cross-check
- 处方: MOD-INF_a2a 改 MOD-INF-a2a（DASH 或大写）；双头统一拼写
- 判据源: `src/zephyr/gov_enforcement/commit_gates/blueprint_amodule_consistency_gate.py`

### GATE-DOMAIN-FK

- 强度: 硬阻断
- 触发面: .py added 行 [DOMAIN] D_XXX
- 判据: 域必须在 functional_domain_registry.yaml 在册
- 豁免: tests/；docstring 行
- 处方: 改已注册域或同 commit 新增域条目
- 判据源: `src/zephyr/gov_enforcement/commit_gates/domain_fk_gate.py`

### DEPGRAPH-ENFORCEMENT

- 强度: 硬阻断
- 触发面: staged src/zephyr/**.py 带 [TTL] permanent（聚合台）
- 判据: build_status=planned 且实质行数超 50 即阻断（施工完成须转 production）；新文件无 depgraph 记录同拦
- 豁免: task_bound 临时件；DB 不可达 fail-open
- 处方: 先 apply_depgraph.py --add-design-node 登记，完工后 --transition-build-status <node> production
- 判据源: `src/zephyr/gov_enforcement/commit_gates/depgraph_pre_registration_gate.py`

### PERMANENT-SYSTEM-TRIGGER

- 强度: 硬阻断
- 触发面: 新增 [TTL] permanent .py
- 判据: 禁 while True/time.sleep/schedule 时间触发，须事件订阅（永久系统四要素）
- 豁免: 只查新增；检测器自身 noqa m10-time-trigger
- 处方: 改 event_bus.subscribe 事件驱动；M11 豁免通道=permanent CLI runner 加 m11-perm-manual-legitimate 尾注
- 判据源: `src/zephyr/gov_enforcement/commit_gates/perm_trigger_gate.py`

### NO-IMPORT-SIDE-EFFECT

- 强度: 硬阻断
- 触发面: src/ .py 模块级语句
- 判据: 禁 import 期 I/O/网络/DB/急切实例化
- 豁免: __main__；main guard；TypeVar/NamedTuple/Enum/Path 纯构造
- 处方: 副作用移入函数或惰性工厂
- 判据源: `src/zephyr/gov_enforcement/commit_gates/no_import_side_effect_gate.py`

### SYNTAX-VALIDATION

- 强度: 硬阻断
- 触发面: 本 commit 清单全部 .py（含 tests/）
- 判据: ast.parse 全绿（全仓唯一语法硬拦真源）
- 豁免: 仅行级 syntax-fixture 豁免（marker 与理由间须 2+ 空格且理由至少 10 字符，测试夹具坏语法）
- 处方: 修语法错误；测试夹具用 syntax-fixture 豁免
- 判据源: `src/zephyr/gov_enforcement/commit_gates/syntax_validation_gate.py`

### NOQA-VALIDATION

- 强度: 硬阻断
- 触发面: 全部 staged .py 全文行
- 判据: 自定义 noqa 三查——非标准码须在 noqa_exempt_registry.yaml 登记；登记后须附至少 10 字符理由；单文件密度超 10 判滥用
- 豁免: ruff/flake8 标准码（E402 等）；存量 grandfather
- 处方: 先在 noqa_exempt_registry.yaml 登记 marker（理由至少 10 字），行内 marker 后直接附理由（两空格为登记约定非机器强制）
- 判据源: `src/zephyr/gov_enforcement/commit_gates/noqa_validation_gate.py`

### MSG-EXPOSURE

- 强度: 硬阻断
- 触发面: .py 异常消息 f-string 含敏感变量（路径/tx_id/凭据/连接串/SQL）
- 判据: 敏感值走结构化 details 字段
- 豁免: 行尾 noqa MSG-EXPOSURE（走 details 契约）
- 处方: raise XxxError(消息, details=字典)
- 判据源: `src/zephyr/gov_enforcement/commit_gates/msg_exposure_gate.py`

### MSG-STYLE

- 强度: 硬阻断
- 触发面: .py 异常消息字符串
- 判据: 禁 Unicode 箭头、禁中文句号结尾
- 豁免: 行级 noqa MSG-STYLE；tests/
- 处方: 统一 ASCII 箭头+无句号结尾
- 判据源: `src/zephyr/gov_enforcement/commit_gates/msg_style_gate.py`

---

## FT-new_script_py — 新建 scripts/ 治理/业务脚本

判定口诀: 路径 scripts/** 且新文件且 .py

1. token 先行（同 src 模块）；14 字段头照带
1. scripts/governance/** 须 from _shared.constants import <sym>（用了就显式 import）
1. manual CLI 永久脚本加 # noqa: m11-perm-manual-legitimate 尾注（M11 豁免通道）
1. 入口形态带 if __name__ == '__main__':（ORPHAN-MODULE 入口豁免面）
1. 翻译登记同 src（TRANSLATION-COVERAGE 照拦 scripts/ 新增）

**本类常见死因**（案例册全量见文末速查）:
- [PERMANENT-SYSTEM-TRIGGER] CLI runner 被判永久系统时间触发 → M11 豁免尾注 # noqa: m11-perm-manual-legitimate（manual CLI 合法先例）

### CREATE-GUARD

- 强度: 硬阻断
- 触发面: staged 新增的 .py/.yaml/.md/.sh/.ps1/.mmd/.json（非 tests/）
- 判据: 六道链——creation_token 精确路径匹配（7 格式）；merge_evaluation 缺失 warn；.py 头 30 行 14 字段（__init__ 3 字段）；governance/ 根禁新增；类名跨模块唯一；basename 碰撞（含未注册 basename 面）
- 豁免: tests/ 全豁免；rules/ .yaml 走命名检查不走 token；codegen（BEGIN CODEGEN）豁免字段头；类名豁免标记 class-name-alias
- 处方: 先 python scripts/governance/d3_metadata/batch_creation_tokens.py --prefix <目录> --created-by <sid> --capability <名> --merge-evaluation <四判据一句话> 登记，再写文件；token 与内容同批原子或 token 批先行（队列 gate 读 HEAD，倒序必死）
- 判据源: `src/zephyr/gov_enforcement/commit_gates/create_guard.py`

### TRANSLATION-COVERAGE

- 强度: 硬阻断
- 触发面: 新增 .py（src/zephyr/ 或 scripts/ 下）
- 判据: 翻译册须有合格条目——存在+非空+CJK 大于等于 8+非通用模板
- 豁免: tests/、demos/、test_ 前缀、*_test.py 后缀、__init__.py、_archive/
- 处方: python scripts/governance/d3_metadata/add_module_translation.py --path <file> --domain <D_*> --name-zh <中文名> --plain-zh <大白话至少 8 汉字>
- 判据源: `src/zephyr/gov_enforcement/commit_gates/translation_coverage_gate.py`

### SCRIPTS-IMPORT-INTEGRITY

- 强度: 硬阻断
- 触发面: 本 session staged scripts/governance/**.py
- 判据: 用了 _shared.constants 符号须显式 import
- 豁免: constants.py 自身；wildcard import 文件
- 处方: 顶部补 from _shared.constants import 符号
- 判据源: `src/zephyr/gov_enforcement/commit_gates/scripts_import_integrity_gate.py`

### UNDEFINED-NAME

- 强度: 硬阻断
- 触发面: scripts/governance/** 与 src/** .py
- 判据: F821 未定义符号 commit 时硬拦（--no-verify 绕不过）
- 豁免: wildcard import 文件跳过
- 处方: 补 import/修拼写/补本地定义
- 判据源: `src/zephyr/gov_enforcement/commit_gates/undefined_name_gate.py`

### PERMANENT-SYSTEM-TRIGGER

- 强度: 硬阻断
- 触发面: 新增 [TTL] permanent .py
- 判据: 禁 while True/time.sleep/schedule 时间触发，须事件订阅（永久系统四要素）
- 豁免: 只查新增；检测器自身 noqa m10-time-trigger
- 处方: 改 event_bus.subscribe 事件驱动；M11 豁免通道=permanent CLI runner 加 m11-perm-manual-legitimate 尾注
- 判据源: `src/zephyr/gov_enforcement/commit_gates/perm_trigger_gate.py`

### ORPHAN-MODULE

- 强度: 硬阻断
- 触发面: staged 新增 src/ 下 .py
- 判据: git grep 限 src/**/*.py 面须有 import 引用（scripts/tests 引用不计入；防死代码 on creation）
- 豁免: __main__/__init__/main/conftest；scripts/、bin/ 路径；含 __main__ guard 块
- 处方: 引用方与模块同批；文件搬移+同批改引用形态注意 ORPHAN 门引用检测不含同批新 import 的结构性拦死（k4 三连死实证）——搬移要么三方（文件+import+名册）同批原子，要么延后另案
- 判据源: `src/zephyr/gov_enforcement/commit_gates/orphan_module_gate.py`

### SYNTAX-VALIDATION

- 强度: 硬阻断
- 触发面: 本 commit 清单全部 .py（含 tests/）
- 判据: ast.parse 全绿（全仓唯一语法硬拦真源）
- 豁免: 仅行级 syntax-fixture 豁免（marker 与理由间须 2+ 空格且理由至少 10 字符，测试夹具坏语法）
- 处方: 修语法错误；测试夹具用 syntax-fixture 豁免
- 判据源: `src/zephyr/gov_enforcement/commit_gates/syntax_validation_gate.py`

---

## FT-new_test_py — 新建 tests/ 测试件

判定口诀: 路径 tests/** 且 .py

1. tests/ 全豁免 CREATE-GUARD token/翻译——直接写
1. 语法必须过（SYNTAX-VALIDATION 不豁免 tests/）；坏语法夹具用 # noqa: syntax-fixture  <理由≥10字符>
1. from zephyr.* import 的符号必须在源码实存（TEST-SOURCE-CONSISTENCY）
1. 禁写生产路径 data/ 业务目录——输出一律 tmp_path fixture（运维红线）

**本类常见死因**（案例册全量见文末速查）:
- [TEST-SOURCE-CONSISTENCY] 测试 import 源码不存在的符号 → import 实存符号；废弃测试 module-level pytest.skip

### SYNTAX-VALIDATION

- 强度: 硬阻断
- 触发面: 本 commit 清单全部 .py（含 tests/）
- 判据: ast.parse 全绿（全仓唯一语法硬拦真源）
- 豁免: 仅行级 syntax-fixture 豁免（marker 与理由间须 2+ 空格且理由至少 10 字符，测试夹具坏语法）
- 处方: 修语法错误；测试夹具用 syntax-fixture 豁免
- 判据源: `src/zephyr/gov_enforcement/commit_gates/syntax_validation_gate.py`

### TEST-SOURCE-CONSISTENCY

- 强度: 硬阻断
- 触发面: tests/ .py added 行 from zephyr import
- 判据: 符号必须在源码模块顶层实存（防测试漂移 ImportError）
- 豁免: pytest.skip module_level/importorskip 文件；外来 warn
- 处方: import 实存符号或源码补齐；废弃测试 module-level skip
- 判据源: `src/zephyr/gov_enforcement/commit_gates/test_source_consistency_gate.py`

### META-TESTS-COVERAGE

- 强度: 硬阻断
- 触发面: staged 触碰 commit_gates/*.py 时扫全目录
- 判据: 每台 gate 头部 [TESTS] 声明的测试文件必须实存（守卫者的守卫者）
- 豁免: [TESTS] 显式声明无；_ 前缀 helper
- 处方: 补测试文件或改 [TESTS] 豁免值
- 判据源: `src/zephyr/gov_enforcement/commit_gates/tests_coverage_gate.py`

---

## FT-working_md — 新建 docs/_working/ 工作文档（报告/台账/案卷）

判定口诀: 路径 docs/_working/** 且 .md

1. frontmatter 三件套：ttl: task_bound + title + session（TTL-METADATA fail-closed；禁 doc_type——EXEMPT-ZONE-FM 拦豁免区带 doc_type）
1. 目录用语义名禁 _NN 日期后缀（R5-DIGIT-SUFFIX 拦新引入目录：e2e_20260924 违规→e2e_integration 合法）
1. 扩展名只许 .csv/.html/.md/.yaml（DIRECTORY-CONTRACT；.meta.json 违规→改 .meta.yaml）
1. token 照登记（CREATE-GUARD 全 7 格式含 .md）
1. md 相对链接目标须实存（DOC-REF-BROKEN，草稿区 skip 面除外）
1. docs/_working 是 24h TTL 暂存面——成果要转正须 promote 到正式目录（FILE-PLACEMENT-TTL）

**本类常见死因**（案例册全量见文末速查）:
- [TTL-METADATA] frontmatter 缺 ttl 或用了废除值 7d/30d → ttl: task_bound（临时区）/permanent（永久区）二选一；禁旧值
- [R5-DIGIT-SUFFIX] 日期后缀目录被拦 → 案卷迁语义名目录；已落 HEAD 的老文件不受影响
- [DIRECTORY-CONTRACT] .meta.json 扩展名违规 → 改 .meta.yaml（内容同步转 YAML），消费侧同批改

### TTL-METADATA

- 强度: 硬阻断
- 触发面: commit 清单中 .md/.py/.sh/.ps1/.mmd/.yaml/.json（超 500 文件触发全量防 WinError 206）
- 判据: frontmatter ttl 必填且合法——v2 只剩 permanent/task_bound 两值；fail-closed
- 豁免: 豁免区/neutral 无 frontmatter 文件 PASS；temporary zone .md 有 frontmatter 跳 doc_type
- 处方: 永久区文件加 ttl permanent，临时区（docs/_working 等）加 ttl task_bound；ttl 词表仅 permanent/task_bound 两值，7d/30d/session 等不在词表；禁注释锚定自欺
- 判据源: `src/zephyr/gov_enforcement/commit_gates/ttl_gate.py`

### EXEMPT-ZONE-FM

- 强度: 硬阻断
- 触发面: 豁免区（docs/_working、_archive、.runtime、.trae、templates）.md/.yaml 带 doc_type frontmatter
- 判据: 本应正式目录的文件不得塞豁免区带 doc_type
- 豁免: HEAD 已存在的历史违规（允许维护）
- 处方: 去 doc_type 或迁正式目录；docs/_working 件用 ttl/title/session 三字段不带 doc_type
- 判据源: `src/zephyr/gov_enforcement/commit_gates/exempt_zone_frontmatter_gate.py`

### DIRECTORY-CONTRACT

- 强度: 硬阻断
- 触发面: 本次 commit 全部 files
- 判据: 目录契约 DCR-001~007（doc_type 目录归属/扩展名白黑名单/根目录白名单）；fail-closed
- 豁免: none
- 处方: 按目录契约放置/改名；docs/_working 只许 .csv/.html/.md/.yaml（.meta.json 违规改 .meta.yaml）
- 判据源: `src/zephyr/gov_enforcement/commit_gates/directory_contract_gate.py`

### R5-DIGIT-SUFFIX

- 强度: 硬阻断
- 触发面: 文件路径任意父级目录名匹配数字后缀（新引入才拦，历史不追溯）
- 判据: 禁 _NN 后缀目录（暗示多真源违 SSoT）；git ls-tree 失败 fail-closed 也拦
- 豁免: 已在 HEAD 的历史目录（progressive_convergence）；删除件
- 处方: 用语义名目录（e2e_20260924 违规、e2e_integration 合法；registry_incident 去 0b 后缀合法先例）
- 判据源: `src/zephyr/gov_enforcement/commit_gates/r5_digit_suffix_gate.py`

### CREATE-GUARD

- 强度: 硬阻断
- 触发面: staged 新增的 .py/.yaml/.md/.sh/.ps1/.mmd/.json（非 tests/）
- 判据: 六道链——creation_token 精确路径匹配（7 格式）；merge_evaluation 缺失 warn；.py 头 30 行 14 字段（__init__ 3 字段）；governance/ 根禁新增；类名跨模块唯一；basename 碰撞（含未注册 basename 面）
- 豁免: tests/ 全豁免；rules/ .yaml 走命名检查不走 token；codegen（BEGIN CODEGEN）豁免字段头；类名豁免标记 class-name-alias
- 处方: 先 python scripts/governance/d3_metadata/batch_creation_tokens.py --prefix <目录> --created-by <sid> --capability <名> --merge-evaluation <四判据一句话> 登记，再写文件；token 与内容同批原子或 token 批先行（队列 gate 读 HEAD，倒序必死）
- 判据源: `src/zephyr/gov_enforcement/commit_gates/create_guard.py`

### DOC-REF-BROKEN

- 强度: 硬阻断
- 触发面: 新增 .md 的相对链接
- 判据: 链接目标必须实存（git index 面）
- 豁免: 草稿区（docs/_working 等 skip 目录）；URL/锚点
- 处方: 目标文件同批创建或修相对路径
- 判据源: `src/zephyr/gov_enforcement/commit_gates/doc_ref_broken_gate.py`

### FILE-PLACEMENT-TTL

- 强度: 硬阻断
- 触发面: 全部 staged 非删除文件
- 判据: 永久区新文件需 allow_promote 准入；ttl 与 zone 一致性（permanent 在临时区/task_bound 在永久区均拦）；一级子目录须在 directory_zones 登记
- 豁免: 隐藏目录；changes/reports/delivery 过程性子目录
- 处方: 正式新文件走 promote 准入旗；临时件落 docs/_working/ 并带 task_bound
- 判据源: `src/zephyr/gov_enforcement/commit_gates/file_placement_ttl_gate.py`

---

## FT-formal_md — 新建正式 docs/** 文档（SOP/政策/规范）

判定口诀: 路径 docs/** 且非 _working/_archive 且 .md

1. frontmatter ttl: permanent + doc_type（正式区必带，TTL-METADATA --strict-doctype）
1. 永久区新文件需 promote 准入旗（FILE-PLACEMENT-TTL 规则 1）
1. 禁过渡文本（'曾用X现为Y'式表述——PURE-ASSERTION 直接写现值）
1. #ARCH-NNN 引用必须先在 architecture_issue_registry.yaml 登记（同批）；AGENTS.md §章节号须实存（REFERENCE-INTEGRITY）
1. token 照登记
1. ruling_*.md 专项：裁定号先登记 ruling_registry 且与文档同 commit 原子（RULE-RULING）；文档里声明的 commit hash 必须已落地本仓（RULING-COMMIT-VERIFIED）

**本类常见死因**（案例册全量见文末速查）:
- [REFERENCE-INTEGRITY] 引用 #ARCH-XXX 未在册编号 → 先登记 architecture_issue_registry.yaml 再引用，同批原子

### TTL-METADATA

- 强度: 硬阻断
- 触发面: commit 清单中 .md/.py/.sh/.ps1/.mmd/.yaml/.json（超 500 文件触发全量防 WinError 206）
- 判据: frontmatter ttl 必填且合法——v2 只剩 permanent/task_bound 两值；fail-closed
- 豁免: 豁免区/neutral 无 frontmatter 文件 PASS；temporary zone .md 有 frontmatter 跳 doc_type
- 处方: 永久区文件加 ttl permanent，临时区（docs/_working 等）加 ttl task_bound；ttl 词表仅 permanent/task_bound 两值，7d/30d/session 等不在词表；禁注释锚定自欺
- 判据源: `src/zephyr/gov_enforcement/commit_gates/ttl_gate.py`

### FILE-PLACEMENT-TTL

- 强度: 硬阻断
- 触发面: 全部 staged 非删除文件
- 判据: 永久区新文件需 allow_promote 准入；ttl 与 zone 一致性（permanent 在临时区/task_bound 在永久区均拦）；一级子目录须在 directory_zones 登记
- 豁免: 隐藏目录；changes/reports/delivery 过程性子目录
- 处方: 正式新文件走 promote 准入旗；临时件落 docs/_working/ 并带 task_bound
- 判据源: `src/zephyr/gov_enforcement/commit_gates/file_placement_ttl_gate.py`

### PURE-ASSERTION

- 强度: 硬阻断
- 触发面: 本 session staged .md added 行
- 判据: 禁过渡文本（曾用 X 现为 Y 式表述）——直接写当前值
- 豁免: checker 环境异常 fail-open；外来 staged warn
- 处方: 删过渡表述写现值
- 判据源: `src/zephyr/gov_enforcement/commit_gates/pure_assertion_gate.py`

### REFERENCE-INTEGRITY

- 强度: 硬阻断
- 触发面: staged 新增文本中的三类引用——#ARCH-NNN、AGENTS.md 章节号、ruling 文档里的 commit hash 声明（聚合台）
- 判据: 新增 #ARCH- 引用须在 architecture_issue_registry.yaml 在册且同 commit（禁 grep-and-claim 占位）；AGENTS.md 章节号须实存；声明已完成 commit 的 hash 须 git cat-file -e 实存
- 豁免: tests/；存量悬空不追溯；模板占位符；message [no-verify-ruling:reason]
- 处方: 补登 architecture_issue_registry.yaml（与引用同批）或删引用；核对 AGENTS.md 章节号；核对 hash 拼写与是否已合并
- 判据源: `src/zephyr/gov_enforcement/commit_gates/dangling_reference_gate.py`

### CREATE-GUARD

- 强度: 硬阻断
- 触发面: staged 新增的 .py/.yaml/.md/.sh/.ps1/.mmd/.json（非 tests/）
- 判据: 六道链——creation_token 精确路径匹配（7 格式）；merge_evaluation 缺失 warn；.py 头 30 行 14 字段（__init__ 3 字段）；governance/ 根禁新增；类名跨模块唯一；basename 碰撞（含未注册 basename 面）
- 豁免: tests/ 全豁免；rules/ .yaml 走命名检查不走 token；codegen（BEGIN CODEGEN）豁免字段头；类名豁免标记 class-name-alias
- 处方: 先 python scripts/governance/d3_metadata/batch_creation_tokens.py --prefix <目录> --created-by <sid> --capability <名> --merge-evaluation <四判据一句话> 登记，再写文件；token 与内容同批原子或 token 批先行（队列 gate 读 HEAD，倒序必死）
- 判据源: `src/zephyr/gov_enforcement/commit_gates/create_guard.py`

### FOLDER-CAPACITY-HARD-LIMIT

- 强度: 硬阻断
- 触发面: staged .py/.yaml/.md 所在目录
- 判据: 目录平铺文件数（不含子目录/__init__）超 120 阻断
- 豁免: tests/
- 处方: 拆子目录；注意主区盘与工棚面不同口径（nightfix 121 实案=数主区盘平铺 .py）
- 判据源: `src/zephyr/gov_enforcement/commit_gates/folder_capacity_hard_limit_gate.py`

---

## FT-registry_yaml — 注册表 YAML（docs/.../_registry/catalogs/）

判定口诀: 路径含 _registry/catalogs/ 且 .yaml

1. 共享热册必走 safe_write_text CAS（禁裸 Edit/Write 后不复核）；写后进程外复核
1. 纯插入；条目插既有根键列表尾（capability 册 token 插 creation_tokens 尾、di_seam_exemptions 行之前）
1. 插后本地 yaml.safe_load 预验（REGISTRY-YAML-PARSE fail-closed 无逃生）
1. 净删/条目减少/身份消失任一信号触发 REGISTRY-MASS-DELETION——合法重排须 message [allow-mass-deletion:<理由≥10字>]
1. 批量补登走 scripts/governance/registry_batch_edit.py；token 批量走 batch_creation_tokens.py（守恒闸防吃他会话刚落地条目）
1. tags 只选词不造词（TAG-VOCAB）；资产登记带 name_zh+plain_zh 血肉（BLOOD-FLESH）

**本类常见死因**（案例册全量见文末速查）:
- [REGISTRY-MASS-DELETION] 整文件快照压盘（陈旧基底覆写他会话刚落地条目） → 热文件 safe_write_text+expected_base_sha256；写前守恒闸拒写即停，勿强行重写
- [REGISTRY-YAML-PARSE] 三向合并失败/快照撕裂死信 → 解析护栏（yaml.safe_load 预验）过了再入队；同族多条插入注意合并器同点插入语义

### REGISTRY-MASS-DELETION

- 强度: 硬阻断
- 触发面: staged YAML 命中 _registry/catalogs/ 或 ROOR
- 判据: 三信号任一拦——净删行/条目数减少/条目身份消失（防删 16 插 25 代数抵消）
- 豁免: message [allow-mass-deletion:<理由至少 10 字>]（合法重排/整文件重生成；放行仍审计）
- 处方: 批量补登走 scripts/governance/registry_batch_edit.py 纯插入；共享热册 CAS 写（safe_write_text）+写前守恒闸；共享暂存区副本陈旧会误报——git add 自愈
- 判据源: `src/zephyr/gov_enforcement/commit_gates/registry_mass_deletion_gate.py`

### REGISTRY-YAML-PARSE

- 强度: 硬阻断
- 触发面: staged capability_canonical_file_registry.yaml / data_asset_registry.yaml
- 判据: safe_load 过+顶层根键唯一+capability 档 di_seam_exemptions 末位键+creation_tokens 为 list；fail-closed 无逃生
- 豁免: none
- 处方: token 条目插 creation_tokens 列表尾（di_seam_exemptions 行之前，注意嵌套同名键勿错插）；插后本地 yaml.safe_load 预验再提交
- 判据源: `src/zephyr/gov_enforcement/commit_gates/registry_yaml_parse_gate.py`

### TAG-VOCAB

- 强度: warn-only
- 触发面: catalogs/ yaml 的 tags 列表
- 判据: tags 只选词不造词（别名可解析）；warn 期
- 豁免: 别名解析合法
- 处方: 改标准词或先收编 library_tag_vocabulary.yaml
- 判据源: `src/zephyr/gov_enforcement/commit_gates/library/tag_vocab_gate.py`

### BLOOD-FLESH

- 强度: warn-only
- 触发面: 新增 .py 翻译条目 A 面/翻译册新增条目 B 面
- 判据: 新资产登记必填血肉——A 面 name_zh；B 面 name_zh+plain_zh 双全非模板
- 豁免: 存量不追溯；翻译册损坏 fail-open
- 处方: add_module_translation.py 一条命令（同 TRANSLATION-COVERAGE）
- 判据源: `src/zephyr/gov_enforcement/commit_gates/library/library_blood_flesh_gate.py`

### HOT-FILE-BASE-FRESHNESS

- 强度: 硬阻断
- 触发面: 热文件（注册表/宪法/tracker）+有 claim_head 锚点
- 判据: claim 后 HEAD 上游改过该热文件即拦陈旧快照覆写（STALE_BASE）
- 豁免: allow_overlap；无 claim_head
- 处方: git log -p 区间核对上游改动；已含则 release 后重 claim（锚刷新）再提交；claim_snapshots 删快照刷锚配方在案
- 判据源: `src/zephyr/gov_enforcement/commit_gates/hot_file_base_freshness_gate.py`

### CREATE-GUARD

- 强度: 硬阻断
- 触发面: staged 新增的 .py/.yaml/.md/.sh/.ps1/.mmd/.json（非 tests/）
- 判据: 六道链——creation_token 精确路径匹配（7 格式）；merge_evaluation 缺失 warn；.py 头 30 行 14 字段（__init__ 3 字段）；governance/ 根禁新增；类名跨模块唯一；basename 碰撞（含未注册 basename 面）
- 豁免: tests/ 全豁免；rules/ .yaml 走命名检查不走 token；codegen（BEGIN CODEGEN）豁免字段头；类名豁免标记 class-name-alias
- 处方: 先 python scripts/governance/d3_metadata/batch_creation_tokens.py --prefix <目录> --created-by <sid> --capability <名> --merge-evaluation <四判据一句话> 登记，再写文件；token 与内容同批原子或 token 批先行（队列 gate 读 HEAD，倒序必死）
- 判据源: `src/zephyr/gov_enforcement/commit_gates/create_guard.py`

---

## FT-config_yaml — 非 rules 配置 YAML（config/ data/ schemas/ 及 docs/_working 的 .yaml/.yml）

判定口诀: .yaml 或 .yml 且新文件且非 _registry/catalogs 且非 rules/

1. token 照登记（非 rules .yaml 无 token 硬拦——YAML 是配置真源，第二真源危害最大；注：.yml 后缀当前不在 CREATE-GUARD 机器强制面，按同标准自律防扩面）
1. frontmatter ttl 按区：config/ 永久区=permanent；docs/_working 下 .yaml/.yml 一律 task_bound（FILE-PLACEMENT-TTL 拦错区）
1. 表名走 TableRegistry；词表值走加载器禁硬编码

### CREATE-GUARD

- 强度: 硬阻断
- 触发面: staged 新增的 .py/.yaml/.md/.sh/.ps1/.mmd/.json（非 tests/）
- 判据: 六道链——creation_token 精确路径匹配（7 格式）；merge_evaluation 缺失 warn；.py 头 30 行 14 字段（__init__ 3 字段）；governance/ 根禁新增；类名跨模块唯一；basename 碰撞（含未注册 basename 面）
- 豁免: tests/ 全豁免；rules/ .yaml 走命名检查不走 token；codegen（BEGIN CODEGEN）豁免字段头；类名豁免标记 class-name-alias
- 处方: 先 python scripts/governance/d3_metadata/batch_creation_tokens.py --prefix <目录> --created-by <sid> --capability <名> --merge-evaluation <四判据一句话> 登记，再写文件；token 与内容同批原子或 token 批先行（队列 gate 读 HEAD，倒序必死）
- 判据源: `src/zephyr/gov_enforcement/commit_gates/create_guard.py`

### TTL-METADATA

- 强度: 硬阻断
- 触发面: commit 清单中 .md/.py/.sh/.ps1/.mmd/.yaml/.json（超 500 文件触发全量防 WinError 206）
- 判据: frontmatter ttl 必填且合法——v2 只剩 permanent/task_bound 两值；fail-closed
- 豁免: 豁免区/neutral 无 frontmatter 文件 PASS；temporary zone .md 有 frontmatter 跳 doc_type
- 处方: 永久区文件加 ttl permanent，临时区（docs/_working 等）加 ttl task_bound；ttl 词表仅 permanent/task_bound 两值，7d/30d/session 等不在词表；禁注释锚定自欺
- 判据源: `src/zephyr/gov_enforcement/commit_gates/ttl_gate.py`

### TABLE-NAME-REGISTRY

- 强度: 硬阻断
- 触发面: .py added 行硬编码表名字符串
- 判据: 走 TableRegistry.table(category_id) 真源
- 豁免: tests/；table_registry 自身；docstring
- 处方: 常量替换为 TableRegistry 引用；与 NO-BARE-SQL 判据不同（行级正则 vs AST）勿混淆豁免方式
- 判据源: `src/zephyr/gov_enforcement/commit_gates/table_name_registry_gate.py`

### GATE-VOCAB

- 强度: 硬阻断
- 触发面: 新增 .py 硬编码词表合法值
- 判据: 词表值从词表 YAML/加载器读取
- 豁免: tests/；只查新增
- 处方: 按 check_vocab_hardcode.py 输出改加载器读取
- 判据源: `src/zephyr/gov_enforcement/commit_gates/vocab_hardcode_gate.py`

---

## FT-rules_yaml — 规则 YAML（docs/01_policies_and_standards/rules/trae_*.yaml）

判定口诀: 路径 docs/01_policies_and_standards/rules/ 且 .yaml

1. 命名铁律 trae_NNN_<主题>_<描述>.yaml（主题段必须含下划线；非 trae 命名/单段 name 硬拦）
1. enforcement.paired_gate_id 必填（null=文档型；值须 gate_registry 在册）
1. 四方式对齐：YAML↔Catalog↔Disk↔Code 同步改
1. scaffold 正门：python scripts/scaffold.py rule <主题_描述>
1. rules/ .yaml 不走 CREATE-GUARD token（走命名检查）；rules/*.yaml 双层保护死路勿闯（勿想给 rules yaml 登 token 绕命名）

**本类常见死因**（案例册全量见文末速查）:
- [RULE-EXECUTION-PAIRING] paired_gate_id 悬空（指向未注册 gate） → 挂真 gate_id 或显式 null

### RULE-EXECUTION-PAIRING

- 强度: 硬阻断
- 触发面: rules/trae_*.yaml 变更或 message 含 [rule-mod]
- 判据: 每规则 YAML 须有 enforcement.paired_gate_id（null 允许=文档型；值须 gate_registry 在册）
- 豁免: message [no-pairing:reason]；paired_gate_id null
- 处方: enforcement 段补 paired_gate_id（挂真 gate 或 null）
- 判据源: `src/zephyr/gov_enforcement/commit_gates/rule_execution_pairing_gate.py`

### RULE-FOUR-WAY-ALIGN

- 强度: 硬阻断
- 触发面: staged 规则文件或 rule_catalog_registry
- 判据: YAML/Catalog/Disk/Code 四方一致
- 豁免: tests/
- 处方: 改 YAML 后同步 catalog/disk/code 引用
- 判据源: `src/zephyr/gov_enforcement/commit_gates/rule_four_way_alignment_gate.py`

### EXEMPT-ZONE-FM

- 强度: 硬阻断
- 触发面: 豁免区（docs/_working、_archive、.runtime、.trae、templates）.md/.yaml 带 doc_type frontmatter
- 判据: 本应正式目录的文件不得塞豁免区带 doc_type
- 豁免: HEAD 已存在的历史违规（允许维护）
- 处方: 去 doc_type 或迁正式目录；docs/_working 件用 ttl/title/session 三字段不带 doc_type
- 判据源: `src/zephyr/gov_enforcement/commit_gates/exempt_zone_frontmatter_gate.py`

---

## FT-rename_move — 文件改名/搬移

判定口诀: git diff --diff-filter=R 或同批 A+D 对

1. git mv 后 commit 前 MUST generate_project_depgraph.py --force 重建（RENAME-DEPGRAPH-SYNC 硬拦）
1. 三方同批原子：文件+引用方 import+名册 module_path 同一批（否则 ORPHAN/IMPORT/名册三方分裂轮番拦死——k4 三连死+lane0b-0017 死锁实证）
1. 改名后注册表条目 code_path/code_symbol 同步（REGISTRY-CODE-ANCHOR 反查）
1. rules/ .yaml rename 也拦命名违规（--diff-filter=R 检测新名）

**本类常见死因**（案例册全量见文末速查）:
- [ORPHAN-MODULE] 搬家批死于 ORPHAN（HEAD 引用方还指旧路径），改引用批死于 IMPORT（新路径不存在）——互为前置死锁 → 合一批原子落地（8 文件合一批先例）；或反方案三方全回原位零新文件

### ORPHAN-MODULE

- 强度: 硬阻断
- 触发面: staged 新增 src/ 下 .py
- 判据: git grep 限 src/**/*.py 面须有 import 引用（scripts/tests 引用不计入；防死代码 on creation）
- 豁免: __main__/__init__/main/conftest；scripts/、bin/ 路径；含 __main__ guard 块
- 处方: 引用方与模块同批；文件搬移+同批改引用形态注意 ORPHAN 门引用检测不含同批新 import 的结构性拦死（k4 三连死实证）——搬移要么三方（文件+import+名册）同批原子，要么延后另案
- 判据源: `src/zephyr/gov_enforcement/commit_gates/orphan_module_gate.py`

### IMPORT-INTEGRITY

- 强度: 硬阻断
- 触发面: 本 session staged .py 的绝对 import
- 判据: 悬空 import 硬阻断（zephyr/scripts 映射路径在 main HEAD+staged 找不到即拦）；撞墙成本次高（P50 148min）
- 豁免: sys.path 注入目录裸模块；相对 import/star import 跳过
- 处方: import 目标与 import 语句同 commit；他会话未 merge 先等或同批建目标模块
- 判据源: `src/zephyr/gov_enforcement/commit_gates/import_integrity_gate.py`

### REGISTRY-CODE-ANCHOR

- 强度: 硬阻断
- 触发面: staged 命中 15 业务注册表或 src/ .py 删除/改名
- 判据: 库条目 code_path/code_symbol 引用的代码不得悬空（防锚点漂移）
- 豁免: deprecated/retired 条目
- 处方: 同步改条目或标 deprecated
- 判据源: `src/zephyr/gov_enforcement/commit_gates/registry_code_anchor_gate.py`

### DEPGRAPH-FRESHNESS

- 强度: 分级/条件
- 触发面: always-on 每次 commit
- 判据: depgraph 扫描缓存超 30min warn、超 24h 硬阻断（防在过期快照上设计）
- 豁免: 缓存缺失 fail-open；PG 离线探针证实超 24h 留痕豁免
- 处方: python scripts/governance/generate_project_depgraph.py 刷新后再提交
- 判据源: `src/zephyr/gov_enforcement/commit_gates/depgraph_freshness_gate.py`

### DERIVED-FILE-DELETION-PROTECTION

- 强度: 硬阻断
- 触发面: staged 删除清单命中受保护派生文件（blueprint_registry.yaml 等）
- 判据: 派生文件删除致 20+ 消费方静默降级，硬阻断
- 豁免: --allow-derived-deletion 逃生（显式声明+留痕）
- 处方: 跑 sync_registry_from_blueprints.py --write 恢复派生文件；确需删走逃生通道
- 判据源: `src/zephyr/gov_enforcement/commit_gates/derived_file_deletion_gate.py`

---

## FT-deletion_batch — 删除批/退役批

判定口诀: git diff --diff-filter=D

1. 派生文件删除被拦——先跑 sync 真源脚本或 --allow-derived-deletion
1. 注册表净删走 [allow-mass-deletion:<理由≥10字>]
1. 退役批注意时序毒窗：主区文件删了、退役注册表批未落地的窗口内一切 landing fail-closed（gslim P3 实证）——文件+注册表+测试单批原子，或先 enabled:false 软开关
1. 反查 code_path 引用（REGISTRY-CODE-ANCHOR）；dangling 引用先清

**本类常见死因**（案例册全量见文末速查）:
- [RECONCILER-HEALTH] 退役半落地窗内他会话全量死信（LandingEnvironmentError） → 退役=单批原子或软开关先行；窗口期施工旗让队列暂停该类落地（立法提案在案）

### DERIVED-FILE-DELETION-PROTECTION

- 强度: 硬阻断
- 触发面: staged 删除清单命中受保护派生文件（blueprint_registry.yaml 等）
- 判据: 派生文件删除致 20+ 消费方静默降级，硬阻断
- 豁免: --allow-derived-deletion 逃生（显式声明+留痕）
- 处方: 跑 sync_registry_from_blueprints.py --write 恢复派生文件；确需删走逃生通道
- 判据源: `src/zephyr/gov_enforcement/commit_gates/derived_file_deletion_gate.py`

### REGISTRY-MASS-DELETION

- 强度: 硬阻断
- 触发面: staged YAML 命中 _registry/catalogs/ 或 ROOR
- 判据: 三信号任一拦——净删行/条目数减少/条目身份消失（防删 16 插 25 代数抵消）
- 豁免: message [allow-mass-deletion:<理由至少 10 字>]（合法重排/整文件重生成；放行仍审计）
- 处方: 批量补登走 scripts/governance/registry_batch_edit.py 纯插入；共享热册 CAS 写（safe_write_text）+写前守恒闸；共享暂存区副本陈旧会误报——git add 自愈
- 判据源: `src/zephyr/gov_enforcement/commit_gates/registry_mass_deletion_gate.py`

### REGISTRY-CODE-ANCHOR

- 强度: 硬阻断
- 触发面: staged 命中 15 业务注册表或 src/ .py 删除/改名
- 判据: 库条目 code_path/code_symbol 引用的代码不得悬空（防锚点漂移）
- 豁免: deprecated/retired 条目
- 处方: 同步改条目或标 deprecated
- 判据源: `src/zephyr/gov_enforcement/commit_gates/registry_code_anchor_gate.py`

### REFERENCE-INTEGRITY

- 强度: 硬阻断
- 触发面: staged 新增文本中的三类引用——#ARCH-NNN、AGENTS.md 章节号、ruling 文档里的 commit hash 声明（聚合台）
- 判据: 新增 #ARCH- 引用须在 architecture_issue_registry.yaml 在册且同 commit（禁 grep-and-claim 占位）；AGENTS.md 章节号须实存；声明已完成 commit 的 hash 须 git cat-file -e 实存
- 豁免: tests/；存量悬空不追溯；模板占位符；message [no-verify-ruling:reason]
- 处方: 补登 architecture_issue_registry.yaml（与引用同批）或删引用；核对 AGENTS.md 章节号；核对 hash 拼写与是否已合并
- 判据源: `src/zephyr/gov_enforcement/commit_gates/dangling_reference_gate.py`

---

## FT-migration_batch — 迁移/DDL/数据批

判定口诀: apply_*.py / DDL / 数据回填批

1. 新 schema 表 15 字段头 + DateTime64(3) 显式时区（RULE-SCHEMA-TZ）
1. ReplacingMergeTree version 列用 ingest_ts；查询走 ch_reader FINAL；写入走 BufferedWriter
1. 表名注册 business_data_categories.yaml（SCHEMA-FILE-EXISTS 校验 schema_file 实存）
1. 破坏性 DB 操作三步验证（必要性/真实性/可逆性）+判重用 check_tick_duplication.py
1. 错误码按 detail 提示的下一可用号 ZA-<前缀>-N 登记

### CH-VERSION-COL

- 强度: 硬阻断
- 触发面: 新增行含 ReplacingMergeTree 带非时间列
- 判据: version 列禁布尔/状态列（blocked 集合）
- 豁免: tests/
- 处方: 用 ingest_ts DateTime DEFAULT now()
- 判据源: `src/zephyr/gov_enforcement/commit_gates/ch_version_col_gate.py`

### CH-FINAL-GATE

- 强度: 硬阻断
- 触发面: .py 直调 ch_writer.query 或硬编码 ReplacingMergeTree 查询
- 判据: CH 查询走 ch_reader.query 自动 FINAL
- 豁免: ch_reader/ch_writer 自身；DDL 部署脚本；tests/
- 处方: ch_writer.query 改 ch_reader.query
- 判据源: `src/zephyr/gov_enforcement/commit_gates/ch_final_gate.py`

### CH-BATCH-SIZE

- 强度: 硬阻断
- 触发面: .py added 行循环体内 write_result
- 判据: 禁逐条写 CH，走 BufferedWriter
- 豁免: ch_writer/buffered_writer 自身；tests/
- 处方: writer.add 循环+flush
- 判据源: `src/zephyr/gov_enforcement/commit_gates/ch_batch_size_gate.py`

### SCHEMA-FILE-EXISTS

- 强度: 硬阻断
- 触发面: staged business_data_categories.yaml
- 判据: schema_file 引用实存（只拦本次新增悬空）
- 豁免: schema_file null
- 处方: schema 文件同批 git add 或修路径
- 判据源: `src/zephyr/gov_enforcement/commit_gates/schema_file_exists_gate.py`

### GATE-ERRCODE-CONSISTENCY

- 强度: 硬阻断
- 触发面: staged src/**.py 或 error_code_registry.yaml
- 判据: 注册表与代码六断言对账（只拦本次新增，存量 warn 归属责任人）
- 豁免: 存量违规；SSoT 缺失 fail-closed
- 处方: 按 detail 内下一可用号（ZA-前缀-N）取号登记
- 判据源: `src/zephyr/gov_enforcement/commit_gates/errcode_consistency_gate.py`

### TABLE-NAME-REGISTRY

- 强度: 硬阻断
- 触发面: .py added 行硬编码表名字符串
- 判据: 走 TableRegistry.table(category_id) 真源
- 豁免: tests/；table_registry 自身；docstring
- 处方: 常量替换为 TableRegistry 引用；与 NO-BARE-SQL 判据不同（行级正则 vs AST）勿混淆豁免方式
- 判据源: `src/zephyr/gov_enforcement/commit_gates/table_name_registry_gate.py`

### BUSINESS-REGISTRY

- 强度: 硬阻断
- 触发面: staged 命中 19 文件/21 段业务资产库
- 判据: 条目 id 唯一+module_id 必填 MOD- 格式且在 depgraph 实存
- 豁免: PG 不可达跳过存在性子检查；空库放行
- 处方: 先 apply_depgraph 登记 blueprint 再入库
- 判据源: `src/zephyr/gov_enforcement/commit_gates/business_registry_gate.py`

---

## FT-ps1 — PowerShell 脚本（.ps1）

判定口诀: .ps1 文件

1. 纯 ASCII（PS5.1 无 BOM 按 GBK 解码，中文注释=假语法错误）——注释写英文
1. 原生重定向用 cmd /c 形态（PS5.1 stderr NativeCommandError 釜底抽薪）
1. token 照登记（7 格式含 .ps1）

### ENCODING-SAFETY

- 强度: 硬阻断
- 触发面: .py/.md/.yaml/.yml/.json/.toml/.ps1
- 判据: 去 BOM/无乱码/LF 行尾/.ps1 纯 ASCII（PS5.1 GBK 假语法错误）
- 豁免: 环境异常 fail-open
- 处方: .ps1 注释写英文；全仓 LF；中文内容只进 UTF-8 文本格式
- 判据源: `src/zephyr/gov_enforcement/commit_gates/encoding_gate.py`

### CREATE-GUARD

- 强度: 硬阻断
- 触发面: staged 新增的 .py/.yaml/.md/.sh/.ps1/.mmd/.json（非 tests/）
- 判据: 六道链——creation_token 精确路径匹配（7 格式）；merge_evaluation 缺失 warn；.py 头 30 行 14 字段（__init__ 3 字段）；governance/ 根禁新增；类名跨模块唯一；basename 碰撞（含未注册 basename 面）
- 豁免: tests/ 全豁免；rules/ .yaml 走命名检查不走 token；codegen（BEGIN CODEGEN）豁免字段头；类名豁免标记 class-name-alias
- 处方: 先 python scripts/governance/d3_metadata/batch_creation_tokens.py --prefix <目录> --created-by <sid> --capability <名> --merge-evaluation <四判据一句话> 登记，再写文件；token 与内容同批原子或 token 批先行（队列 gate 读 HEAD，倒序必死）
- 判据源: `src/zephyr/gov_enforcement/commit_gates/create_guard.py`

---

## FT-other_new_asset — 其他新建资产（.json/.sh/.mmd）

判定口诀: 新文件且扩展名为 .json/.sh/.mmd（CREATE-GUARD 七格式覆盖面）

1. token 照登记（CREATE-GUARD 七格式含 .json/.sh/.mmd，data/runtime/*.json 也拦）
1. ttl 义务同在（TTL-METADATA 格式面含 .json/.sh/.mmd）：永久区 frontmatter ttl permanent，临时区 task_bound
1. 目录契约扩展名面：docs/_working 只许 .csv/.html/.md/.yaml——.json 落别处或改 .meta.yaml

### CREATE-GUARD

- 强度: 硬阻断
- 触发面: staged 新增的 .py/.yaml/.md/.sh/.ps1/.mmd/.json（非 tests/）
- 判据: 六道链——creation_token 精确路径匹配（7 格式）；merge_evaluation 缺失 warn；.py 头 30 行 14 字段（__init__ 3 字段）；governance/ 根禁新增；类名跨模块唯一；basename 碰撞（含未注册 basename 面）
- 豁免: tests/ 全豁免；rules/ .yaml 走命名检查不走 token；codegen（BEGIN CODEGEN）豁免字段头；类名豁免标记 class-name-alias
- 处方: 先 python scripts/governance/d3_metadata/batch_creation_tokens.py --prefix <目录> --created-by <sid> --capability <名> --merge-evaluation <四判据一句话> 登记，再写文件；token 与内容同批原子或 token 批先行（队列 gate 读 HEAD，倒序必死）
- 判据源: `src/zephyr/gov_enforcement/commit_gates/create_guard.py`

### TTL-METADATA

- 强度: 硬阻断
- 触发面: commit 清单中 .md/.py/.sh/.ps1/.mmd/.yaml/.json（超 500 文件触发全量防 WinError 206）
- 判据: frontmatter ttl 必填且合法——v2 只剩 permanent/task_bound 两值；fail-closed
- 豁免: 豁免区/neutral 无 frontmatter 文件 PASS；temporary zone .md 有 frontmatter 跳 doc_type
- 处方: 永久区文件加 ttl permanent，临时区（docs/_working 等）加 ttl task_bound；ttl 词表仅 permanent/task_bound 两值，7d/30d/session 等不在词表；禁注释锚定自欺
- 判据源: `src/zephyr/gov_enforcement/commit_gates/ttl_gate.py`

### DIRECTORY-CONTRACT

- 强度: 硬阻断
- 触发面: 本次 commit 全部 files
- 判据: 目录契约 DCR-001~007（doc_type 目录归属/扩展名白黑名单/根目录白名单）；fail-closed
- 豁免: none
- 处方: 按目录契约放置/改名；docs/_working 只许 .csv/.html/.md/.yaml（.meta.json 违规改 .meta.yaml）
- 判据源: `src/zephyr/gov_enforcement/commit_gates/directory_contract_gate.py`

---

## FT-queue_channel — 队列通道专项（enqueue/requeue/死信分诊）

判定口诀: 任何走 commit_queue 的提交

1. token 先行纪律：token 批与内容同批原子，或 token 批严格先行——队列 gate 读 HEAD，倒序必死（cleaninv-0007 实证）
1. 死信三分类：吸收型（禁 requeue！核袋=git show HEAD:<file> 对照，内容已在他批落地）/内容死（属主自修）/冤案（环境性，修复后 requeue）
1. requeue 用新快照：死信后先核 HEAD 现状（判据可能已随重构过时——q-0005 判旧单体实证），带 --from-bag 前先核袋
1. requeue 不改 message——死因是 message 类（no-lookup reason 不在白名单）必须新 enqueue（sweep-0002/0013 实证）
1. 直连配方：--allow-non-worktree --adopt-prior-work --allow-overlap + 全暂存区扫描连坐时先临时 unstage 外来件
1. 代修代投：修文件→release_files 精准释放死 sid claim→commit_queue enqueue 留痕（st-cmd 0007 配方）
1. bag 回执自检：落地后 git show HEAD:<file> 验真；NOTHING_TO_COMMIT+blob 不符=陈旧吸收型勿重放

**本类常见死因**（案例册全量见文末速查）:
- [REGISTRY-YAML-PARSE] 吸收型死信盲目 requeue 反复白死 → 先 git show HEAD 核袋；已吸收=放弃重放并销账
- [CAPABILITY-LOOKUP-REQUIRED] no-lookup 理由不在白名单 → reason 改白名单关键词（gate-fix/continuation/mechanical 等 16 项）重新 enqueue

### CAPABILITY-LOOKUP-REQUIRED

- 强度: 硬阻断
- 触发面: commit 含 src/zephyr/**.py 业务代码
- 判据: 本 session 审计日志须有 capability_lookup/rule_discovery 调用记录
- 豁免: message [no-lookup:<白名单 reason>]（gate-fix/continuation/mechanical 等 16 项；sweep 两封死因=reason 不在白名单）；env 紧急逃生
- 处方: 写码前 capability_lookup.find()（留审计）；纯机械批用白名单 reason 词；requeue 不改 message——死因是 message 类必须新 enqueue
- 判据源: `src/zephyr/gov_enforcement/commit_gates/capability_lookup_required_gate.py`

### REGISTRY-YAML-PARSE

- 强度: 硬阻断
- 触发面: staged capability_canonical_file_registry.yaml / data_asset_registry.yaml
- 判据: safe_load 过+顶层根键唯一+capability 档 di_seam_exemptions 末位键+creation_tokens 为 list；fail-closed 无逃生
- 豁免: none
- 处方: token 条目插 creation_tokens 列表尾（di_seam_exemptions 行之前，注意嵌套同名键勿错插）；插后本地 yaml.safe_load 预验再提交
- 判据源: `src/zephyr/gov_enforcement/commit_gates/registry_yaml_parse_gate.py`

### SNAPSHOT-DRIFT

- 强度: 硬阻断
- 触发面: staged data/runtime_violation_snapshot/latest.json
- 判据: JSON 可解析+字段齐+generated_at 24h 内+commit_sha=HEAD
- 豁免: 本 gate 自身修改
- 处方: 重新生成快照再提交
- 判据源: `src/zephyr/gov_enforcement/commit_gates/snapshot_drift_gate.py`

---

## FT-extra-registry — 机制红线（非 in-process 台，但同硬阻断级）

- GIT-SAFE：危险 git 命令清单禁用；禁 plumbing 绕过（read-tree/update-index/write-tree）；[GW:] 伪造=POST-COMMIT-GUARD 自动 reset
- 热文件写入必 safe_write_text CAS；写后进程外核实
- belt daemon 只在心跳陈旧+30min 零落地双条件才杀；epoch 换血（pid 变+队列在动）=健康
- serializer 读 HEAD 代码：盘面热修对落地器无效，修复须走队列正门送 HEAD（K1 铁证）
- 全暂存区 33 台扫描=连坐来源：会话收尾清自己 staged；外来违规不代修（owner 责任制）

---

## DEATH-CASES — 死因处方速查（按实测成本排序）

成本口径=created_at 到 dead_at 分钟（含排队等待）；样本=2026-09-22/23 死信 112 封。

### CASE-DEATH-015-PROTECTED-PATHS

- 症状: PROTECTED-PATHS 写受保护路径
- 关联门禁: PROTECTED-PATHS
- 机制: .gitignore/.gitattributes/AGENTS.md 等须审批
- 处方: message 加 [ARCH-APPROVAL:<issue_id>]（issue 须在册）；勿硬闯勿 env 逃（除非真紧急留痕）
- 实测成本: P50 182.8min/封（最贵档）

### CASE-DEATH-008-IMPORT-DANGLING

- 症状: IMPORT-INTEGRITY 悬空 import
- 关联门禁: IMPORT-INTEGRITY
- 机制: import 目标在 main HEAD+staged 都不存在（他会话未 merge/新路径未同批）
- 处方: import 与目标文件同 commit；他会话未落地先等 merge；改 import 前核目标在 HEAD
- 实测成本: P50 148.4min/封（次昂贵档）
- 证据: k4-0003

### CASE-DEATH-004-TTL-FRONTMATTER

- 症状: TTL-METADATA frontmatter 校验失败（工棚新 .py 常见）
- 关联门禁: TTL-METADATA
- 机制: worktree 新文件缺 frontmatter ttl 或用了废除值
- 处方: frontmatter 补 ttl: task_bound（临时区）；ttl 合法值动态真源=ttl_vocabulary.yaml（现只 permanent/task_bound）
- 实测成本: P50 101.3min/封（昂贵档）
- 证据: buildB-0001

### CASE-DEATH-011-FINAL-MISSING

- 症状: MUTABLE-CONST-WITHOUT-FINAL（__all__ 等缺 Final）
- 关联门禁: MUTABLE-CONST-WITHOUT-FINAL
- 机制: 模块级 List/Dict/Set 赋值未 Final 标注
- 处方: 写 __all__: Final = [...]（AnnAssign 形态）；一行修
- 实测成本: P50 44.6min/封
- 证据: k4-0004, e2e-0004

### CASE-DEATH-007-ORPHAN-MOVE

- 症状: ORPHAN-MODULE：文件搬移后全仓无 import 引用
- 关联门禁: ORPHAN-MODULE
- 机制: ORPHAN 门引用检测不含同批新 import（结构性盲区）；"搬运+同批改引用"被 ORPHAN/IMPORT/格式三门轮番拦死
- 处方: 三方（文件+import+名册）合一批原子；或反方案全回原位零新文件；迁移延后另案
- 实测成本: P50 36.8min/封；k4 三投三死（0006 ruff→0007 ORPHAN→0008 反方案）
- 证据: lane0b-0017, k4-0007, k4-0008

### CASE-DEATH-003-R5-DIGIT-DIR

- 症状: R5 数字后缀目录禁止
- 关联门禁: R5-DIGIT-SUFFIX
- 机制: 目录名 _NN/日期后缀=暗示多真源；新引入目录硬拦，历史不追溯
- 处方: 案卷迁语义名目录重发；已落 HEAD 文件不受影响
- 实测成本: P50 28.9min/封
- 证据: lane0b-0009, e2e-0005

### CASE-DEATH-001-TOKEN-MISSING

- 症状: 无 creation_token，禁止造第二真源
- 关联门禁: CREATE-GUARD
- 机制: 新文件未登记 token（队列 gate 读 HEAD 名册，盘面登记未落地=无）
- 处方: batch_creation_tokens.py --prefix <目录> --created-by <sid> --capability <名> --merge-evaluation "<四判据一句话>"；token 与内容同批原子或 token 批先行独立批
- 实测成本: P50 14.1min/封，112 封中 13 封
- 证据: q-20260923-st-cleaninv-20260923-0007

### CASE-DEATH-005-TRANSLATION

- 症状: TRANSLATION-COVERAGE 新模块无大白话简介
- 关联门禁: TRANSLATION-COVERAGE
- 机制: 新增 .py 未登记翻译册（或 plain_zh 模板话 CJK<8）
- 处方: python scripts/governance/d3_metadata/add_module_translation.py --path <f> --domain <D_*> --name-zh <中文> --plain-zh <人话>
- 实测成本: P50 7.5min/封，9 封
- 证据: emoreplay-0002

### CASE-DEATH-010-RUFF-FORMAT

- 症状: GATE-PRECOMMIT-RUN ruff-format 失败
- 关联门禁: GATE-PRECOMMIT-RUN
- 机制: 落地前未 ruff format 归一
- 处方: 提交前 ruff format <files>；代修配方=ruff format→git rm --cached 旧路径→release_files→enqueue 代投
- 实测成本: P50 4.1min/封（高频便宜档，20 封居首）
- 证据: k4-0006

### CASE-DEATH-002-BASENAME-COLLISION

- 症状: 新文件与已有文件 basename 碰撞（第二函数面）
- 关联门禁: CREATE-GUARD
- 机制: basename 碰撞检测有两条函数面，只豁免修复其一=盲发重发连死
- 处方: 对照两处检查函数确认豁免面（basename==__init__.py）后重发；盲发重发=白死（0058/59/60 连三实证）
- 证据: chainpile-0058, chainpile-0059, chainpile-0060

### CASE-DEATH-006-DIRECTORY-CONTRACT

- 症状: DIRECTORY-CONTRACT 扩展名/目录违规
- 关联门禁: DIRECTORY-CONTRACT
- 机制: docs/_working 只许 .csv/.html/.md/.yaml
- 处方: 改后缀（.meta.json→.meta.yaml 内容转 YAML）+消费侧同批改
- 证据: emoreplay-0001

### CASE-DEATH-009-STALE-SNAPSHOT-REQUEUE

- 症状: NO-COMPLEXITY-GUARD 等判据与盘面现状明显不符
- 关联门禁: COMPLEXITY-GUARD
- 机制: 入队快照是旧单体（判 42>15 时盘上已重构为线性流水）——死信判据可能已过时
- 处方: 死信后先核 HEAD 现状再 requeue 新快照；勿拿旧死因反复盲修
- 证据: q-0005-lane0b

### CASE-DEATH-012-NO-LOOKUP-REASON

- 症状: no-lookup reason 不匹配白名单
- 关联门禁: CAPABILITY-LOOKUP-REQUIRED
- 机制: message [no-lookup:<reason>] 的 reason 不在 16 项白名单
- 处方: 改白名单关键词（gate-fix/continuation/mechanical 等）重新 enqueue（requeue 不改 message 必须新 enqueue）
- 证据: sweep-0002, sweep-0013

### CASE-DEATH-013-BLUEPRINT-HEADER-FORMAT

- 症状: BLUEPRINT-FORMAT：[BLUEPRINT] 头 module_id 不合规格
- 关联门禁: BLUEPRINT-FORMAT
- 机制: module_id 不合裁定#214/#208 规格（MOD-/SH- 前缀格式）
- 处方: 对照规格改头格式再发；未修先重发=盲发白死（chainpile 0061/0062 连死实证）
- 证据: chainpile-0061, chainpile-0062

### CASE-DEATH-014-MASS-DELETION

- 症状: REGISTRY-MASS-DELETION 净删/条目数减少/身份消失
- 关联门禁: REGISTRY-MASS-DELETION
- 机制: 三信号任一（含删16插25代数抵消）；共享暂存区副本陈旧也会误报
- 处方: 合法重排带 [allow-mass-deletion:<理由≥10字>]；共享册 git add 自愈；批量补登走 registry_batch_edit.py
- 实测成本: 8 封
- 证据: in_process 册误报案

### CASE-DEATH-016-ABSORBED-DEAD-LETTER

- 症状: 死信 requeue 后 NOTHING_TO_COMMIT/blob 不符
- 关联门禁: QUEUE-MECHANICS
- 机制: 吸收型死信——内容已被他会话更信落地覆盖，旧袋重放=假落地风险
- 处方: 核袋=git show HEAD:<file> 对照；已吸收=销账勿 requeue（unified-0012 定性先例）
- 证据: unified-0012

### CASE-DEATH-017-WORKTREE-FAKE-RECEIPT

- 症状: worktree 内提交回执成功但 HEAD 无此提交
- 关联门禁: SESSION-REQUIRED
- 机制: worktree 局部队列根主传送带永不排它（statreplay 实证）
- 处方: commit_queue.py --queue-root 主区 enqueue --worktree-root 本区 --no-bootstrap；判据只认 git show HEAD:<file>
- 证据: statreplay

### CASE-DEATH-018-MERGE-BASE-CONFLICT

- 症状: 冲突：入队基底之后 dev 已推进且触及同路径
- 关联门禁: QUEUE-MECHANICS
- 机制: 同路径他会话先行落地，快照基底陈旧
- 处方: 重取最新基底重新入队；热门共享册错峰写
- 证据: scripts/go 冲突案

### CASE-DEATH-019-FOLDER-CAPACITY

- 症状: FOLDER-CAPACITY 目录平铺超 120
- 关联门禁: FOLDER-CAPACITY-HARD-LIMIT
- 机制: 平铺 .py 计数（主区盘口径）超硬限
- 处方: 拆子目录/删残留；注意主区盘与工棚口径差（nightfix 121>120 实案）
- 证据: nightfix q-0008

### CASE-DEATH-020-STATE-VOCAB-MISSING

- 症状: state_vocab 词表线在飞件盘有 HEAD 无——落地环境全员阻断
- 关联门禁: STATE-VOCAB-REGISTRY
- 机制: 词表注册表先行落地与否决定全仓门禁状态（xhs 复职全阻案）
- 处方: 词表/注册表类先行批独立落地；落地阻断等先行批自愈勿对抗
- 证据: xhs-full 复职案

### CASE-DEATH-021-HOT-REGISTRY-EVAPORATION

- 症状: 刚登记的 token/翻译条目从盘面消失；提交被 CREATE-GUARD 拦无 token；batch_creation_tokens 写前守恒闸报基底缺条目拒写
- 关联门禁: REGISTRY-MASS-DELETION
- 机制: 共享热册被并发写手与还原机制（watchdog quarantine_tamper 搬移/检查点流程/B2 盾 staging）CAS-less 覆盖——盘面回落旧态，未提交写入蒸发（09-24 实测：盘面缺 31 条+写入后 42s 逐字节回滚+watchdog 三次 quarantine 案底）
- 处方: ①写前做三方条目集对账（HEAD/盘面/index 各自 safe_load 抽 creation_tokens 集合比对，任一守恒闸拒写即停勿强写）②写后立即入袋（袋读盘面快照，落地走三向合并不受盘面翻转影响）③整段修复用段级重建+CAS（safe_write_text expected_base_sha256），禁 git checkout 整片覆盖 ④证据交黑手取证包治本（G1 还原审计闸/G2 还原 CAS 化）
- 实测成本: 单次损失 15-60min（重写+重登记+死信循环）；2026-09-22 蒸发事故 116 条净损的同机制前案
- 证据: st-commitsys-20260924-tripwire, .runtime/quarantine/drift_20260923T*

---

## APPENDIX-A — 全台速查表

| gate | 强度 | 触发面（一句） | 处方（一句） |
|---|---|---|---|
| HELD-OVERLAP | block | 提交目标文件被其他活跃 session 持有（SessionRegistry+.ailocks 双轨） | 等锁释放 |
| FORGED-GW-MARKER | block | commit message 含 [GW: 标记 | 从 message 移除手写 [GW:] 片段——留痕标记由网关自动追加，永不手写 |
| FOREIGN-CHANGE-DETECTION | block | 目标文件在 claim_files 时有基线快照且他会话 claim 痕迹存在 | 失败提交重试带 --adopt-prior-work |
| DERIVED-FILE-DELETION-PROTECTION | block | staged 删除清单命中受保护派生文件（blueprint_registry.yaml 等） | 跑 sync_registry_from_blueprints.py --write 恢复派生文件 |
| COMMIT-SCOPE | block | 每个 commit 的 files 清单 | 拆分为每域一笔 |
| SESSION-REQUIRED | block | 每次 commit | 会话启动第一步 session_worktree_start() |
| CLAIM-REQUIRED | block | commit 目标 files 清单 | 提交前 lock_files.py acquire <file> <sid>（或 gateway claim_files） |
| CAPABILITY-OVERLAP | conditional | staged 新建 .py（own-scope） | 扩展现有函数而非新建 |
| DIRECTORY-CONTRACT | block | 本次 commit 全部 files | 按目录契约放置/改名 |
| TTL-METADATA | block | commit 清单中 .md/.py/.sh/.ps1/.mmd/.yaml/.json（超 500 文件触发全量防 W | 永久区文件加 ttl permanent，临时区（docs/_working 等）加 ttl task_bound |
| FILE-PLACEMENT-TTL | block | 全部 staged 非删除文件 | 正式新文件走 promote 准入旗 |
| CREATE-GUARD | block | staged 新增的 .py/.yaml/.md/.sh/.ps1/.mmd/.json（非 tests/） | 先 python scripts/governance/d3_metadata/batch_creation_tokens.py --prefix <目录> - |
| RULE-EXECUTION-PAIRING | block | rules/trae_*.yaml 变更或 message 含 [rule-mod] | enforcement 段补 paired_gate_id（挂真 gate 或 null） |
| REFERENCE-INTEGRITY | block | staged 新增文本中的三类引用——#ARCH-NNN、AGENTS.md 章节号、ruling 文档里的 commi | 补登 architecture_issue_registry.yaml（与引用同批）或删引用 |
| RULE-FOUR-WAY-ALIGN | block | staged 规则文件或 rule_catalog_registry | 改 YAML 后同步 catalog/disk/code 引用 |
| RULING-COMMIT-VERIFIED | block | ruling 文档/架构登记册新增行声明已完成 commit hash | 核对 hash 拼写与是否已合并 |
| R5-DIGIT-SUFFIX | block | 文件路径任意父级目录名匹配数字后缀（新引入才拦，历史不追溯） | 用语义名目录（e2e_20260924 违规、e2e_integration 合法 |
| TRANSLATION-COVERAGE | block | 新增 .py（src/zephyr/ 或 scripts/ 下） | python scripts/governance/d3_metadata/add_module_translation.py --path <file> -- |
| ENCODING-SAFETY | block | .py/.md/.yaml/.yml/.json/.toml/.ps1 | .ps1 注释写英文 |
| SSOT-REDEFINITION | block | staged .py 新增 class 或赋值且符号在 SSoT 清单 | 查 capability_canonical_file_registry.yaml 找 canonical 文件后 import |
| UNSAFE-DICT-SPREAD | warn | .py 新增行类构造直接字典展开 | 改 SomeClass(**filter_dataclass_fields(SomeClass, data)) |
| PURE-SHIM | block | 全部 staged .py | 删 shim，消费者改引 canonical 路径 |
| PURE-ASSERTION | block | 本 session staged .md added 行 | 删过渡表述写现值 |
| NOQA-VALIDATION | block | 全部 staged .py 全文行 | 先在 noqa_exempt_registry.yaml 登记 marker（理由至少 10 字），行内 marker 后直接附理由（两空格为登记约定非机器强制 |
| NO-DOMAIN-NAME-ZH-DIRECT-ACCESS | block | .py added 行 DOMAIN_NAME_ZH 字典直访 | import get_domain_name_zh 或 get_domain_name_zh_strict（strict 未找到返回空串，用于 mermaid  |
| DATETIME-NOW-FORBIDDEN | block | 生成器代码（generators 目录或 generate_ 前缀）新增行；src/zephyr/ 新增行 | 改 now_utc() 或 datetime.now(UTC) |
| GATE-VOCAB | block | 新增 .py 硬编码词表合法值 | 按 check_vocab_hardcode.py 输出改加载器读取 |
| SNAPSHOT-DRIFT | block | staged data/runtime_violation_snapshot/latest.json | 重新生成快照再提交 |
| FILE-COPY | block | staged 新增 .py 与主仓已有同名 basename 文件比对 | 扩展现有文件而非复制 |
| ID-UNIQUENESS | block | staged .pre-commit-config.yaml | 去重 hook id |
| EXEMPT-ZONE-FM | block | 豁免区（docs/_working、_archive、.runtime、.trae、templates）.md/.yam | 去 doc_type 或迁正式目录 |
| MODULE-ID-CONSISTENCY | block | .py 含 CFG-/MOD-/PS- 三轨道声明头 | 对齐三轨道声明 |
| PERMANENT-SYSTEM-TRIGGER | block | 新增 [TTL] permanent .py | 改 event_bus.subscribe 事件驱动 |
| MSG-EXPOSURE | block | .py 异常消息 f-string 含敏感变量（路径/tx_id/凭据/连接串/SQL） | raise XxxError(消息, details=字典) |
| EMPTY-HANDLER | block | 新增 .py 事件 handler | 补实际逻辑 |
| ORPHAN-MODULE | block | staged 新增 src/ 下 .py | 引用方与模块同批 |
| DOC-REF-BROKEN | block | 新增 .md 的相对链接 | 目标文件同批创建或修相对路径 |
| FUNCTION-DUP | block | 新增 .py 顶层函数 | 扩展而非复制 |
| NO-BARE-GETENV | block | .py 新增行裸 os.getenv/os.environ 读密钥类变量 | get_secret/get_secret_or_default |
| MSG-STYLE | block | .py 异常消息字符串 | 统一 ASCII 箭头+无句号结尾 |
| NO-UPWARD-IMPORT | block | staged shared 层 .py 的 ImportFrom | 类型真源下沉 shared 或放 TYPE_CHECKING |
| NO-HARDCODED-URL | block | .py added 行 localhost URL | import DEFAULT_OLLAMA_URL 等常量 |
| MAP-ALIGNMENT | block | 触碰 depgraph/dataflow/decision 相关路径（聚合台含 legacy 注册） | python scripts/governance/sync_panorama_module.py --all 对齐后提交 |
| NO-BARE-SQL | block | staged .py 中 SQL 字符串 | SQL 提为模块级常量或走 DatabaseService |
| CH-BATCH-SIZE | block | .py added 行循环体内 write_result | writer.add 循环+flush |
| CH-FINAL-GATE | block | .py 直调 ch_writer.query 或硬编码 ReplacingMergeTree 查询 | ch_writer.query 改 ch_reader.query |
| CH-VERSION-COL | block | 新增行含 ReplacingMergeTree 带非时间列 | 用 ingest_ts DateTime DEFAULT now() |
| COMPLEXITY-GUARD | block | staged .py 真正新增的函数（改签名已有函数不重罚） | 拆短函数+回归 |
| ALGO-NOTE-SYNC | block | 触碰决策地图节点 module_ref 指向的 .py | 同批改 algo_note_zh 或加 note_confirmed 日期行（TDM 地图与触码批同批原子） |
| ALGO-FLOW-LINK | block | 触碰含 ALGO_FLOW external 锚的 .py 或 algo_flow 镜像 yaml | 新增外锚 token 与 yaml 同批 |
| META-TESTS-COVERAGE | block | staged 触碰 commit_gates/*.py 时扫全目录 | 补测试文件或改 [TESTS] 豁免值 |
| TEST-SOURCE-CONSISTENCY | block | tests/ .py added 行 from zephyr import | import 实存符号或源码补齐 |
| BLUEPRINT-FORMAT | block | .py added 行 [BLUEPRINT] 头（无 tests/ 豁免） | 对照裁定 214/208 改 [BLUEPRINT] 头 module_id 格式后再发（盲发重发=白死三连实证） |
| GATE-DOMAIN-FK | block | .py added 行 [DOMAIN] D_XXX | 改已注册域或同 commit 新增域条目 |
| BLUEPRINT-HEADER | block | .py added 行 [A_module] module_id 与 [BLUEPRINT] 头（聚合台含双头一致性） | MOD-INF_a2a 改 MOD-INF-a2a（DASH 或大写） |
| CAP-CONSISTENCY | block | staged provider .py | meta.capabilities 补声明或补方法 |
| NO-IMPORT-SIDE-EFFECT | block | src/ .py 模块级语句 | 副作用移入函数或惰性工厂 |
| DEPGRAPH-FRESHNESS | conditional | always-on 每次 commit | python scripts/governance/generate_project_depgraph.py 刷新后再提交 |
| RECONCILER-HEALTH | conditional | always-on | resolve_blocks() 清障后提交 |
| SCRIPTS-IMPORT-INTEGRITY | block | 本 session staged scripts/governance/**.py | 顶部补 from _shared.constants import 符号 |
| GIT-CALL-BUDGET | warn | .py added 行循环体内 subprocess git 调用 | 改 GitCommandBatcher.git_show_batch |
| BARE-SUBPROCESS | block | .py 新增行 subprocess.run/Popen 等 | 改 process_pool.py 的 run_subprocess_hidden/spawn_python_hidden |
| UNDEFINED-NAME | block | scripts/governance/** 与 src/** .py | 补 import/修拼写/补本地定义 |
| IMPORT-INTEGRITY | block | 本 session staged .py 的绝对 import | import 目标与 import 语句同 commit |
| CAPABILITY-LOOKUP-REQUIRED | block | commit 含 src/zephyr/**.py 业务代码 | 写码前 capability_lookup.find()（留审计） |
| GATE-PRECOMMIT-OFFLINE | block | staged .pre-commit-config.yaml | repo local+stdlib local hook |
| FOLDER-CAPACITY-HARD-LIMIT | block | staged .py/.yaml/.md 所在目录 | 拆子目录 |
| DEPGRAPH-ENFORCEMENT | block | staged src/zephyr/**.py 带 [TTL] permanent（聚合台） | 先 apply_depgraph.py --add-design-node 登记，完工后 --transition-build-status <node> pr |
| DERIVATION-ANNOTATION | block | 新增 .py/.yaml 头部 DERIVES_FROM 声明 | 修路径或删声明 |
| RELATIVE-PATH-LITERAL | block | .py added 行字符串以 ./ ../ ~/ 开头 | REPO_ROOT 或 Path(__file__).resolve().parent 拼接 |
| CONSUMERS-ACCURACY | warn | .py [CONSUMERS] 头部 | 核实/删除失实声明 |
| SCHEMA-FILE-EXISTS | block | staged business_data_categories.yaml | schema 文件同批 git add 或修路径 |
| ASYNCIO-RUN-IN-CONTEXT | block | src/zephyr/ .py 新增行 | 改 async_utils.run_coroutine_sync |
| MUTABLE-CONST-WITHOUT-FINAL | block | src/zephyr/ .py 新增的模块级可变容器赋值（List/Dict/Set） | 写法改 AnnAssign+Final（如 __all__ 加 Final 注解） |
| OPEN-WITHOUT-WITH | block | src/zephyr/ .py 新增行裸 open() | with open 上下文管理器 |
| ZEPHYR-ENV-DIRECT-ACCESS | block | src/zephyr/ .py added 行 os.environ 访问 ZEPHYR_ENV | 经 src/zephyr/shared/foundation/config 读取 |
| MCP-VERSION-FIELD | block | staged mcp.json | 补 version 字段 |
| PROTECTED-PATHS | block | staged 命中受保护路径（.gitignore/.gitattributes/AGENTS.md 等） | 走 [ARCH-APPROVAL:<issue_id>] 标记（裁定登记后），勿硬闯 |
| BLUEPRINT-NODE-ID-HARDCODE | block | blueprint.md 新增/修改 | 用稳定逻辑标识替换物理 ID |
| WORKTREE-REQUIRED | block | 每次 commit | session_worktree_start 隔离施工 |
| TEST-RESIDUE-SSOT | block | .py 新增/修改中硬编码测试残留前缀集合（两个以上元素命中） | 改 reconciliation_registry._load_test_residue_config() 动态加载 |
| SECRET-REGISTRY-CONSISTENCY | block | staged 含 .env.example 或 config/secret_registry.yaml | 新密钥三步流程齐步走（裁定 S-1） |
| NO-SECRET-HARDCODE | block | .py/.yaml/.yml/.json/.toml added 行密钥模式（sk-/AKIA/ghp_/KEY 赋值） | 走 zephyr.shared.security.secrets（get_required_secret 等） |
| RECONCILER-FILE-OPS | block | 治理代码（governance/gov_enforcement/scripts/governance/backup）新增 | guard_remove/guard_move/guard_recycle |
| REGISTRY-CODE-ANCHOR | block | staged 命中 15 业务注册表或 src/ .py 删除/改名 | 同步改条目或标 deprecated |
| STASH-ACCUMULATION | conditional | 每次 commit 全局状态 | ZEPHYR_STASH_LIFECYCLE_AGGRESSIVE=1 触发 reconciler 清理 |
| TABLE-NAME-REGISTRY | block | .py added 行硬编码表名字符串 | 常量替换为 TableRegistry 引用 |
| GATE-ERRCODE-CONSISTENCY | block | staged src/**.py 或 error_code_registry.yaml | 按 detail 内下一可用号（ZA-前缀-N）取号登记 |
| HOT-FILE-BASE-FRESHNESS | block | 热文件（注册表/宪法/tracker）+有 claim_head 锚点 | git log -p 区间核对上游改动 |
| STATE-VOCAB-REGISTRY | warn | .py 新定义状态枚举类（类名含 state/phase/regime/emotion/mode） | 词表登记或 noqa |
| TAG-VOCAB | warn | catalogs/ yaml 的 tags 列表 | 改标准词或先收编 library_tag_vocabulary.yaml |
| BLOOD-FLESH | warn | 新增 .py 翻译条目 A 面/翻译册新增条目 B 面 | add_module_translation.py 一条命令（同 TRANSLATION-COVERAGE） |
| FRONTEND-TRUTH-SOURCE | warn | dashboard/web/ .js（豁免 api.js/loader.js 等） | 接 services/api.js 真源通道 |
| BUSINESS-REGISTRY | block | staged 命中 19 文件/21 段业务资产库 | 先 apply_depgraph 登记 blueprint 再入库 |
| REGISTRY-MASS-DELETION | block | staged YAML 命中 _registry/catalogs/ 或 ROOR | 批量补登走 scripts/governance/registry_batch_edit.py 纯插入 |
| REGISTRY-YAML-PARSE | block | staged capability_canonical_file_registry.yaml / data_asset_ | token 条目插 creation_tokens 列表尾（di_seam_exemptions 行之前，注意嵌套同名键勿错插） |
| SPLIT-COORDINATION | block | 活跃拆分声明在案且提交命中 old_paths | re-base 到新位置 |
| SYNTAX-VALIDATION | block | 本 commit 清单全部 .py（含 tests/） | 修语法错误 |
| RESOURCE-SCHEDULE | block | staged config/resource_profile_registry.yaml | 错峰/互斥声明/co_start_intent |
| REAL-KEY-REFERENCE-SCAN | block | own-diff 任意文本文件出现 QMT前缀+REAL后缀组合键名 字样 | 代码/配置/文档删 QMT前缀+REAL后缀组合键名 字样改间接引用 |
| TASK-ORDER-DOCS-LOCK | block | own-diff 含 TO-*.yaml 任务书且同批含其他施工产物 | 判据变更拆出本批，独立复核会话出修订案或 Owner 改判后再交施工产物（主文档 3.2 协议） |
| CONSTITUTION-LINE-LIMIT | block | own-diff 含任意目录深度的 AGENTS.md | 等长替换压回 300 行内 |
| GIT-DANGEROUS（机制红线） | block | 危险 git 命令（reset hard/checkout 等）+plumbing 绕过 | 走 git_commit.py 正门 |
| SESSION-HEARTBEAT（机制红线） | warn | 长任务会话（reaper 看护面） | 长批先登记 data/runtime/process_reaper_keep.txt（每行一个 cmdline 子串） |

## APPENDIX-B — 在册未蒸馏台目（生成器自动清点，蒸馏后重跑）

（无——在册全覆盖）

## APPENDIX-C — 判据源新鲜度快照

- 漂移待重蒸馏: 0 台
- 未记录哈希: 0 台
- 在册覆盖: 102/102

