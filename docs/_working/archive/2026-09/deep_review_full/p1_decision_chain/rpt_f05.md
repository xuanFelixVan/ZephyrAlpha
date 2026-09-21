---
ttl: task_bound
title: 深度审查报告——F05 技术指标注册引擎（indicator_base）
owner: st-deeprev-20260918
reviewer_model: GLM-5.3-Flash
baseline_commit: 2fa92002c3
created: 2026-09-18
---

# 深度审查报告：F05 技术指标注册引擎（GLM-5.3-Flash / 基线 2fa92002c3）

- 状态: **已审**
- 级别: P1｜类型: 引擎（指标库地基：meta/抽象基类/注册表/autodiscover）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/factor/technical_indicators/indicator_base.py:175(Registry)(:254 autodiscover)`
- 生产调用方: 真实——data/implementations/internal_compute_provider.py:1017-1025（autodiscover+list_all）、:1649-1654（Registry.get）；trend/momentum/volatility/volume/reversal 五族装饰器注册
- 测试文件: tests/zephyr/factor/technical_indicators/test_indicator_base.py（存在）
- 变更热力: 2026 年 4 commits（低热）
- 材料包缺项: 运行时证据包缺（低风险；注册表数量有 gate 体系外覆盖）

## 1 对象快照

指标库地基三层：TechnicalIndicatorMeta（元数据）/ TechnicalIndicatorBase（抽象基类，compute→多列 DataFrame，区别于 FactorBase 单列）/ TechnicalIndicatorRegistry（全局单例注册表+装饰器）/ autodiscover（pkgutil 扫描动态 import）。**排除项及理由**：五族指标的具体数学实现（trend/momentum/volatility/volume/reversal 模块）——递推初值/warmup/NaN 语义的数学四问归属各实现件，本件只审地基机制；建议后续批对其逐指标与 TA-Lib 对拍。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| B | **autodiscover 污染 sys.path**：package_path 默认本目录时 parent=src/zephyr/factor 被 insert(0) 进 sys.path[0]——factor/ 下所有子目录/模块获得顶层命名空间导入位（shadowing 向量：与任意三方包同名的子目录将劫持顶层 import） | indicator_base.py:270-276 | P2 | `python -c "import zephyr.factor.technical_indicators as t,sys; t.autodiscover_technical_indicators(); print(sys.path[:3])"` |
| B | **autodiscover package_path 参数名不副实**：扫描用传入目录，但 import 名硬编码 `zephyr.factor.technical_indicators.{module}`（:282）——传其他路径会扫 A 装 B（潜在坑+误导 API） | indicator_base.py:278-284 | P3 | 传 tmp 目录含同名模块，观察 import 的仍是本包模块 |
| E | **模块 import 失败仅 warning 静默跳过**：某指标模块语法坏/依赖缺→注册表缩水无告警通道；下游 internal_compute_provider:1025 list_all 直接消费→特征缺口静默（模式#6 变体） | indicator_base.py:283-288 | P2 | 造坏模块放目录内跑 autodiscover，看仅 log.warning |
| A | **__len__ 死代码**：定义在类体只对实例生效；本件全类方法用法（单例语义），len(类) 抛 TypeError——误导 API | indicator_base.py:245-246 | P3 | `len(TechnicalIndicatorRegistry)` → TypeError |
| A | list_output_columns 无去重/冲突检测：两指标输出同名列时静默重复，DDL 列映射上游漂移 | indicator_base.py:232-238 | P3 | 双指标注册同 output_column 看清单重复 |
| A（边界） | validate()：None/空→False，缺列→raise（ERROR_CONTRACT :13 声明一致 ✓）；get_params 覆盖合并 ✓；注册表重复 ID raise ✓（测试重注册依赖 clear()，并行测试有 clear 竞态面） | :143-158, 160-164, 203-208 | ✓ 查无（竞态 P3） | 并行测试下双文件同时注册同 ID |
| C | 消费链闭合 ✓：internal_compute_provider 动态接线两处真实消费（autodiscover→list_all→get→compute）；与 header [CONSUMERS] 声明一致 | internal_compute_provider.py:1017-1025, 1649-1654 | ✓ 查无 | grep |
| D | warmup 契约只写在基类 docstring（"预热期前 N-1 行为 NaN" :140），无 enforce/无输出列校验 hook——子类不守约无人拦 | indicator_base.py:130-141 | P3 | 造不守约子类注册，validate 仍通过 |

## 3 SOTA 对照

- **对等已有（基线）**：TA-Lib（https://ta-lib.org/ ，TA-Lib.org，C 开源库，200+ 指标）为业界指标语义基线；RSI 等 Wilder 平滑约定官方文档（https://ta-lib.org/functions/rsi ，TA-Lib.org）。（2026-09-18 检索）
- **立卡候选**：本件"纯自实现无第三方 TA 库依赖"是 header 明示设计裁定（INVARIANTS :8）——建议立卡"指标实现 vs TA-Lib 数值对拍"变形测试（首批：RSI/MACD/KDJ），防自实现递推漂移；非替换建议。
- 驳回：无。

## 4 缺陷清单

1. **P2 autodiscover sys.path 污染**：insert(0, factor/) 属全局副作用，构建/测试环境 shadowing 风险。建议：删 sys.path 操作（importlib 已可按 full_name 导入，pkgutil 扫描不需 sys.path）。验证法：§2 B-1 命令。
2. **P2 坏模块静默缩水**：autodiscover 失败仅 warning。建议：失败聚合 raise 或注册告警表（对接 workspace_alerts）。验证法：§2 E 行。
3. **P3 组**：package_path 参数误导、__len__ 死代码、输出列重复、warmup 契约无 enforce、clear() 并行竞态。

## 5 挂起疑问

- 五族指标实现件的数量/覆盖（header 声称 8 文件）与注册表 gate 侧的总量核对属后续指标实现批范围。

## 6 完备性自评

六轴全查（A 的数学四问：本件无递推算法，以边界/契约四问覆盖；指标数学排除声明见 §1）。长尾：①pkgutil.iter_modules 对 zip 包/冻结环境的兼容未测；②meta.version 字段无消费方（grep 未展开到前端）。

## 7 收口裁定（收口方填）
- 三态逐条:
- 修复 commit:
- 复检结论:
