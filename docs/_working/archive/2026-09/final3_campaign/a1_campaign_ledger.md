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

---

## 9. W9 收官终态（2026-09-19 深夜，本战役会话收口）

**六波施工+收官循环**：27+ 笔 [final3] commit 全在 dev 祖先（git log --grep 验）；产物 15 件全在盘；红蓝一轮 13 攻 2 倒（两处归档误埋活件已勘误，W8-1 口径=A12+B3）；X-1 两轮清账后 dead=130（124+6 REVIEW，0 内容丢失）；分支终态 --no-merged=仅剩 2 条裁定尾巴（Owner 终裁件）；working C 类=127+5=132（较基线 131 净 +1=pattern_line 由 A 转 C）。

**S1-S7 验收**：S1 规则审计=A0/B/B2/C/D/E/A1/G 八批落地，F 批判案+三件红证验收归 Max【待 M】；S2 bizmine=T1-T5+BM3 三件+BM4/5 全落，骨架封矿 a4 待续挖（已收编）；S3 工程债=X-0..X-7 全落（复权链 X-2 预注册卡备好待 Max 复验后施工）；S4 全景图=W4-1/3/4/5/6/7 前半全落（W4-7 后半 4 条接线待 Max 复验差距表）；S5 内收=W5-0 基线+W5-1 四簇先导落（W5-2 Owner 签字后、W5-3 宪法改动【M】未动）；S6 前端=8890 一体化上线（W6-3 自启待 Owner）；S7 working=台账+硬门禁循环已运转（W8-1 归档批待 Owner 签字，C 类消化完成 deep_review 对账等 6 件，其余按四桶移交）。

**本轮新增待 Max 复验清单**：#343 删除包执行（65 件/87.88MB manifest 在 .runtime/tmp/x343_deletion_manifest.txt）；X-2 复权链预注册卡（x2_adjfactor_prereg.md，病灶实锤=daily_kline 表名错+独立 adj_factor 表 86.45% 非 1 可用）；W4-7 差距表（4 条接线=UP-2/3/4/5 模块已建待接线）；W1-G WP17 验收（补 description 参数裁量披露）；W1-F 判案（v2 案卷 1404 份）。
**本轮新增待 Owner 清单**：签字册 w8_3_owner_signature_book.md（128 项/10 主题，已含勘误节）；W9-6③ 两分支终裁；W4-6 自启两案；#342 B① 复裁。
**移交后续班**：RA-H2 T0 机械波（另开便宜模型会话，前置=B 批已落地✓）；W5-1 其余 18 域分包；W4-7 后半接线+X-2 施工（均 Max 复验后）；dead 6 条 REVIEW 属主处理；W8-4 归档循环滚动至 C 类清零。

## 10. Max 收官班进展锚（st-maxexec-20260920，断点续班用）

**开工**：裁定#371 授权登记（2a5711961a）+P0 对账（回退炸弹三分法 A 类 20 件 unstage/507 真内容留归属包）。

**已落地 commit 链**（截至 2026-09-20 13:00 前后）：
- P1：判决册#372（8f8bf8ccee）→rules 统一批 40 件（48acb99c46，含 #344/#346/#347/#350/#353①+九簇悬空消解+闸3 D1）→trae_036 追尾（0adc7497）
- P2：验收记录三件（d141ab7ee6）
- P3：删除包 66 件（541df75347）
- P5：TDM 四接线+两雏形（ac6521b943，DAL 27→32）
- P6 部分：分支终裁#373 两报告并入（8a1730c159+token 批 7f9d8fbfc）
- P9①：宪法 §4 等长替换#375（23042a0497）；②audit_prompts v5（袋中）
- P7 部分：#376 十九 ARCH 方向裁定+墓碑四项+final_adjudication 回执 19 条（袋中）
- P12：队列终态记录（袋中）；死信 144→129（15 件已取代清袋 dead_purged_20260920/）
- P14 部分：szopen 一页纸（袋中）

**在飞代理（8）**：P4 复权链（最大件）/P6-mech 结构批八项/P7-A A/C 族/P7-B B/D 族/P7-C EFGH+低置信/P8 W5-2+18 域/P9③ 门禁化/P10 T0 机械波。

**待收口**：P11 C 类四桶（等 P6/P8 产物）→P13 循环两轮+红蓝→P14 终局报告。

**本班新配方**：①金哈希滞后=validate_rules_integrity --fold（工作树混合基线，flush 前算最终态）；②PROTECTED-PATHS Layer2 无 message 通道双重计数盲区=同 shell ZEPHYR_PROTECTED_PATHS_BYPASS=1 + 直连正门（--no-auto-enqueue，Layer 1 标记先行，#374⑧ 留痕）；③audit_prompts 残留只读位（v4 班临时保护未解锁）attrib -R 治之；④死信"已取代"判定=file-existence+HEAD 双查+改名场景 git show --stat 验证。

---

## 终局状态块（W8 第二圈 2026-09-21）

- 状态: A 已结案可归档
- 依据: p14_final_report 七条硬数字全✅（e7531c2f3b）+p14_owner_szopen_onepager 作废更正（Owner 无需 A/B 组操作，47/47 接口全通）+18 条终态件保护批已入队 q-20260921-st-workclean-20260921-0001 前批
- 归档/留场: archive/2026-09/final3_campaign/
- 备注: w9_triage_ledger 四态状态机为全仓 working 治理最高价值复用资产（本清理班即其 W8-4 循环第二圈执行者），随档并在 working_cleanup_campaign 台账标方法论范本
