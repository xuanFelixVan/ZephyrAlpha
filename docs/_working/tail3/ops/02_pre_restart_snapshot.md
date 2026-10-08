---
created: 2026-10-08
session: st-t3c-ops
ttl: task_bound
completes_when: 裁定③低峰窗处置随袋取证件（快照/心跳），随 01 诊断报告归档即闭环
---

# 02_pre_restart_snapshot — ZephyrAlpha_PostSettlement 重启处置前状态快照
# 采集时间: 2026-10-08 03:24:58 +0800
# 处置上下文: 车道C(st-t3c-ops) 低峰窗重启检查——若任务已健康则不重复重启(取证即裁定意图达成)


文件夹: \
主机名:                             范清风
任务名:                             \ZephyrAlpha_PostSettlement
下次运行时间:                       2026/10/8 15:30:00
模式:                               就绪
登录状态:                           只使用交互方式
上次运行时间:                       2026/10/7 15:30:00
上次结果:                           0
创建者:                             N/A
要运行的任务:                       C:\Windows\System32\conhost.exe --headless -- "C:\Windows\System32\cmd.exe" /c cd /d "D:\ZephyrAlpha" && "C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe" -u "D:\ZephyrAlpha\scripts\run_post_settlement.py" >> "D:\ZephyrAlpha\data\runti
起始于:                             D:\ZephyrAlpha
注释:                               N/A
计划任务状态:                       已启用
空闲时间:                           已禁用
电源管理:                           
作为用户运行:                       fanzi
删除没有计划的任务:                 已禁用
如果运行了 X 小时 X 分钟，停止任务: 00:30:00
计划:                               计划数据在此格式中不可用。
计划类型:                           每周
开始时间:                           15:30:00
开始日期:                           2026/10/5
结束日期:                           N/A
天:                                 MON，TUE，WED，THU，FRI
月:                                 每 1 周
重复: 每:                           已禁用
重复: 截止: 时间:                   已禁用
重复: 截止: 持续时间:               已禁用
重复: 如果还在运行，停止:           已禁用

=== XML 定义 ===
<?xml version="1.0" encoding="UTF-16"?>

<Task version="1.3" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">

  <RegistrationInfo>

    <URI>\ZephyrAlpha_PostSettlement</URI>

  </RegistrationInfo>

  <Principals>

    <Principal id="Author">

      <UserId>S-1-5-21-2457011696-187744368-63685291-1001</UserId>

      <LogonType>InteractiveToken</LogonType>

    </Principal>

  </Principals>

  <Settings>

    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>

    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>

    <ExecutionTimeLimit>PT30M</ExecutionTimeLimit>

    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>

    <StartWhenAvailable>true</StartWhenAvailable>

    <IdleSettings>

      <Duration>PT10M</Duration>

      <WaitTimeout>PT1H</WaitTimeout>

      <StopOnIdleEnd>true</StopOnIdleEnd>

      <RestartOnIdle>false</RestartOnIdle>

    </IdleSettings>

    <UseUnifiedSchedulingEngine>true</UseUnifiedSchedulingEngine>

  </Settings>

  <Triggers>

    <CalendarTrigger>

      <StartBoundary>2026-10-05T15:30:00+08:00</StartBoundary>

      <ScheduleByWeek>

        <WeeksInterval>1</WeeksInterval>

        <DaysOfWeek>

          <Monday />

          <Tuesday />

          <Wednesday />

          <Thursday />

          <Friday />

        </DaysOfWeek>

      </ScheduleByWeek>

    </CalendarTrigger>

  </Triggers>

  <Actions Context="Author">

    <Exec>

      <Command>C:\Windows\System32\conhost.exe</Command>

      <Arguments>--headless -- "C:\Windows\System32\cmd.exe" /c cd /d "D:\ZephyrAlpha" &amp;&amp; "C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe" -u "D:\ZephyrAlpha\scripts\run_post_settlement.py" &gt;&gt; "D:\ZephyrAlpha\data\runtime\post_settlement_last_run.log" 2&gt;&amp;1</Arguments>

      <WorkingDirectory>D:\ZephyrAlpha</WorkingDirectory>

    </Exec>

  </Actions>

</Task>
=== 关键文件存在性核验 ===
-rw-r--r-- 1 fanzi 197609 14017 Oct  7 15:30 data/runtime/post_settlement_last_run.log
-rw-r--r-- 1 fanzi 197609 37064 Oct  4 07:48 scripts/run_post_settlement.py
-rwxr-xr-x 1 fanzi 197609 104952 Dec  3  2024 /c/Users/fanzi/AppData/Local/Programs/Python/Python312/python.exe

=== 日志尾块(最后3行) ===
[标注] 日终审计输入=空快照最小输入（持仓/净值/限额真源未接线，57 号文 GAP 族后续批）
[标注] VaR 回测定级：跳过（状态根 D:\ZephyrAlpha\data\runtime\state 无盘前基线归档——编排层未在此根跑过，预测腿零来源，绝不拿空归档伪造定级）
[INFO] exit_code=0（0=OK/SKIPPED, 3=DRIFT, 1=ERROR）
