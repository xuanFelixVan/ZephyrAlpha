---
ttl: task_bound
completes_when: 统筹验收本册＋day2-day7 影子由周期班续跑满 7 日零异常转正；移交三线被承接
---
# 终清波三·收班册 99_delivery（sid=st-fclean3-20261012，2026-10-12 18:4x）

> 统筹批复（15:5x 两菜单）＝菜单一 A **只接本班收到收班**；菜单二 A 矿考开账**只报不动**、系统性部分并案维护三班。本册即收班交付。
> 北极星对照（Owner 通宵令 §〇）："附属物 63.4GB 存量每面有主有据" ⇒ 本班把该面从**工令点名的 8 面**推到 **101/102 面有主有据**（缺 1 面＝嵌套 `.runtime`，本班按内容级实测自判态④留证，见 §五-2）。

## 一、目标三件终态

| 目标 | 终态 | 凭据 |
|---|---|---|
| 案卷全出品 | **达**：7 份车道案卷＋5 本册（P1 分账／机械面＋影子／交接卡／晨间包／本册） | dev 上 `wave3/` 已 15 件；车道 `lanes/` 7 份（aidrafts 441 行、untracked_audit 437、face_ownership 361、tmp_lanes 224、deadletter 251、quarantine 260、consumers） |
| 机械面清零 | **达（按判据，非按数量）**：真删 46 个零文件目录；69 空壳中 22 无文件树＋43 真壳＝46 清、其余 22 面因代码面读者＞0 全态④留；`.runtime` 根 22 枚散件**零删除**（14 在飞锁与缓存∧5 查无写者不可证可再生∧1 有独有字节）；嵌套 `.runtime` 整面态④ | 清单 sha256 `0b0cae988df22cca4767662b0f01a1e882a7ababb6b03ec8868fc42008065f7a`；回执 deleted=46／failed=0／复存=0；散件内容证据 `out/p2_root_files_content_evidence.json`（22 件 sha／行数／首尾） |
| 孤儿壳影子归档在跑 | **达**：day1 五轮全 PASS（`mode=shadow∧errors=0∧suspected=0∧命中在飞=0`）；原证已搬入非 TTL 安全区；日检交周期班 | `.runtime/quarantine/fclean3_safety/shadow_rounds/`（5 份＋raw sha 入册）；`27_...yaml` 观测账；`23_` 交接卡（脚本本班实跑通过） |

## 二、九袋账（只认 HEAD，含两笔死信）

| 袋 | 内容 | 终态 | 备注 |
|---|---|---|---|
| q-0001 | P1 首袋 6 件 | **done** | 落地面 13 件验真、零空件 |
| q-0002 | 机械面＋影子＋2 案卷 | **done** | |
| q-0003 | 影子日检交接卡 | **done** | |
| q-0004 | 晨间包＋面产权册＋`00_ledger` 纯追加 | **done** | `00_ledger` 对 616 基线**删除行=0**（落地面复验） |
| q-0005 | 卡位观测登记 | **done** | 内容后被 §四-1 更正 |
| q-0006 | M2 闸①七件（含矿考 yaml） | **dead** | 死因＝`TAKEOVER-PENDING` 命中矿考 open 接管条目 ⇒ **门拦得对**；不 requeue（内容由 q-0008 摘件替代） |
| q-0007 | 影子观测账 v1 | **done** | 其『四轮全等』范围过宽，由 `29_` 附录更正（仅限同日）；day1 实为五轮 |
| q-0008 | M2 闸①六件（摘出矿考件）＋广播条文 | **done** | regsolo t1..t4（frontmatter-only，双 sha 入册）＋dexp 移交单＋`26_` |
| q-0009 | 观测账 v2（复投同件 27_） | **dead** | 死因＝`landing 异常: 非注册表族件双侧皆改真冲突` ⇒ **本班方法错误**（见 §四-4）；根因＝base_head 是车道旧 HEAD 非 dev，超集式失效 |

