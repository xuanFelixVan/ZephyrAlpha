---
ttl: task_bound
title: L09 案卷 F85 — 环境与启动链（冷启动三步/windows_service/desktop shell/AI wrapper 注入）
session: zc-l09-20260927
---

# F85 环境与启动链（I 段 S10，骨架态=partial/P1）

## 一、六向台账（2026-09-27 实证）

| 向 | 实测证据 |
|---|---|
| 上游输入 | F76 计划任务群（96 实体）；Python 3.12 PATH 修正前置（宪法 §0 RULE-ENV，本会话冷启动已验证 3.12.8） |
| 下游消费 | 全链（启动链是底板）；desktop shell→Electron 前端（F111 面） |
| 自动化触发 | `scripts/register_desktop_shell_startup.ps1`（头部自述"Register the ZephyrAlpha Electron desktop shell to start at user logon"实存）；`ZephyrAlpha-AI-Wrapper-Inject` PT1M one-shot 补注射（M5：Running，历史僵尸 0x800710E0 已清） |
| 真源与注册表 | `src/zephyr/trading/windows_service.py`（头 [STARTUP] manual/[CONSUMERS] 空，实存）；注册脚本族 scripts/register_*.ps1 |
| 门禁与质量尺 | M5 04 册 S10 已修史（powershell 闪窗风暴→wscript+launch_hidden.vbs 十任务统一）；AI-Wrapper-Inject 僵尸清理在案 |
| 当前运行状态 | **黄**：desktop shell 启动脚本+AI wrapper 注入任务在岗（M5 基线绿）；windows_service 本体 manual 态、[CONSUMERS] 空=服务化路径建成未消费 |

## 二、子模块三级枚举

1. 冷启动三步（宪法 §0）：RULE-ENV PATH 修正→RULE-GUARDIAN reaper 探活→RULE-WORKTREE 会话化；本会话步 1 实测通过（python 3.12.8）。
2. `windows_service.py`（MOD 域=D_INFRA_RUNTIME 系）：Windows 服务化封装，[STARTUP] manual——按需手动安装，非出厂常驻。
3. `register_desktop_shell_startup.ps1`：Electron 桌面壳登录自启注册（Logon 触发器路线）。
4. AI-Wrapper-Inject 计划任务：PT1M one-shot 补注射 toolhost 快照（M5 02 册 §七实证 Running）。
5. 依赖放错区已修史族：RestartMiniQmt/NightlySentiment 0x80070002/TraeCacheCleanup（M5 04 册 §三.4 横断模式登记）。

## 三、接线四态独立复核

- **desktop shell 自启=已接线**（注册脚本实存+M5 基线在岗）。
- **AI wrapper 注入=已接线**（PT1M 任务 Running，M5 05 册 #10 基线绿）。
- **windows_service=建成未接线**：[STARTUP] manual+[CONSUMERS] 空，全仓无服务安装登记证据——服务化路线挂起态。
- **usercustomize 引导链=缺失**（F88 DP-2 交叉）：启动链不含 usercustomize 存在性校验（接续收口01 修法草案①的冷启动序列增行尚未落地）——本日复核 usercustomize 仍不存在。

## 骨架勘误

1. 骨架"partial（M5 补挖项）"成立；细化缺口定性：**partial 的实体=windows_service manual 挂起+启动链缺 usercustomize 校验行**，desktop shell 与 wrapper 注入两腿实为绿。
2. 交叉新发现：宪法 §0 冷启动序列与 F88 DP-1/DP-2 修复建议（增 usercustomize 校验行）尚未回灌宪法——两处登记需对齐（归治理面，本卷只登记）。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | 启动链无 usercustomize/拦截器在岗自证 | 采纳接续收口01 修法①：冷启动序列增一行+AutoRuntime 启动 is_installed() 告警 | P1 |
| 2 | windows_service 服务化路线悬置 | Owner 定向：转正式服务 or 退役登记（净零） | P2 |
| 3 | [CONSUMERS] 空的头部声明漂移（windows_service） | 随批次补登记 | P2 |

## 五、自审闸三态

**挖干（脚本/任务/头注/进程四向锚点）✅；待裁（缺口#2 服务化去留）；windows_service 内部逐函数深挖未做（manual 态低价值），登记为有意不挖。**

## 六、复跑命令

```bash
grep -E "STARTUP|CONSUMERS" src/zephyr/trading/windows_service.py | head -2
head -3 scripts/register_desktop_shell_startup.ps1
schtasks /query /tn ZephyrAlpha-AI-Wrapper-Inject /v /fo LIST | grep -E "Status|Last Result"
python -c "import site,os;print(os.path.exists(os.path.join(site.getusersitepackages(),'usercustomize.py')))"  # False=缺口1在
```
