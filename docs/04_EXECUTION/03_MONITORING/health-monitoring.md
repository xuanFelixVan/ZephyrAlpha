---
module_id: 04_EXECUTION_03_MONITORING_HEALTH_MONITORING
layer: layer_04
version: 1.0.0
status: Active
responsibility:
  - Health Monitoring相关业务
created_date: 2026-04-01
last_updated: 2026-04-07
owner: 首席文档架构?
standard_type: 专业量化机构交易执行标准
applicable_scope: 交易执行与监控
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行?
---

## 1. 为什么需要健康监控



```

?监督) ?AI(执行) ?AI(优化) ??监督) ?AI(报告)



系统可能出问题：

- 服务崩溃

- 数据未更?

- 磁盘空间不足

- 任务执行失败



?AI自动检测并告警，人只需处理异常

```



```
```---
```



## 2. 简化监控架?



```python

class SimpleHealthCheck:

    """简化健康检?- 1?AI版本"""



    def __init__(self):

        self.checks = [

            self.check_processes,      # 进程检?

            self.check_data_fresh,    # 数据新鲜?

            self.check_disk_space,     # 磁盘空间

            self.check_error_logs,     # 错误日志

            self.check_pipeline_status # 流水线状?

        ]



    def check_all(self) -> HealthReport:

        """执行所有检?""

        results = []

        for check in self.checks:

            result = check()

            results.append(result)



        return HealthReport(

            timestamp=datetime.now(),

            checks=results,

            status='HEALTHY' if all(r.ok for r in results) else 'UNHEALTHY'

        )

```



```
```---
```



## 3. 检查项定义



### 3.1 进程检查



```python

def check_processes(self) -> CheckResult:

    """检查关键进程是否存?""

    critical_processes = [

        'data_pipeline',    # 数据流水?

        'strategy_engine',  # 策略引擎

        'execution_agent',   # 执行Agent

        'ai_research_agent' # AI研究Agent

    ]



    failed = []

    for process in critical_processes:

        if not self._is_process_running(process):

            failed.append(process)



    return CheckResult(

        name='process_check',

        ok=len(failed) == 0,

        message=f"Failed processes: {failed}" if failed else "All processes running"

    )



def _is_process_running(self, process_name: str) -> bool:

    """检查进程是否运?""

    # 使用 psutil 或系统命令检?

    return True  # 简化实?

```



### 3.2 数据新鲜度检查



```python

def check_data_fresh(self) -> CheckResult:

    """检查数据是否是最新的"""

    import os



    data_files = {

        'daily_ohlcv': 'data/daily_ohlcv.parquet',

        'realtime_cache': 'data/realtime_quote.json'

    }



    stale_data = []

    for name, path in data_files.items():

        if not os.path.exists(path):

            stale_data.append(name)

            continue



        mtime = os.path.getmtime(path)

        age_hours = (time.time() - mtime) / 3600



        # 日线数据应该在收盘后2小时内更?

        if age_hours > 26:

            stale_data.append(f"{name}({age_hours:.1f}h)")



    return CheckResult(

        name='data_fresh',

        ok=len(stale_data) == 0,

        message=f"Stale data: {stale_data}" if stale_data else "All data fresh"

    )

```



### 3.3 磁盘空间检查



```python

def check_disk_space(self) -> CheckResult:

    """检查磁盘空?""

    import shutil



    # 检查根目录和data目录

    paths_to_check = ['/', 'D:/']



    low_space = []

    for path in paths_to_check:

        usage = shutil.disk_usage(path)

        free_gb = usage.free / (1024**3)

        if free_gb < 10:  # 少于10GB告警

            low_space.append(f"{path}: {free_gb:.1f}GB")



    return CheckResult(

        name='disk_space',

        ok=len(low_space) == 0,

        message=f"Low space: {low_space}" if low_space else f"Space OK"

    )

```



### 3.4 错误日志检查



```python