| q-0010 | 收班袋（27_ 重建＋28_） | **dead** | 同因再死一次（27_ 仍在袋内）⇒ 证"超集式"在车道落后 dev 时彻底失效；本袋改走 28_＋`29_` 新文件路线，27_ 不再入袋 |
`dead/` 内本班命中 3 笔（0006／0009，以及本册所在袋之前一次同因失败），**均非幽灵烧袋**：0006 是门拦得对（他班开账连坐），0009 与后续同因袋是**本班方法错误**（同件复投撞三方）。0006 走摘件替代（q-0008 已落），0009 走换新文件追加册（`29_`）。

## 三、净零申报

- **新增永久面＝0**：未新建门禁／规则／注册表／第二套判据／第二个影子观测面。字节对拍全部复用波二 `scan_dev_delta.py` 四原语（`importlib` 导入，未执行该文件）。
- 悬挂账三条，全部如实留在册、无自我销账：
  1. 4 条指向从未落地路径的 creation_token（`REG-CAPCAN-001/creation_tokens`，坐标见 P1 §六）——`retire()` 需 `authority_ref`，本班无凭据、不自造，**统筹已转维护三班**；
  2. `99_delivery.md`（regsolo 终报）**仍未落**：其 `:155` 引用 `ARCH-383`，YAML 真源尾号止于 382、PG 无 architecture_issues 表 ⇒ 真悬空。同段其余断言本班已验真（`裁定#504` 在册、commit `7ff589652f` 为 dev 祖先）。**不自造注册表条目、不改他班正文**，交属主线处置；
  3. 本班曾用**车道副本**跑 token 的 publish/render，致车道热册 `capability_canonical_file_registry.yaml` 呈 M——已按 `git show dev:` 字节复位（恢复后 sha 与 dev 全等），未入任何袋（守"禁出重打投影袋"）。

## 四、⚑ 本班自犯五起（全留案，无一遮蔽）

1. **"只读探测"实为执行写盘**：波二 27 支工具 22 支无 argparse，`--help` 即跑主逻辑 ⇒ 误删他人分支（已按存证 sha `15b147066e…` 复原且为 dev 祖先）＋幂等覆写 793 枚受保护存证件（**788/788 sha 全等**，坏的只是 mtime 证据）。
2. **把兼容副本滞后误归因于自己的整表写**，并以"`_save` merge-upsert 永不删"为其开脱——该论断后被自己的二次实测作废（见 3）。
3. **mutating 探针**：`list_active()` 缺省 `mutating=True`＝判死即写接管台账＋`_delete_shard:1048-1054` 删片并 `legacy.pop` 整表重写兼容副本（宽限 900s）。归因上限＝机制确证∧时刻吻合∧**计数不可追认**（`_write_legacy_raw` 不经 `safe_write_text`⇒无写者审计面）。后果实测仍为零。广播四条纪律已入 `26_` §三并被统筹采纳。
4. **明知同会话后袋吞前件的在册坑，仍用"严格超集复投同件"救观测账** ⇒ q-0009 直接撞 `三方真冲突` 死信。正解＝**先取 dev 现字节为基做纯追加**（本袋已照此重建，dev 原文为前缀、删除行=0）。教训：**在册坑写进记忆不等于已被遵守**，动手前须回查该条而不是沿用直觉配方。
5. **`lock_files.py release` 参数序写反**（应 `release <file> <owner>`），首次得 NOT FOUND 后误判"未被锁定"。

## 五、移交三线（统筹 15:5x 已定归属，本班只交代出口）

