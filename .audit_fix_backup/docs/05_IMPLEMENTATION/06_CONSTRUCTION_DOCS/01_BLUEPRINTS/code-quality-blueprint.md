---

module_id: CODE_QUALITY_001

version: 1.0.0

status: Active

created_date: 2026-04-07

last_updated: 2026-04-07

owner: 首席文档架构师

responsibility:

  - 代码质量检查

  - 代码规范验证

  - 代码复杂度分析

  - 代码重复检测

standard_type: 专业量化机构蓝图

compliance_level: 专业标准

layer: layer_05

---



# 代码质量检查蓝图



> **核心职责**: 提供自动化的代码质量检查，确保代码符合规范、可维护、可读

> **职责边界**: 

> - ✅ 本文档负责：代码质量检查、规范验证、复杂度分析

> - ❌ 本文档不负责：代码测试（由测试框架负责）、代码安全（由安全扫描负责）



## 接口与契约（蓝图终稿）



- 全库 API 与事件约定真源：`API_Contract.md`。代码质量检查结果若作为“质量门禁事件/报告接口”对外消费（CI/CD、发布审批、审计查询），其对外口径以该真源为准。



## 验收标准（可检查）



- 能对目标代码库输出结构化检查结果（问题数量、严重等级、文件分布），且可被流水线消费（例如 JSON/报告文件）。

- 质量阈值可配置且可验证：例如复杂度阈值、重复率阈值、规范违规阈值，未达标时能阻断合并/发布。

- 误报/漏报处理策略明确（例如白名单、基线、抑制规则），并能在报告中体现被抑制项。

- 对外结果上报/审计查询若存在，应能在 `API_Contract.md` 中定位契约入口（或在“已知限制”列出未闭合项）。



## 已知限制



- SaaS（如 SonarCloud）在私有仓库/离线环境下的可用性与成本存在不确定性；必要时需准备自托管替代（SonarQube 等）。



## 核心定位



负责代码质量检查模块的设计与构建，实现自动化代码质量检查、代码规范验证、代码复杂度分析，确保代码质量和可维护性。



## 设计目标



### 主要目标



1. **代码规范检查**: 确保代码符合PEP8等规范

2. **代码复杂度分析**: 识别过于复杂的代码

3. **代码重复检测**: 发现重复代码片段

4. **代码质量评分**: 提供代码质量评分和改进建议



### 质量目标



- 代码规范合规率: 95%

- 代码复杂度阈值: <10

- 代码重复率: <5%

- 质量门禁通过率: 90%



## 开源方案选型



### 推荐方案: SonarCloud



| 属性 | 详情 |

|------|------|

| **平台** | SonarCloud (SaaS) |

| **免费额度** | 公开仓库免费 |

| **特点** | 云端代码质量平台 |



**选择理由**:

1. **免费使用**: 公开仓库完全免费

2. **云端托管**: 无需部署和维护

3. **功能完整**: 支持多种语言

4. **GitHub集成**: 与GitHub无缝集成

5. **个人友好**: 适合个人开发者使用



### 备选方案



| 项目 | Stars | 特点 | 推荐度 |

|------|-------|------|--------|

| **SonarQube** | 8k+ | 自托管代码质量平台 | ⭐⭐⭐⭐⭐ |

| **Pylint** | 5k+ | Python代码检查工具 | ⭐⭐⭐⭐⭐ |

| **flake8** | 3k+ | Python代码规范检查 | ⭐⭐⭐⭐⭐ |



## 核心功能设计



### 1. 代码规范检查模块



