---
ttl: task_bound
title: final3 战役台账——排班/并发档位/提交清单/C 类趋势线（滚动更新）
---

# a1_campaign_ledger.md — final3 战役台账

## 1. 并发档位（自适应爬坡协议，Owner 定）
| 波次 | 档位 | 死亡 | 依据 |
|---|---|---|---|
| 波1 | 4 | 1（X-7 代理 600s 不活跃死） | 起步档，实测 3/4 成活 |
| 波2 | 4 | 0 | 死一降档：不升维持 4（X-7 重派+恢复残留） |
| 波3 | 6 | 0 | 波2 零死亡→+2 探测 |
| 波4（计划） | 6 | - | 波3 零死亡，保守 +0（额度波动观察） |

机械扫描一律 Python 脚本（w8_ledger_scan.py 等在 .runtime/tmp/），不占代理额度。

## 2. 开工自证与抢救（2026-09-19）
- 冷启动 PASS：Python 3.12.8 / lock CLEAN / reaper 存活（last_run 09-18 19:10，dry_run 模式）。
- 会话 st-final3-20260919 注册+detached 心跳 daemon 30s。
- **st-bizmine2-20260919 不在会话注册表=已死**[亲验]→W2 按 BM-1 接手；其 stale claim 已自清（lock CLEAN）。
- 回退炸弹三分法：1 条（bizmine_campaign_ledger.md，WT==HEAD/INDEX 陈旧 -3 行）已复位，内容中性[亲验]。
- W8-5：AD 残留 docs/_working/2026-09-19-max-dayshift-rulings.md 已 git restore --staged 清除[亲验]。
- 他会话在途件：36 条 staged 在途件全程未吸收未复位（白名单提交隔离）。

## 3. 提交清单（每批 git log -1 --name-only 核归属=零吸收）
| 批 | commit | 内容 |
|---|---|---|
| W1-A0 | 9949f018b5 | #355 generate_missing_index_md 相对路径修复（红证双向，主区 1080 目录实测） |
| W1-B | 745d6491b0 | #345a/b+#352 口径批（--tracked-only×3 台+TEMP 4 类+编码 fail-closed；85 tests） |
| W1-B2 | b5bc9f820f | #357 check_index_integrity 判据重造+cross-ref file:///（5→2 fixture 红证） |
| X-7 | d49aed6ddf | top10_shareholders 断供修复+补齐（20260630 报告期 0→99.93% 覆盖，幂等 Δ=0） |
| W6 | e77d0b13ba | api_server StaticFiles 一体化+壳入口切 8890+描述同步（404→200 双向） |
| W1-C1 | 6afa21fe08/d06103b716/a046ac41e7 | #358 WP11 五点+#360a 断链豁免面（4→0 warning） |
| W1-C2 | 1192d9cc8e | #353②③ LSG 配置化+网关引号路径解析（102+552+1220 tests） |
| W1-D1 | 0cc6e87618 | #351 gate_auto_registrar fail-closed（113/113 预检健康，26 tests） |
| W1-D2 | aca8c71fad | #354+#341+#342（九台 --full-tree+计划任务+网关 pre-commit 通道 own-scope+enforcement_channel 55/113/1） |
| W1-D3 | 39ae8d2443 | #343 CAS 写入端退避治本+删除包 dry-run 清单 65 件/87.88MB（**删除待 Max 复验**） |
| W1-E | 7a63b93dee/dadf6cc077/d2c242cf9d/52781e8672/1cfcaca8e4/5309963076/16218b1b56/4a651a9552 | #356 index.md 800 件（债务口径 230 全清+闭包口径） |
| W1-A1 | c2900f1115/b39ab7f614 | WP8 案卷 v2 1404 份（闸1 962→142/闸3 948→5/分母 0→1025，判案归 Max） |
| X-1 | 98b055acc6/8b056db496 | 死信三分法清账：purge 912/requeue 0/REVIEW 124（清单+归档在案） |

## 4. working C 类剩余计数趋势线（S7 硬门禁）
| 时点 | C+C-3 | 说明 |
|---|---|---|
| 2026-09-19（W8-0 基线） | **131** | 重扫 177 对象=A14/B3/C126/C-3:5/D19/E4/P6；基线审查 164 对象 A24/B4/C112/D20/E4 的散文件 A10 无法机械恢复并入 C（台账头有漂移说明） |

## 5. 战线状态板（滚动）
- W1：A0/A1/B/C/D/E 全落地；**剩余=F 批（判案归 Max，v2 案卷已备）+G(#359 施工)+H(身份键 st-ramp-wp1b 件+工棚收尾)+RA-H2 机械波（另开便宜会话）**。#342 B①停手上交（src/zephyr/data/=合法模块 MOD-L00-001，字面扩前缀将冻结数据域→待 Owner 新裁定）。
- W2：BM-1 判定=接手（bizmine2 死）；P0 T1-T5 未动（骨架产物 staged 待收尾）；BM-3 等 X-0。
- W3：X-1✅ X-7✅；X-0（本会话在办）；X-2 复权链（【M】预注册先行）；X-3/X-5/X-6 待。
- W4：未开（W4-1 三分法/W4-7 TDM 吸收批待派）。
- W5：未开（W5-0 盘点待派）。
- W6：W6-1/2✅；W6-3【O】备料在案（壳=Electron 实测修正：tools/desktop/main.js，非 WebView2）。
- W7：未开（前置 X-7✅ 已解锁建表批）。
- W8：W8-0✅（本台账+台账落盘）；W8-5✅；W8-1【O】待签字（归档清单=台账 A14+B3 行）；W8-2/W8-3/W8-4 待。
- W9-6/W9：未开。

## 6. 待 Max 复验清单（五关卡）
1. **#343①③ 删除包执行**：dry-run 清单 .runtime/tmp/x343_deletion_manifest.txt（65 件/87.88MB，已排除 .git 内 86 件与 .worktrees）——Max 复验后由总包执行删除。
2. W1-F 判案：v2 案卷 1404 份在 .runtime/sessions/st-final3-20260919/staging/dossiers_v2/（闸5 判决+5 归档/7 真删逐条终判）。
3. W1-G(#359) 施工后红证验收。
4. X-2 复权链预注册修复方案。
5. W4-7 TDM 吸收批差距表。

## 7. 待 Owner 签字清单（W8-3 汇拢中）
1. W8-1 归档批（28→台账实测 A14 目录+B3 件+可核 A 散件）批量移动。
2. #342 B①：src/zephyr/data/ 前缀扩面新裁定（或豁免 MOD-L00-001）。
3. W4-2 ig bak 90 表清理；W4-6/W6-3 服务自启+看门狗。
4. kimi_audit S3 96 条+szopen 28 接口地址（打包成册送签）。
5. W9-6③ 两条裁定尾巴终裁（sowner002-regime-switcher 并入 or 废弃 / tv2terrain 同）。

## 8. 停手/回执遗留汇总
- W1-D2：#342 B①停手（见上）；GATE-21 manifest 秒级竞态窗口待裁定。
- W1-E：10_trading_map 目录契约不含 index（DCR-001）待 Owner；check_index_integrity LOW 588→1500=生成器平铺 vs 校验器递归口径矛盾（advisory）。
- W1-D1：fail_open_register 派生册 DRIFT 早于本批（含他会话 WIP），留例行重生成。
- X-7：4 只缺席股（源侧无数据）+2025Q4/Q3 覆盖率为 bdpan 时代旧债+调度器进程重启依赖动作。
- 环境预存告警：RECONCILER-HEALTH SECRET-REGISTRY-DRIFT（REDIS 三键）、DEPGRAPH-FRESHNESS。