- **→ 矿考二班 `st-mineloop2-20261012`（双臂线法定接棒人，正在跑）**：`docs/_working/mineloop_campaign/10_exam_recast_quintile.yaml` 由属主重投。三处字节对拍**全等** `8754f823120d2e668325d772cec8a006f87bfbeef593aa6a76cd123cd6c48744`（车道副本／安全区／属主原树），凭据 `.runtime/quarantine/fclean3_safety/mineloop_handoff/HANDOFF.json`；本班已把该件**摘出车道**，防后续袋误吞他班属主件。矿考前任 `st-mineloop-20261010` 的开账（dirty=107、心跳断、15:22 立案）按裁定**只报不动**，个案归二班处置。
- **→ 维护三班（活性族／队列完整性簇，统筹已并案）**：①`st-dexp-20261009.json` 分片 JSON 损坏（读侧 skip＋warn ⇒ 会话隐形、可被误判死）；②接管台账 **188 条 status 全为 open**，而销账走 `.runtime/takeover/resolved/` 目录面 ⇒ **开账/销账两面不同源**；③`processing` 占位者身份与年龄须可与 done/dead 对账（袋体无 `claimed_by/attempt/state` 字段）；④`session_registry/*.tmp` 崩溃残件 8 枚（27.6%）；⑤GATE-RUNTIME-CLEANUP 吃文件须留一行审计（哪个闸／何时／sha）——本班已冻 22 枚散件内容证据兜底，其中 3 枚将于 10-13/10-15/10-18 到期即无声消失；⑥M2 闸②：`git worktree remove` 前逐棵核在飞引用＋`ahead` 分支逐 commit 四态判读；⑦4 条悬挂 token retire；⑧`.runtime/locks`↔根 `.ailocks` 与兼容副本↔分片真源两组双轨；⑨M13 六面写者未定位（正属"写者署名"闸作业面）。
- **→ Owner 门位（未动，等裁）**：only-copy 死信 1,425 袋/2.61GB（dedup 1.10GB）∧ tmp C2 业务资产 49.88 GiB；两份未纳管明文密钥副本（`.aidrafts/st-regsolo-20261010/config/.env.{clickhouse,postgres}`，与主仓 sha 全等）；`gate_audit`/`audit` 缩容＝删生产审计件（且应先扩取证窗，现仅 3.7d/0.7d）；波二 C 件"照批清"批文原话未验（执行自洽度已证，授权面待一句结案）。

## 六、余下唯一未闭合项与复算入口

**day2–day7 影子**（10-13 至 10-18，每日至少一轮）由周期班/维护三班按 `23_` 卡续跑；满 7 个自然日零异常＋统筹签认后才转真 mv，**计划任务注册与转正同批定**。跨轮比较口径已更正为 `would_n ＋ new/gone 差集`（同日才可用 `would_set_sha256` 全等）。

```bash
# —— 落地核验（只认 HEAD）——
git -C /d/ZephyrAlpha log --oneline -- docs/_working/finalclean2_campaign/wave3/
git -C /d/ZephyrAlpha ls-tree -r --name-only dev | grep -c finalclean2_campaign/wave3      # 期望 ≥15
git -C /d/ZephyrAlpha show dev:docs/_working/finalclean2_campaign/00_ledger.md | wc -l     # 期望 628＋追加分支
python -c "import subprocess,hashlib;d=subprocess.run(['git','-C',r'D:/ZephyrAlpha','show','dev:docs/_working/finalclean2_campaign/00_ledger.md'],capture_output=True,text=True).stdout;print('rows',len(d.splitlines()),'波三十四节' , '## 十四、波三' in d)"
# —— 机械面与存证完好 ——
python -c "import json,pathlib;d=json.loads(pathlib.Path(r'D:/ZephyrAlpha/.runtime/tmp/st-fclean3-20261012/out/p2_delete_receipt.json').read_text(encoding='utf-8'));R=pathlib.Path(r'D:/ZephyrAlpha/.runtime');print('deleted',len(d['deleted']),'复存',len([t for t in d['deleted'] if (R/t).exists()]))"
python -c "import json,hashlib,pathlib;S=pathlib.Path(r'D:/ZephyrAlpha/.runtime/quarantine/fclean3_safety/aidrafts_irreplaceable');m=[json.loads(l) for l in (S/'MANIFEST.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()];bc=[r for r in m if r['mode']=='byte_copy'];print('byte_copy',len(bc),'sha_ok',sum(1 for r in bc if hashlib.sha256((S/r['sid']/r['rel']).read_bytes()).hexdigest()==r['sha256']))"
# —— 矿考件移交三处对拍（属主重投前勿动）——
python -c "import json,pathlib;h=json.loads(pathlib.Path(r'D:/ZephyrAlpha/.runtime/quarantine/fclean3_safety/mineloop_handoff/HANDOFF.json').read_text(encoding='utf-8'));print(h['sha256_safety'][:16],h['three_way_equal'],h['to'][:20])"
# —— 影子日检（day2 起，禁加 --execute；活死判定只用 list_active_readonly）——
python scripts/governance/_tasks/session_closeout_reconciler.py --dry-run --json > .runtime/tmp/st-fclean3-20261012/out/shadow_round6.json
```