```python

import subprocess

from typing import Dict, List, Any

import json



class CodeQualityChecker:

    """代码质量检查器"""

    

    def __init__(self, project_path: str):

        self.project_path = project_path

    

    def run_flake8(self) -> Dict[str, Any]:

        """运行flake8检查"""

        result = subprocess.run(

            ["flake8", self.project_path, "--format=json"],

            capture_output=True,

            text=True

        )

        

        violations = json.loads(result.stdout) if result.stdout else []

        

        return {

            "total_violations": len(violations),

            "violations_by_type": self._group_by(violations, "code"),

            "violations_by_file": self._group_by(violations, "filename"),

            "details": violations

        }

    

    def run_pylint(self) -> Dict[str, Any]:

        """运行pylint检查"""

        result = subprocess.run(

            ["pylint", self.project_path, "--output-format=json"],

            capture_output=True,

            text=True

        )

        

        issues = json.loads(result.stdout) if result.stdout else []

        

        return {

            "score": self._extract_score(result.stderr),

            "total_issues": len(issues),

            "issues_by_type": self._group_by(issues, "type"),

            "issues_by_severity": self._group_by(issues, "severity"),

            "details": issues

        }

    

    def run_black_check(self) -> Dict[str, Any]:

        """运行black格式检查"""

        result = subprocess.run(

            ["black", "--check", self.project_path],

            capture_output=True,

            text=True

        )

        

        return {

            "would_reformat": result.returncode != 0,

            "files_to_reformat": self._extract_files(result.stdout),

            "passed": result.returncode == 0

        }

    

    def run_mypy(self) -> Dict[str, Any]:

        """运行mypy类型检查"""

        result = subprocess.run(

            ["mypy", self.project_path, "--json-report", "-"],

            capture_output=True,

            text=True

        )

        

        errors = self._parse_mypy_output(result.stdout)

        

        return {

            "total_errors": len(errors),

            "errors_by_file": self._group_by(errors, "file"),

            "passed": result.returncode == 0,

            "details": errors

        }

    

    def calculate_complexity(self) -> Dict[str, Any]:

        """计算代码复杂度"""

        result = subprocess.run(

            ["radon", "cc", self.project_path, "-j"],

            capture_output=True,

            text=True

        )

        

        complexity_data = json.loads(result.stdout) if result.stdout else {}

        

        return {

            "average_complexity": self._calculate_avg_complexity(complexity_data),

            "high_complexity_files": self._find_high_complexity(complexity_data, threshold=10),

            "details": complexity_data

        }

    

    def detect_duplicates(self) -> Dict[str, Any]:

        """检测代码重复"""

        result = subprocess.run(

            ["jscpd", self.project_path, "--reporters", "json"],

            capture_output=True,

            text=True

        )

        

        duplicates = json.loads(result.stdout) if result.stdout else {}

        

        return {

            "duplicate_percentage": duplicates.get("statistics", {}).get("total", 0),

            "duplicate_blocks": len(duplicates.get("duplicates", [])),

            "details": duplicates

        }

    

    def generate_quality_report(self) -> Dict[str, Any]:

        """生成质量报告"""

        flake8_results = self.run_flake8()

        pylint_results = self.run_pylint()

        black_results = self.run_black_check()

        mypy_results = self.run_mypy()

        complexity_results = self.calculate_complexity()

        duplicate_results = self.detect_duplicates()

        

        overall_score = self._calculate_overall_score(

            flake8_results,

            pylint_results,

            black_results,

            mypy_results,

            complexity_results,

            duplicate_results

        )

        

        return {

            "overall_score": overall_score,

            "flake8": flake8_results,

            "pylint": pylint_results,

            "black": black_results,

            "mypy": mypy_results,

            "complexity": complexity_results,

            "duplicates": duplicate_results,

            "recommendations": self._generate_recommendations(

                flake8_results,

                pylint_results,

                complexity_results

            )

        }

    

    def _group_by(self, items: List[Dict], key: str) -> Dict[str, int]:

        """按字段分组"""

        from collections import Counter

        return dict(Counter(item.get(key, "unknown") for item in items))

    

    def _extract_score(self, output: str) -> float:

        """提取pylint评分"""

        import re

        match = re.search(r"rated at ([\d.]+)/10", output)

        return float(match.group(1)) if match else 0.0

    

    def _extract_files(self, output: str) -> List[str]:

        """提取文件列表"""

        import re

        return re.findall(r"would reformat (.+)", output)

    

    def _parse_mypy_output(self, output: str) -> List[Dict]:

        """解析mypy输出"""

        errors = []

        for line in output.split("\n"):

            if line.strip():

                errors.append({"message": line})

        return errors

    

    def _calculate_avg_complexity(self, data: Dict) -> float:

        """计算平均复杂度"""

        if not data:

            return 0.0

        

        total = 0

        count = 0

        for file_data in data.values():

            for item in file_data:

                total += item.get("complexity", 0)

                count += 1

        

        return total / count if count > 0 else 0.0

    

    def _find_high_complexity(self, data: Dict, threshold: int) -> List[Dict]:

        """查找高复杂度文件"""

        high_complexity = []

        for file_path, items in data.items():

            for item in items:

                if item.get("complexity", 0) >= threshold:

                    high_complexity.append({

                        "file": file_path,

                        "name": item.get("name"),

                        "complexity": item.get("complexity")

                    })

        return high_complexity

    

    def _calculate_overall_score(self, *results) -> float:

        """计算总体评分"""

        score = 100.0

        

        flake8 = results[0]

        score -= min(flake8["total_violations"] * 0.5, 20)

        

        pylint = results[1]

        score = (score + pylint["score"] * 10) / 2

        

        black = results[2]

        if not black["passed"]:

            score -= 5

        

        mypy = results[3]

        score -= min(mypy["total_errors"] * 0.3, 15)

        

        complexity = results[4]

        if complexity["average_complexity"] > 10:

            score -= (complexity["average_complexity"] - 10) * 2

        

        duplicates = results[5]

        score -= duplicates["duplicate_percentage"] * 0.5

        

        return max(0, min(100, score))

    

    def _generate_recommendations(self, *results) -> List[str]:

        """生成改进建议"""

        recommendations = []

        

        flake8 = results[0]

        if flake8["total_violations"] > 10:

            recommendations.append("修复flake8代码规范违规")

        

        pylint = results[1]

        if pylint["score"] < 8.0:

            recommendations.append("改进代码质量，提升pylint评分")

        

        complexity = results[2]

        if complexity["average_complexity"] > 10:

            recommendations.append("重构高复杂度代码，降低圈复杂度")

        

        return recommendations

```



