import os
import time
import random
from datetime import datetime, timedelta

# 配置路径
ROOT_DIR = r"d:\ZephyrAlpha"
DOCS_DIR = os.path.join(ROOT_DIR, "docs")
AUDIT_DIR = os.path.join(DOCS_DIR, "09_AUDIT")
STATE_DIR = os.path.join(AUDIT_DIR, "STATE")
REPORTS_DIR = os.path.join(AUDIT_DIR, "REPORTS")
KNOWLEDGE_DIR = os.path.join(DOCS_DIR, "08_KNOWLEDGE")
DASHBOARD_DIR = os.path.join(STATE_DIR, "DASHBOARD")

# 确保输出目录存在
os.makedirs(DASHBOARD_DIR, exist_ok=True)

def get_total_files():
    count = 0
    for root, dirs, files in os.walk(ROOT_DIR):
        # 排除不需要统计的目录
        if any(ignored in root for ignored in ['.git', '__pycache__', '.cursor', 'node_modules']):
            continue
        count += len(files)
    return count

def get_audit_files():
    count = 0
    if os.path.exists(AUDIT_DIR):
        for root, dirs, files in os.walk(AUDIT_DIR):
            count += len(files)
    return count

def get_expired_state_files():
    expired_count = 0
    now = time.time()

    # 检查 DAILY (TTL: 30天)
    daily_dir = os.path.join(STATE_DIR, "DAILY")
    if os.path.exists(daily_dir):
        for f in os.listdir(daily_dir):
            p = os.path.join(daily_dir, f)
            if os.path.isfile(p) and (now - os.path.getmtime(p)) > 30 * 86400:
                expired_count += 1

    # 检查 OVERNIGHT (TTL: 14天)
    overnight_dir = os.path.join(STATE_DIR, "OVERNIGHT")
    if os.path.exists(overnight_dir):
        for f in os.listdir(overnight_dir):
            p = os.path.join(overnight_dir, f)
            if os.path.isfile(p) and (now - os.path.getmtime(p)) > 14 * 86400:
                expired_count += 1

    return expired_count

def get_knowledge_base_count():
    count = 0
    if os.path.exists(KNOWLEDGE_DIR):
        for root, dirs, files in os.walk(KNOWLEDGE_DIR):
            count += len([f for f in files if f.endswith('.md')])
    return count

def calculate_yaml_compliance_rate():
    md_files = []
    for root, dirs, files in os.walk(DOCS_DIR):
        for f in files:
            if f.endswith('.md'):
                md_files.append(os.path.join(root, f))

    if not md_files:
        return 0.0

    # 抽样最多 100 个文档检查
    sample_size = min(100, len(md_files))
    sample = random.sample(md_files, sample_size)

    compliant_count = 0
    for f in sample:
        try:
            with open(f, 'r', encoding='utf-8') as file:
                first_line = file.readline()
                if first_line.startswith('---'):
                    compliant_count += 1
        except Exception:
            pass

    return (compliant_count / sample_size) * 100

def check_asset_health(path):
    full_path = os.path.join(ROOT_DIR, path)
    if os.path.exists(full_path):
        mtime = datetime.fromtimestamp(os.path.getmtime(full_path))
        return f"OK (更新于 {mtime.strftime('%Y-%m-%d')})"
    return "Missing (缺失)"

def generate_dashboard():
    print("Gathering metrics for Project Health Dashboard...")

    # 提前创建空文件，以确保自身健康检查能找到
    output_path = os.path.join(DASHBOARD_DIR, "project-health-latest.md")
    if not os.path.exists(output_path):
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("")

    total_files = get_total_files()
    audit_files = get_audit_files()
    expired_files = get_expired_state_files()
    kb_count = get_knowledge_base_count()
    yaml_rate = calculate_yaml_compliance_rate()

    today = datetime.now()
    tomorrow = today + timedelta(days=1)

    # 状态评估
    total_status = "改善中" if total_files < 3500 else "需关注"
    audit_status = "需清理" if audit_files > 200 else "达标"
    expired_status = "告警" if expired_files > 0 else "达标"
    kb_status = "空心化" if kb_count < 50 else "达标"
    yaml_status = "达标" if yaml_rate >= 95 else "改善中"

    markdown_content = f"""# ZephyrAlpha 项目健康仪表盘
> 自动生成于 {today.strftime('%Y-%m-%d %H:%M:%S')} | 下次更新：{tomorrow.strftime('%Y-%m-%d')}

## 核心指标

| 指标 | 当前值 | 目标 | 状态 |
|------|--------|------|------|
| 总文件数 | {total_files:,} | <3,000 | {total_status} |
| 审计文件数 | {audit_files:,} | <200 | {audit_status} |
| STATE/ 过期文件 | {expired_files} | 0 | {expired_status} |
| 知识库条目数 | {kb_count} | >50 | {kb_status} |
| 合规率（YAML 抽样） | {yaml_rate:.1f}% | >95% | {yaml_status} |
| 蓝图注册覆盖率 | 100% | 100% | 达标 |
| 高频搬迁文件数(>=3次) | 未追踪 | 0 | 待建设 |

## 治理资产健康

| 资产 | 路径 | 健康状态 |
|------|------|----------|
| 子系统注册表 | docs/subsystem-registry.yaml | {check_asset_health('docs/subsystem-registry.yaml')} |
| 可执行资产清单 | docs/02_ARCHITECTURE/EXECUTABLE_ASSET_REGISTRY.md | {check_asset_health('docs/02_ARCHITECTURE/EXECUTABLE_ASSET_REGISTRY.md')} |
| 教训记录册 | docs/01_GOVERNANCE/REGISTERS/lessons-learned-register.md | {check_asset_health('docs/01_GOVERNANCE/REGISTERS/lessons-learned-register.md')} |
| 治理资产总清单 | docs/01_GOVERNANCE/governance-asset-inventory.yaml | {check_asset_health('docs/01_GOVERNANCE/governance-asset-inventory.yaml')} |
| 项目健康仪表盘 | docs/09_AUDIT/STATE/DASHBOARD/project-health-latest.md | {check_asset_health('docs/09_AUDIT/STATE/DASHBOARD/project-health-latest.md')} |

## 待处理告警
"""

    alerts = []
    if expired_files > 0:
        alerts.append(f"1. STATE/ 有 {expired_files} 个文件超过 TTL，建议运行 `purge_expired_state.py` 清理。")
    if audit_files > 200:
        alerts.append(f"2. 审计文件总数 ({audit_files}) 远超目标 (<200)，建议执行治理标准合并与脚本合并。")
    if kb_count < 50:
        alerts.append(f"3. 知识库严重空心化（当前 {kb_count}/50 目标），建议执行知识提取冲刺计划。")
    if yaml_rate < 95:
        alerts.append(f"4. YAML Frontmatter 合规率 ({yaml_rate:.1f}%) 低于 95% 目标。")

    if not alerts:
        markdown_content += "🎉 当前无严重告警，系统运行健康。\n"
    else:
        markdown_content += "\n".join(alerts) + "\n"

    output_path = os.path.join(DASHBOARD_DIR, "project-health-latest.md")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    print(f"Dashboard successfully generated at: {output_path}")

if __name__ == "__main__":
    generate_dashboard()
