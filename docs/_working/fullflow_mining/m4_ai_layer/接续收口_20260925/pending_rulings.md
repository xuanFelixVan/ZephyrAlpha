---
ttl: task_bound
volume: pending_rulings
session: st-ailayer-final-20260924
creation_token: fullflow-w4b-m4-pending-rulings-20260926
---

# 接续收口_20260925 · 待裁清单（车道 W4-B 补四案，编号 W4B-M4-1…W4B-M4-4）

> 铁律：**本车道不自赋裁定号、不写"Owner 已裁"**；W4B-M4-n 是本车道内部流水，非 `ruling_registry.yaml` 裁定号。
> 案源=`04_f89_local_models_and_embedding.md`（本地模型与嵌入格）。门位口径依宪法 §5。

| # | 问题 | 已试路径（实测） | 选项 | 建议 | 门位属性 |
|---|---|---|---|---|---|
| W4B-M4-1 | **宪法 §9.3 红线口径歧义**：红线写"reconciler 必须事件触发，禁 cron/Timer/sleep-loop"，而 `local_model_scheduler` 能力卡自述 tags=`[scheduler, daemon, polling]`、实现为 `_task_queue.get(timeout=poll)`（`src/zephyr/integration/local_model/local_model_scheduler.py:243`）＋两处 `time.sleep`（:176 启动握手、:296 退避）。**阻塞式队列取任务**与**忙等轮询**在红线文本里未区分 | 读实现三段（:120-135/:170-200/:240-250/:290-300）；读能力卡 `data/capability_cards/local_model_scheduler.yaml`（MOD-INF-035、24/7 loop、P0/hot/ACTIVE）；起停实证=`pipeline_orchestrator.py:429-430/813/818` | a＝精化红线为"禁忙等 sleep 轮询；`queue.get(timeout)` 型消费合法"；b＝判该件违宪并要求改事件驱动（真·唤醒式）；c＝不动文本，逐案豁免登记 | **a**（现文本会让每台队列消费者都落进"待判违宪"，是口径缺口非该件缺陷）；本车道**不自行判其违宪、也不为其开脱** | 治理门（medium；改宪法 §9.3 文本＝热文件，总筹／Owner 落地） |
| W4B-M4-2 | **能力卡面在 ROOR 无登记**：`data/capability_cards/` 44 张 yaml，ROOR REG-SKILL-001（`docs/registry_of_registries.yaml:97-104`）只认领 22 张 `skill_*.yaml`，另 22 张能力卡（含本环节四张：ollama_chat/embedding_router/local_model_scheduler/reranker）**查无条目** → 本地模型能力面无机读注册身份 | `ls data/capability_cards/*.yaml \| wc -l`=44；`ls \| grep -c "^skill_"`=22；`grep -l "^capability_id:" *.yaml \| wc -l`=44；ROOR grep 仅 :99 一条指向该目录 | a＝ROOR 增 `REG-CAP-001 能力卡目录`（口径=非 skill_ 前缀，maintenance 与 generator 注明）；b＝两类件分目录后各登一条；c＝并入 REG-SKILL-001 改口径为"44 张两类" | **a**（b 要动 22 个文件路径，触发 RENAME-DEPGRAPH-SYNC 与翻译册同步，成本不对等） | 治理门（medium；ROOR 新增非净删） |
| W4B-M4-3 | **LSG 闸门可被环境静默关闭**：`lsg_gate.py:64 LSG_ENABLED_ENV="ZEPHYR_LSG_LOCAL_MODEL_ENABLED"`，:31 口径"（'0'/'false'/'off'/'no' 关闭）> 默认开"；fail-closed 只覆盖"LSG 不可用/判决 BLOCK"，**不覆盖"人为关掉闸门"这一路径的留痕** → 宪法 §9.2"所有 LLM 调用必经 LSG"存在一条无声旁路 | 读 `src/zephyr/integration/local_model/lsg_gate.py:19-31/60-90`（自述"三通道同一闸门，无旁路"＋`resolve_lsg_enabled`）；确认调用链：`ollama_chat.py:42` 真 import lsg_gate、:473 才 post；`grep -c "adversarial\|red.blue\|local_model" gate_registry.yaml` 类实测→本环节不在提交门册（属运行时闸门，符合设计） | a＝关态 MUST 写 L6 审计一条含 reason；b＝生产禁关（部署脚本/`register_*.ps1` 固定置 1 并加自检）；c＝a+b | **c**（a 是审计面，b 是执行面；只做 a 仍可长期旁路，只做 b 无留痕） | 治理门（medium）；**若改为"flag 出厂值翻转"（如把默认关→开或反之）＝Owner（high）** |
| W4B-M4-4 | **承载服务无守护，归属两说**：ollama 侧计划任务 `ZephyrAlpha_OllamaServe` 在本战役 m5 簿记为"一次性 / 09-20 拉起 / 0 次运行"，健康表判"拉起后无守护、未逐项验证（黄）"；本环节全链路（嵌入/聊天/重排）依赖它，掉线即静默降级。归 F89（模型源）还是 F76-F85（调度常驻）？ | `grep -i "zcode\|ollama" docs/_working/fullflow_mining/m5_scheduling/01_windows_schedtasks.md:91`；`05_master_health_table.md:34`；`ollama_chat.py:563` 有 `/api/tags` 探活码（能力在、无外部巡检消费方）；宪法 §0.2 keep 名单=`data/runtime/process_reaper_keep.txt` | a＝归 m5 调度车道（加存活探测＋事件重拉）；b＝归 F89 自持（embedding/chat 内建重拉）；c＝登记为已知跨车道缺口不排工 | **a**（重拉属调度面通用能力；F89 内建重拉会与 reaper/watchdog 体系形成同域重复簇，违 w5_1 判据③）；另需注意在案教训"LLM 腿无人重启"与本病灶同型 | 治理门（medium）；若涉 reaper keep 名单或计划任务注册变更＝落地车道执行面（low→medium） |

## 复核命令

```bash
sed -n '97,104p' docs/registry_of_registries.yaml
ls data/capability_cards/*.yaml | wc -l ; ls data/capability_cards/ | grep -c "^skill_"
sed -n '19,31p;60,90p' src/zephyr/integration/local_model/lsg_gate.py
schtasks /query /tn ZephyrAlpha_OllamaServe /fo LIST /v | grep -i "Task To Run\|Last Run Time\|Status"
```