### 2. GitHub Actions集成



```yaml

# .github/workflows/code-quality.yml

name: Code Quality Check



on:

  push:

    branches: [ main, develop ]

  pull_request:

    branches: [ main ]



jobs:

  code-quality:

    runs-on: ubuntu-latest

    

    steps:

    - uses: actions/checkout@v4

    

    - name: Set up Python

      uses: actions/setup-python@v4

      with:

        python-version: '3.10'

    

    - name: Install dependencies

      run: |

        python -m pip install --upgrade pip

        pip install flake8 pylint black mypy radon jscpd

    

    - name: Run flake8

      run: flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics

    

    - name: Run black check

      run: black --check src/

    

    - name: Run mypy

      run: mypy src/ --ignore-missing-imports

    

    - name: Run pylint

      run: pylint src/ --fail-under=8.0

    

    - name: SonarCloud Scan

      uses: SonarSource/sonarcloud-github-action@master

      env:

        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

        SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}

```



### 3. SonarCloud配置



```xml

<!-- sonar-project.properties -->

sonar.projectKey=zephyr-alpha

sonar.organization=your-org

sonar.sources=src

sonar.tests=tests

sonar.python.coverage.reportPaths=coverage.xml

sonar.python.xunit.reportPath=test-results.xml

sonar.python.pylint.reportPath=pylint-report.txt

```



## 部署架构



### 本地开发环境



```bash

# 安装依赖

pip install flake8 pylint black mypy radon jscpd



# 运行检查

flake8 src/

pylint src/

black --check src/

mypy src/

radon cc src/ -a

jscpd src/

```



### CI/CD集成



```yaml

# GitHub Actions自动检查

# 每次提交自动运行代码质量检查

# PR必须通过质量门禁才能合并

```



## 实施计划



### 阶段1: 基础配置 (Week 1)



| 任务 | 工时 | 负责人 | 交付物 |

|------|------|--------|--------|

| 安装工具 | 1h | 开发者 | 工具安装 |

| 配置文件 | 2h | 开发者 | 配置文件 |

| 本地测试 | 2h | 开发者 | 测试报告 |



### 阶段2: CI/CD集成 (Week 1)



| 任务 | 工时 | 负责人 | 交付物 |

|------|------|--------|--------|

| GitHub Actions配置 | 2h | 开发者 | 工作流文件 |

| SonarCloud配置 | 2h | 开发者 | SonarCloud项目 |

| 质量门禁配置 | 2h | 开发者 | 质量规则 |



### 阶段3: 持续改进 (Week 2)



| 任务 | 工时 | 负责人 | 交付物 |

|------|------|--------|--------|

| 修复现有问题 | 8h | 开发者 | 修复代码 |

| 优化配置 | 2h | 开发者 | 优化配置 |

| 文档编写 | 2h | 开发者 | 使用文档 |



## 性能指标



| 指标 | 目标值 | 测量方法 |

|------|--------|---------|

| **代码规范合规率** | 95% | flake8违规数量 |

| **代码质量评分** | >8.0 | pylint评分 |

| **代码复杂度** | <10 | 平均圈复杂度 |

| **代码重复率** | <5% | 重复代码比例 |



## 成本估算



| 项目 | 开源方案成本 | 商业方案成本 |

|------|-------------|-------------|

| **软件许可** | $0 | $0 (公开仓库) |

| **SonarCloud** | 免费 | $150/月 (私有仓库) |

| **总成本** | **$0** | **$0-$150/月** |



```---



**文档版本**: v1.0.0

**创建日期**: 2026-04-07

**最后更新**: 2026-04-07

**状态**: Active



## 接口与契约（蓝图终稿）



- 全库 API 与事件约定真源：`API_Contract.md`。代码质量扫描的规则集、报告输出、阻断策略与告警事件等对外约定需以该真源或其子契约为准。

- 邻层协同边界：与 **CI/CD（发布流水线）**、**Layer 10（治理与合规）** 的交互以契约为准（避免门禁口径冲突）。



## 验收标准（可检查）



- 能对目标代码库产出可复核报告（lint/复杂度/重复率任一），并能说明规则版本与范围。

- 能配置并验证“阻断阈值”（如重复率/复杂度/严重问题数），触发时有事件留痕。

- 能对误报/漏报给出最小闭环处理流程（登记→修复/豁免→复验），并可追溯。

- 能在 CI 中稳定运行且性能可接受（给出时间预算与测量方式）。



## 已知限制



- 规则集字段字典、报告 schema 与事件载荷细化将在施工阶段固化到 `API_Contract.md` 子契约；本蓝图先确保边界、接口闭合点与验收闭环清晰。

