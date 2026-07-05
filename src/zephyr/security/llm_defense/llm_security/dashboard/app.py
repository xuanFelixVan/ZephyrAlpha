# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md | §
# [MODULE] zephyr.security.llm_defense.llm_security.dashboard.app
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.llm_defense.llm_security.layers.__init__; zephyr.security.llm_defense.llm_security.self_protection.__init__; zephyr.security.llm_defense.llm_security.payloads.__init__; zephyr.security.llm_defense.llm_security.patterns.__init__; zephyr.security.llm_defense.llm_security.behavior_audit_logger; zephyr.security.llm_defense.llm_security.input_sanitizer; zephyr.security.llm_defense.llm_security.protocol
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SEC_app | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""LLM Security Gateway - Streamlit Dashboard.

提供实时安全监控、攻击检测统计、载荷分析、系统健康状态的可视化界面。
"""

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
import yaml
from zephyr.shared.io.paths import REPO_ROOT

# 5.129.4 修复: 移除冗余 sys.path.insert — line 30 已 from zephyr.shared.io.paths import REPO_ROOT,
# 说明 zephyr 包已在 sys.path 上, 此处重复插入无意义且污染全局 sys.path
project_root = REPO_ROOT

try:
    from zephyr.security.llm_defense.llm_security.behavior_audit_logger import AuditLogger
    from zephyr.security.llm_defense.llm_security.input_sanitizer import InputSanitizer
    from zephyr.security.llm_defense.llm_security.layers import (
        l0_supply_chain,
        l1_input,
        l2_prompt_protection,
        l3_output,
        l4_agent,
        l5_resource_protection,
        l6_observability,
        l8_multi_agent,
    )
    from zephyr.security.llm_defense.llm_security.patterns import injection_patterns, secrets
    from zephyr.security.llm_defense.llm_security.payloads import (
        injection_payloads,
        leak_probe_phrases,
        red_team_payloads,
        tool_call_payloads,
    )
    from zephyr.security.llm_defense.llm_security.protocol import LLMSecurityProtocol
    from zephyr.security.llm_defense.llm_security.self_protection import code_integrity, isolation, l7_validation

    IMPORT_SUCCESS = True
except ImportError as e:
    IMPORT_SUCCESS = False
    st.warning(f"部分导入失败: {e}")


class SecurityDashboard:
    """安全仪表板主类"""

    def __init__(self):
        self.setup_page_config()
        self.load_payloads()
        self.setup_sidebar()

    def setup_page_config(self):
        """设置页面配置"""
        st.set_page_config(
            page_title="LLM Security Gateway Dashboard", page_icon="🛡️", layout="wide", initial_sidebar_state="expanded"
        )

    def load_payloads(self):
        """加载载荷数据"""
        payloads_dir = project_root / "src" / "zephyr" / "llm-security" / "payloads"

        self.payloads_data = {}
        for yaml_file in payloads_dir.glob("*.yaml"):
            try:
                with open(yaml_file, encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    self.payloads_data[yaml_file.stem] = data
            except Exception as e:
                st.error(f"加载 {yaml_file} 失败: {e}")

    def setup_sidebar(self):
        """设置侧边栏"""
        st.sidebar.title("🛡️ LSG Dashboard")
        st.sidebar.markdown("---")

        # 导航菜单
        self.selected_page = st.sidebar.selectbox("导航", ["安全概览", "攻击检测", "载荷分析", "系统健康", "实时监控"])

        # 时间范围选择
        st.sidebar.markdown("### 时间范围")
        time_range = st.sidebar.selectbox("选择时间范围", ["最近1小时", "最近24小时", "最近7天", "自定义"])

        if time_range == "自定义":
            col1, col2 = st.sidebar.columns(2)
            with col1:
                start_date = st.date_input("开始日期")
            with col2:
                end_date = st.date_input("结束日期")

        # 严重性过滤器
        st.sidebar.markdown("### 严重性过滤器")
        severities = st.sidebar.multiselect(
            "选择严重性级别", ["critical", "high", "medium", "low"], default=["critical", "high"]
        )

        st.sidebar.markdown("---")
        st.sidebar.info("LLM Security Gateway v0.10.0")

    def render_security_overview(self):
        """渲染安全概览页面"""
        st.title("🔒 安全概览")

        # 关键指标卡片
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(label="检测到的攻击", value="1,247", delta="+12%")

        with col2:
            st.metric(label="阻止的注入", value="892", delta="-5%")

        with col3:
            st.metric(label="平均响应时间", value="47ms", delta="-8%")

        with col4:
            st.metric(label="系统可用性", value="99.8%", delta="+0.2%")

        # 攻击趋势图
        st.subheader("📈 攻击趋势")

        # 模拟数据
        dates = pd.date_range(start="2024-01-01", periods=30, freq="D")
        attack_data = pd.DataFrame(
            {
                "date": dates,
                "injections": [
                    12,
                    15,
                    8,
                    20,
                    18,
                    22,
                    25,
                    30,
                    28,
                    25,
                    20,
                    18,
                    15,
                    12,
                    10,
                    8,
                    6,
                    5,
                    4,
                    3,
                    2,
                    1,
                    2,
                    3,
                    4,
                    5,
                    6,
                    7,
                    8,
                    9,
                ],
                "tool_abuse": [
                    5,
                    7,
                    6,
                    8,
                    10,
                    12,
                    15,
                    18,
                    16,
                    14,
                    12,
                    10,
                    8,
                    6,
                    5,
                    4,
                    3,
                    2,
                    1,
                    2,
                    3,
                    4,
                    5,
                    6,
                    7,
                    8,
                    9,
                    10,
                    11,
                    12,
                ],
                "data_leak": [
                    3,
                    4,
                    2,
                    5,
                    6,
                    8,
                    10,
                    12,
                    11,
                    9,
                    7,
                    6,
                    5,
                    4,
                    3,
                    2,
                    1,
                    2,
                    3,
                    4,
                    5,
                    6,
                    7,
                    8,
                    9,
                    10,
                    11,
                    12,
                    13,
                    14,
                ],
            }
        )

        fig = px.line(
            attack_data,
            x="date",
            y=["injections", "tool_abuse", "data_leak"],
            title="攻击类型趋势",
            labels={"value": "攻击次数", "variable": "攻击类型"},
        )
        st.plotly_chart(fig, use_container_width=True)

        # 严重性分布
        st.subheader("⚠️ 严重性分布")

        severity_data = pd.DataFrame({"severity": ["critical", "high", "medium", "low"], "count": [245, 478, 324, 200]})

        fig = px.pie(severity_data, values="count", names="severity", title="攻击严重性分布", hole=0.3)
        st.plotly_chart(fig, use_container_width=True)

    def render_attack_detection(self):
        """渲染攻击检测页面"""
        st.title("🔍 攻击检测")

        # 实时检测日志
        st.subheader("🕵️ 实时检测日志")

        # 模拟检测日志
        detection_logs = [
            {
                "timestamp": "2024-01-15 10:23:45",
                "type": "Prompt Injection",
                "severity": "critical",
                "status": "阻止",
                "source": "API Gateway",
            },
            {
                "timestamp": "2024-01-15 10:22:30",
                "type": "Tool Abuse",
                "severity": "high",
                "status": "阻止",
                "source": "MCP Server",
            },
            {
                "timestamp": "2024-01-15 10:21:15",
                "type": "Data Leak",
                "severity": "medium",
                "status": "警告",
                "source": "Output Filter",
            },
            {
                "timestamp": "2024-01-15 10:20:00",
                "type": "Encoding Bypass",
                "severity": "high",
                "status": "阻止",
                "source": "Input Sanitizer",
            },
            {
                "timestamp": "2024-01-15 10:19:45",
                "type": "Role Play",
                "severity": "critical",
                "status": "阻止",
                "source": "Prompt Protection",
            },
        ]

        df_logs = pd.DataFrame(detection_logs)
        st.dataframe(df_logs, use_container_width=True)

        # 检测模式分析
        st.subheader("📊 检测模式分析")

        col1, col2 = st.columns(2)

        with col1:
            # 检测成功率
            detection_stats = pd.DataFrame(
                {
                    "layer": ["L1 Input", "L2 Prompt", "L3 Output", "L4 Agent", "L5 Resource"],
                    "success_rate": [98.5, 96.2, 97.8, 95.4, 99.1],
                    "false_positive": [1.2, 2.1, 1.5, 3.2, 0.8],
                }
            )

            fig = px.bar(
                detection_stats, x="layer", y=["success_rate", "false_positive"], barmode="group", title="各层检测性能"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # 响应时间分布
            response_times = pd.DataFrame(
                {
                    "time_range": ["<10ms", "10-50ms", "50-100ms", "100-500ms", ">500ms"],
                    "count": [1200, 850, 320, 150, 45],
                }
            )

            fig = px.pie(response_times, values="count", names="time_range", title="检测响应时间分布")
            st.plotly_chart(fig, use_container_width=True)

    def render_payload_analysis(self):
        """渲染载荷分析页面"""
        st.title("📋 载荷分析")

        # 载荷统计概览
        st.subheader("📈 载荷统计概览")

        if self.payloads_data:
            # 计算各类载荷数量
            payload_counts = {}
            for payload_name, payload_data in self.payloads_data.items():
                if "payloads" in payload_data:
                    payload_counts[payload_name] = len(payload_data["payloads"])

            df_counts = pd.DataFrame(list(payload_counts.items()), columns=["Payload Type", "Count"])

            col1, col2 = st.columns(2)

            with col1:
                fig = px.bar(df_counts, x="Payload Type", y="Count", title="载荷类型分布", color="Payload Type")
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                fig = px.pie(df_counts, values="Count", names="Payload Type", title="载荷类型占比")
                st.plotly_chart(fig, use_container_width=True)

            # 载荷详情展示
            st.subheader("🔬 载荷详情")

            selected_payload_type = st.selectbox("选择载荷类型", list(self.payloads_data.keys()))

            if selected_payload_type in self.payloads_data:
                payloads = self.payloads_data[selected_payload_type].get("payloads", [])

                # 创建可展开的载荷详情
                for i, payload in enumerate(payloads[:10]):  # 限制显示数量
                    with st.expander(f"{payload.get('id', f'Payload-{i}')}: {payload.get('name', 'Unnamed')}"):
                        col1, col2 = st.columns(2)

                        with col1:
                            st.write(f"**类别**: {payload.get('category', 'N/A')}")
                            st.write(f"**严重性**: {payload.get('severity', 'N/A')}")

                        with col2:
                            st.write(f"**变体数量**: {len(payload.get('variants', []))}")

                        # 显示变体示例
                        variants = payload.get("variants", [])
                        if variants:
                            st.write("**变体示例**:")
                            for j, variant in enumerate(variants[:3]):  # 显示前3个变体
                                st.code(variant, language="text")
        else:
            st.warning("未能加载载荷数据")

    def render_system_health(self):
        """渲染系统健康页面"""
        st.title("💚 系统健康")

        # 系统状态概览
        st.subheader("📊 系统状态概览")

        col1, col2, col3 = st.columns(3)

        with col1:
            # CPU/内存使用率
            st.metric("CPU 使用率", "23%", "-2%")
            st.progress(0.23)

        with col2:
            st.metric("内存使用率", "67%", "+5%")
            st.progress(0.67)

        with col3:
            st.metric("磁盘使用率", "42%", "+1%")
            st.progress(0.42)

        # 安全层健康状态
        st.subheader("🛡️ 安全层健康状态")

        layer_health = pd.DataFrame(
            {
                "Layer": [
                    "L0 Supply Chain",
                    "L1 Input",
                    "L2 Prompt",
                    "L3 Output",
                    "L4 Agent",
                    "L5 Resource",
                    "L6 Observability",
                    "L7 Validation",
                    "L8 Multi-Agent",
                ],
                "Status": [
                    "Healthy",
                    "Healthy",
                    "Degraded",
                    "Healthy",
                    "Healthy",
                    "Healthy",
                    "Healthy",
                    "Healthy",
                    "Healthy",
                ],
                "Uptime": ["99.9%", "99.8%", "95.2%", "99.7%", "99.9%", "99.8%", "99.6%", "99.9%", "99.7%"],
                "Last Check": [
                    "2 min ago",
                    "1 min ago",
                    "5 min ago",
                    "3 min ago",
                    "1 min ago",
                    "2 min ago",
                    "4 min ago",
                    "1 min ago",
                    "2 min ago",
                ],
            }
        )

        # 添加状态颜色
        def status_color(status):
            if status == "Healthy":
                return "background-color: #90EE90"
            elif status == "Degraded":
                return "background-color: #FFD580"
            else:
                return "background-color: #FFB6C1"

        styled_df = layer_health.style.applymap(
            lambda x: status_color(x) if x in ["Healthy", "Degraded", "Unhealthy"] else "", subset=["Status"]
        )

        st.dataframe(styled_df, use_container_width=True)

        # 性能指标
        st.subheader("⚡ 性能指标")

        performance_data = pd.DataFrame(
            {
                "Metric": ["平均响应时间", "P95 响应时间", "吞吐量", "错误率", "并发连接数"],
                "Value": ["47ms", "128ms", "1,250 req/s", "0.12%", "850"],
                "Target": ["<100ms", "<200ms", ">1000 req/s", "<0.5%", "<1000"],
                "Status": ["✅", "✅", "✅", "✅", "✅"],
            }
        )

        st.dataframe(performance_data, use_container_width=True)

    def render_realtime_monitoring(self):
        """渲染实时监控页面"""
        st.title("📡 实时监控")

        # 实时流量监控
        st.subheader("🌊 实时流量监控")

        # 模拟实时数据
        time_points = pd.date_range(start="2024-01-15 10:00:00", periods=60, freq="min")
        traffic_data = pd.DataFrame(
            {
                "timestamp": time_points,
                "requests": [
                    120,
                    135,
                    110,
                    125,
                    140,
                    130,
                    145,
                    150,
                    135,
                    125,
                    120,
                    130,
                    140,
                    150,
                    160,
                    155,
                    145,
                    135,
                    125,
                    115,
                    120,
                    130,
                    140,
                    150,
                    160,
                    170,
                    165,
                    155,
                    145,
                    135,
                    125,
                    115,
                    120,
                    130,
                    140,
                    150,
                    160,
                    170,
                    180,
                    175,
                    165,
                    155,
                    145,
                    135,
                    125,
                    115,
                    120,
                    130,
                    140,
                    150,
                    160,
                    170,
                    180,
                    190,
                    185,
                    175,
                    165,
                    155,
                    145,
                    135,
                ],
                "attacks": [
                    12,
                    15,
                    8,
                    10,
                    14,
                    12,
                    16,
                    18,
                    15,
                    12,
                    10,
                    11,
                    13,
                    15,
                    17,
                    16,
                    14,
                    12,
                    10,
                    9,
                    8,
                    9,
                    11,
                    13,
                    15,
                    17,
                    16,
                    14,
                    12,
                    10,
                    9,
                    8,
                    9,
                    10,
                    12,
                    14,
                    16,
                    18,
                    20,
                    19,
                    17,
                    15,
                    13,
                    11,
                    9,
                    8,
                    9,
                    10,
                    12,
                    14,
                    16,
                    18,
                    20,
                    22,
                    21,
                    19,
                    17,
                    15,
                    13,
                    11,
                ],
            }
        )

        fig = px.line(
            traffic_data,
            x="timestamp",
            y=["requests", "attacks"],
            title="实时请求与攻击流量",
            labels={"value": "数量", "variable": "类型"},
        )
        st.plotly_chart(fig, use_container_width=True)

        # 实时警报
        st.subheader("🚨 实时警报")

        alerts = [
            {
                "timestamp": "10:29:30",
                "level": "HIGH",
                "message": "检测到大规模 Prompt Injection 攻击",
                "source": "L2 Prompt Protection",
            },
            {
                "timestamp": "10:28:45",
                "level": "MEDIUM",
                "message": "资源使用率异常升高",
                "source": "L5 Resource Protection",
            },
            {
                "timestamp": "10:27:15",
                "level": "LOW",
                "message": "检测到可疑工具调用模式",
                "source": "L4 Agent Security",
            },
            {
                "timestamp": "10:26:30",
                "level": "HIGH",
                "message": "输出过滤器检测到敏感信息泄露尝试",
                "source": "L3 Output Security",
            },
        ]

        for alert in alerts:
            if alert["level"] == "HIGH":
                st.error(f"**{alert['timestamp']}** - {alert['message']} ({alert['source']})")
            elif alert["level"] == "MEDIUM":
                st.warning(f"**{alert['timestamp']}** - {alert['message']} ({alert['source']})")
            else:
                st.info(f"**{alert['timestamp']}** - {alert['message']} ({alert['source']})")

        # 地理分布
        st.subheader("🌍 攻击来源地理分布")

        geo_data = pd.DataFrame(
            {
                "country": ["美国", "中国", "俄罗斯", "德国", "英国", "日本", "巴西", "印度"],
                "attacks": [245, 189, 156, 98, 87, 76, 65, 54],
                "lat": [37.0902, 35.8617, 61.5240, 51.1657, 55.3781, 36.2048, -14.2350, 20.5937],
                "lon": [-95.7129, 104.1954, 105.3188, 10.4515, -3.4360, 138.2529, -51.9253, 78.9629],
            }
        )

        fig = px.scatter_geo(
            geo_data,
            lat="lat",
            lon="lon",
            size="attacks",
            hover_name="country",
            title="攻击来源地理分布",
            projection="natural earth",
        )
        st.plotly_chart(fig, use_container_width=True)

    def render(self):
        """渲染主页面"""
        # 页面标题
        st.markdown("""
        # 🛡️ LLM Security Gateway Dashboard
        *实时安全监控与攻击检测分析平台*
        """)

        # 根据选择的页面渲染内容
        if self.selected_page == "安全概览":
            self.render_security_overview()
        elif self.selected_page == "攻击检测":
            self.render_attack_detection()
        elif self.selected_page == "载荷分析":
            self.render_payload_analysis()
        elif self.selected_page == "系统健康":
            self.render_system_health()
        elif self.selected_page == "实时监控":
            self.render_realtime_monitoring()

        # 页脚
        st.markdown("---")
        st.markdown(
            """
        <div style='text-align: center; color: gray;'>
        LLM Security Gateway v0.10.0 | 最后更新: 2024-01-15
        </div>
        """,
            unsafe_allow_html=True,
        )


def main():
    """主函数"""
    # 检查导入状态
    if not IMPORT_SUCCESS:
        st.warning("⚠️ 部分模块导入失败，仪表板功能可能受限")

    # 创建并渲染仪表板
    dashboard = SecurityDashboard()
    dashboard.render()


if __name__ == "__main__":
    main()