def check_error_logs(self) -> CheckResult:

    """检查最近错误日?""

    import os



    log_file = 'logs/error.log'

    if not os.path.exists(log_file):

        return CheckResult(name='error_logs', ok=True, message="No error log")



    # 读取最?小时的错?

    with open(log_file, 'r') as f:

        lines = f.readlines()



    recent_errors = []

    cutoff = time.time() - 3600  # 1小时?



    for line in lines[-100:]:  # 只检查最?00?

        if 'ERROR' in line:

            try:

                timestamp = self._parse_log_timestamp(line)

                if timestamp > cutoff:

                    recent_errors.append(line.strip())

            except:

                pass



    return CheckResult(

        name='error_logs',

        ok=len(recent_errors) < 10,  # 少于10个错误认为正?

        message=f"Recent errors: {len(recent_errors)}" if recent_errors else "No recent errors"

    )

```



### 3.5 流水线状态检查



```python

def check_pipeline_status(self) -> CheckResult:

    """检查今日流水线是否正常完成"""

    expected_tasks = {

        'morning_pipeline': {'expected_by': '09:30', 'completed': False},

        'realtime_monitor': {'expected_by': '15:00', 'completed': False},

        'afterhours_pipeline': {'expected_by': '20:00', 'completed': False},

        'night_pipeline': {'expected_by': '06:00', 'completed': False}

    }



    current_time = datetime.now().strftime('%H:%M')

    failed_tasks = []



    for task_name, config in expected_tasks.items():

        if not config['completed']:

            # 如果已过预期时间但未完成

            if current_time > config['expected_by']:

                failed_tasks.append(task_name)



    return CheckResult(

        name='pipeline_status',

        ok=len(failed_tasks) == 0,

        message=f"Pending tasks: {failed_tasks}" if failed_tasks else "All pipelines completed"

    )

```



```
```---
```



## 4. 自动告警



```python

class SimpleAlertManager:

    """简化告警管?""



    def __init__(self):

        self.alert_history = []



    def send_alert(self, level: str, message: str):

        """发送告?""

        alert = Alert(

            timestamp=datetime.now(),

            level=level,

            message=message

        )

        self.alert_history.append(alert)



        # 简化实现：打印到控制台

        # 实际可用：send to WeChat / Email / SMS

        print(f"[{level}] {message}")



    def should_alert(self, result: CheckResult) -> bool:

        """判断是否需要告?""

        if not result.ok:

            # 首次失败不告警（可能是临时问题）

            if self._is_first_failure(result.name):

                return False

            # 连续失败才告?

            return self._consecutive_failures(result.name) >= 2

        else:

            # 恢复时发送恢复通知

            if self._was_failing(result.name):

                self.send_alert('INFO', f"{result.name} recovered")

            self._clear_failures(result.name)

            return False

```



```
```---
```



## 5. 定时执行



```python

class MonitorScheduler:

    """监控调度?""



    def __init__(self, health_check: SimpleHealthCheck,

                 alert_manager: SimpleAlertManager):

        self.health_check = health_check

        self.alert_manager = alert_manager



    def run_periodic_check(self, interval_minutes: int = 30):

        """定时执行健康检?""

        while True:

            report = self.health_check.check_all()



            if report.status == 'UNHEALTHY':

                for result in report.checks:

                    if self.alert_manager.should_alert(result):

                        self.alert_manager.send_alert('WARNING', result.message)



            # 发送每日健康报?

            self._send_daily_report(report)



            time.sleep(interval_minutes * 60)



    def _send_daily_report(self, report: HealthReport):

        """发送每日健康报告（22:00?""

        current_time = datetime.now().strftime('%H:%M')

        if current_time == '22:00':

            summary = f"""

每日健康报告 - {datetime.now().date()}

========================

状? {report.status}

检查项: {len(report.checks)}

正常? {sum(1 for r in report.checks if r.ok)}

异常? {sum(1 for r in report.checks if not r.ok)}

"""

            self.alert_manager.send_alert('INFO', summary)

```



```
```---
```



## 6. 自动恢复



```python

class AutoRecovery:

    """自动恢复机制"""



    def recover_process(self, process_name: str) -> bool:

        """尝试自动恢复进程"""

        recovery_actions = {

            'data_pipeline': lambda: self._restart_pipeline(),

            'strategy_engine': lambda: self._restart_engine(),

            'execution_agent': lambda: self._restart_agent()

        }



        if process_name in recovery_actions:

            try:

                recovery_actions[process_name]()

                return True

            except Exception as e:

                return False

        return False



    def _restart_pipeline(self):

        """重启数据流水?""

        # 实现重启逻辑

        pass

```



```
```---
```



## 7. 监控配置



```yaml

# config/monitoring.yaml

monitoring:

  enabled: true

  check_interval_minutes: 30



  alerts:

    wechat_webhook: "${WECHAT_WEBHOOK}"

    email: "${ALERT_EMAIL}"



  thresholds:

    disk_space_gb: 10

    max_errors_per_hour: 10

    pipeline_delay_minutes: 60



  auto_recovery:

    enabled: true

    max_retries: 3

```



```
```---
```



## 8. 与其他模块的关系



```

04_EXECUTION/03_MONITORING/

├── README.md              # 本文?

├── REAL_TIME_MONITORING.md  # 实时监控（策略PnL等）

├── PERFORMANCE_ATTRIBUTION.md # 业绩归因

└── HEALTH_MONITOR.py       # 健康监控脚本 ⭐新?

```



```
```---
```



## 索引



- 父目? 04_EXECUTION/03_MONITORING/README.md

- 相关: REAL_TIME_MONITORING.md
