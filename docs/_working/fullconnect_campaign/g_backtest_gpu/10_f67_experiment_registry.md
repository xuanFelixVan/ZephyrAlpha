---
ttl: task_bound
title: "F67 实验登记与档案——experiment_registry 11 条 FallbackBackend+Panel 实验 Tab"
session: zc-l07-20260927
create_guard: creation_token 由落地车道随批补办（M2 车道先例）
---

# F67 · 实验登记与档案（总册状态 built/P2；本卷复核=built 维持，11 条+FallbackBackend+Panel Tab 三锚全实证）

## 一、六向台账（实证锚点）

| 向 | 实证（本日实勘） |
|---|---|
| 上游输入 | F66 考试/循环产物（run 目录 VAL-*）；src/zephyr/experiment_tracking/ 四 adapter（vectorized/strategy_runner/c1/c2c3，本日 ls 实测） |
| 下游消费 | F50 C3 绩效归因反馈（总册边 F67→F50）；前端 Panel 实验 Tab（Owner 查阅面）；log_location/artifact_path/fallback_ref 三指针（registry :25 实锚） |
| 自动化触发 | imported 库件+CLI；无计划任务 |
| 真源与注册表 | docs/01_policies_and_standards/_registry/catalogs/experiment_registry.yaml：**experiments=11（本日 yaml 解析实测）**；存储后端=**FallbackBackend 本地 JSON**（logs/experiment_tracking_fallback/{component}/{run_id}/run_meta.json，:75 实锚）；**MLflow 已裁定完全卸载**（:26 实锚）；真源反查链=51 号（FallbackBackend/C1 实验契约）+52 号（BM-BT-01~07 回测设施）+代码（:31-33 实锚）；条目=真实可溯源实验（4 条 regime_validation 已 completed 起账，:33） |
| 门禁与质量尺 | pending_fk=1（本日解析实测，外键悬空 1 条登记在册）；指令 mlflow_run_id→fallback_ref 迁移注记（:33） |
| 当前运行状态 | **built（P2 支线）**：登记+档案+面板三件在位；实验写入频度低（批次制） |

## 二、子模块三级枚举（登记→存储→面板三级；本日实扫）

- **登记表**：experiment_registry.yaml（11 experiments+pending_fk 1）；schema 含 log_location/artifact_path/fallback_ref 三指针字段
- **存储层**：src/zephyr/experiment_tracking/（adapters 4 件实测：vectorized_adapter/strategy_runner_adapter/c1_adapter/c2c3_adapter——各回测引擎/策略运行器→实验档案的适配面）；FallbackBackend 落点 logs/experiment_tracking_fallback/
- **面板层**：src/zephyr/frontend/dashboard/app_panel.py:40（"8. 实验历史—experiment_history（v3.4.0）"）+:100-102（import fetch/render）+:437（_tab_experiment_history）+components/experiment_history.py（**Panel 实验 Tab 实证**）
- **姊妹档案**：data/backtest_artifacts/（bt-*.json 族+backup_val_20260909_smoke+drills/<run_id>——M2-02 危机演练落盘口径）；run 目录 VAL-* 归档经 run_archive.py

## 三、接线四态独立复核

| 面 | 四态判定 | 复核证据 |
|---|---|---|
| 登记表 | built（11 条实测） | yaml 解析本日 |
| FallbackBackend | built（MLflow 卸载裁定在册） | :26/:75 实锚+adapter 4 件 |
| Panel 实验 Tab | built wired | app_panel 三处行号实测 |
| 档案完整性 | 黄（历史蒸发案受害者域） | IBT 成绩单 22 件蒸发在案（M2-06 堵点 4，artifacts 重建依赖 runner 幂等） |

### 骨架勘误
- 无锚点级勘误。补充：experiment_registry 与 backtest_artifacts/run 目录是**两套档案面**（登记表=元数据，artifacts=产物），总册一句话未区分，检索时须两处都查。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | pending_fk=1 外键悬空 | 查悬空对象补链或标注弃用（XS） | P2 |
| 2 | IBT 22 件产物蒸发未重建 | runner 幂等重放重建（施工班，同 F65 缺口 3） | P1 |
| 3 | 实验写入靠批次自律（跑完不登记无拦截） | run_archive 归档时校验 registry 条目存在（XS，与 F66 缺口 4 同批） | P2 |
| 4 | 11 条 vs 实际跑批轮次（GPU T0/T1 多轮）覆盖度未证 | 完赛后批量补登记（S，随 F68 完赛） | P2 |

## 五、自审闸三态
**挖干可施工**（三锚全实证+四级档案地图补全；P2 支线按内收判据暂无退役项——登记/存储/面板三件均有消费）。

## 六、复跑命令
```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$PATH"
python -c "
import yaml,io;d=yaml.safe_load(io.open('docs/01_policies_and_standards/_registry/catalogs/experiment_registry.yaml',encoding='utf-8'))
print(len(d['experiments']),d.get('pending_fk'))"
sed -n '25,26p;75p' docs/01_policies_and_standards/_registry/catalogs/experiment_registry.yaml   # 三指针+MLflow 卸载
sed -n '40p;437p' src/zephyr/frontend/dashboard/app_panel.py    # 实验 Tab
ls src/zephyr/experiment_tracking/adapters/*.py | grep -v __init__
ls data/backtest_artifacts/ | head -5
```
