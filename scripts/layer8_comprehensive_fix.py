"""
Layer 8 人机交互层综合修复脚本
修复：双YAML头部、Layer定位、职责描述
"""

import re
from pathlib import Path
from datetime import datetime

LAYER8_DIR = Path("docs/08_human_ai_interface")


class Layer8ComprehensiveFixer:
    """Layer 8 综合修复器"""
    
    def __init__(self):
        self.stats = {
            "double_yaml_fixed": 0,
            "layer_fixed": 0,
            "responsibility_fixed": 0,
            "errors": []
        }
        
        self.responsibility_map = {
            "MONITORING_DASHBOARD_BLUEPRINT.md": "系统监控仪表板，负责实时监控系统运行状态、关键指标展示和性能监控，不负责告警推送和日志记录",
            "ALERTING_SYSTEM_BLUEPRINT.md": "告警通知系统，负责异常检测、告警规则配置和告警推送，不负责系统监控和日志记录",
            "AUTH_SYSTEM_BLUEPRINT.md": "认证授权系统，负责用户身份认证、登录管理和基础权限验证，不负责细粒度权限控制",
            "API_DOCS_BLUEPRINT.md": "API文档系统，负责API接口文档的自动生成、展示和维护，不负责API限流和权限管理",
            "BACKTEST_UI_BLUEPRINT.md": "交互式回测界面，负责策略回测的可视化展示、结果分析和报告生成，不负责实盘交易和参数优化",
            "REPORTING_BLUEPRINT.md": "报告生成系统，负责投资报告、风险报告和绩效报告的自动生成，不负责实时监控和告警",
            "AUDIT_LOG_BLUEPRINT.md": "审计日志系统，负责操作审计、日志记录和审计追踪，不负责系统监控和告警",
            "MOBILE_PUSH_BLUEPRINT.md": "移动推送通知，负责移动端消息推送、通知管理和推送策略，不负责告警规则配置",
            "TRADING_JOURNAL_BLUEPRINT.md": "交易日志系统，负责交易记录的展示、分析和归档，不负责实盘交易操作和策略管理",
            "CONFIG_MANAGEMENT_BLUEPRINT.md": "配置管理系统，负责系统配置的集中管理、版本控制和配置同步，不负责用户偏好设置",
            "USER_PREFERENCES_BLUEPRINT.md": "用户偏好设置，负责用户个性化配置、界面定制和偏好管理，不负责系统配置管理",
            "SYSTEM_STATUS_BLUEPRINT.md": "系统状态监控，负责系统健康状态检查、服务可用性监控和状态展示，不负责性能监控和告警",
            "DATA_MANAGEMENT_BLUEPRINT.md": "数据管理界面，负责数据的导入导出、数据质量管理和数据生命周期管理，不负责数据备份",
            "STRATEGY_MANAGEMENT_BLUEPRINT.md": "策略管理界面，负责策略的配置、部署和生命周期管理，不负责策略回测和参数优化",
            "PERMISSION_MANAGEMENT_BLUEPRINT.md": "权限管理系统，负责细粒度权限控制、角色管理和权限审计，不负责基础认证授权",
            "API_RATE_LIMITING_BLUEPRINT.md": "API限流系统，负责API访问频率控制、流量管理和限流策略，不负责API文档和权限管理",
            "DOCUMENTATION_CENTER_BLUEPRINT.md": "文档中心，负责系统文档的集中展示、检索和维护，不负责知识库管理",
            "KNOWLEDGE_BASE_BLUEPRINT.md": "知识库系统，负责知识管理、知识检索和知识共享，不负责文档中心管理",
            "CI_CD_INTEGRATION_BLUEPRINT.md": "CI/CD集成，负责持续集成、持续部署和自动化流水线，不负责系统监控和告警",
            "DATA_BACKUP_BLUEPRINT.md": "数据备份系统，负责数据备份、恢复和备份策略管理，不负责数据导入导出",
            "ONLINE_RESEARCH_ENVIRONMENT_BLUEPRINT.md": "在线研究环境，负责交互式研究、数据分析和实验管理，不负责策略回测和参数优化",
            "PARAMETER_OPTIMIZATION_BLUEPRINT.md": "参数优化界面，负责策略参数优化、参数搜索和优化结果展示，不负责策略回测和实盘交易",
            "LIVE_TRADING_INTERFACE_BLUEPRINT.md": "实盘交易界面，负责实盘交易操作、订单管理和交易监控，不负责策略回测和参数优化"
        }
    
    def read_document(self, filepath: Path) -> str:
        """读取文档内容"""
        encodings = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312', 'latin-1']
        for encoding in encodings:
            try:
                with open(filepath, 'r', encoding=encoding) as f:
                    return f.read()
            except:
                continue
        return ""
    
    def fix_double_yaml(self, filepath: Path) -> tuple:
        """修复双YAML头部"""
        content = self.read_document(filepath)
        if not content:
            return False, content
        
        # 检测双YAML头部模式
        # 模式1: ---\n...\n---\n\n---\n...\n---\n
        pattern1 = r'^---\s*\n(.*?)\n---\s*\n\s*\ufeff?---\s*\n(.*?)\n---\s*\n'
        match1 = re.match(pattern1, content, re.DOTALL)
        
        if match1:
            first_yaml = match1.group(1).strip()
            second_yaml = match1.group(2).strip()
            rest_content = content[match1.end():]
            
            # 合并YAML，优先使用第二个（更完整的）
            merged = self.merge_yaml_headers(first_yaml, second_yaml)
            
            new_content = f"---\n{merged}\n---\n" + rest_content
            return True, new_content
        
        # 模式2: 检查是否有两个独立的YAML块
        yaml_blocks = list(re.finditer(r'^---\s*\n(.*?)\n---\s*\n', content[:2000], re.DOTALL | re.MULTILINE))
        
        if len(yaml_blocks) >= 2:
            first_yaml = yaml_blocks[0].group(1).strip()
            second_yaml = yaml_blocks[1].group(1).strip()
            rest_content = content[yaml_blocks[1].end():]
            
            merged = self.merge_yaml_headers(first_yaml, second_yaml)
            
            new_content = f"---\n{merged}\n---\n" + rest_content
            return True, new_content
        
        return False, content
    
    def merge_yaml_headers(self, first: str, second: str) -> str:
        """合并两个YAML头部"""
        # 解析第二个YAML（通常更完整）
        yaml_dict = {}
        for line in second.split('\n'):
            if ':' in line and not line.startswith(' '):
                key, value = line.split(':', 1)
                yaml_dict[key.strip()] = value.strip()
            elif line.startswith(' ') and yaml_dict:
                # 处理多行值
                last_key = list(yaml_dict.keys())[-1]
                yaml_dict[last_key] += '\n' + line
        
        # 从第一个YAML补充缺失的字段
        for line in first.split('\n'):
            if ':' in line and not line.startswith(' '):
                key, value = line.split(':', 1)
                key = key.strip()
                if key not in yaml_dict:
                    yaml_dict[key] = value.strip()
        
        # 确保layer字段正确
        if 'layer' not in yaml_dict or 'Layer 8' not in yaml_dict.get('layer', ''):
            yaml_dict['layer'] = 'Layer 8 (人机交互层)'
        
        # 确保responsibility字段正确
        if 'responsibility' not in yaml_dict:
            yaml_dict['responsibility'] = '\n  - 待定义'
        
        # 重建YAML
        lines = []
        for key, value in yaml_dict.items():
            if '\n' in str(value):
                lines.append(f"{key}:{value}")
            else:
                lines.append(f"{key}: {value}")
        
        return '\n'.join(lines)
    
    def fix_document(self, filepath: Path):
        """修复单个文档"""
        print(f"  处理: {filepath.name}")
        
        # 1. 修复双YAML头部
        fixed, content = self.fix_double_yaml(filepath)
        if fixed:
            self.stats['double_yaml_fixed'] += 1
            print(f"    ✅ 双YAML已修复")
        
        # 2. 确保layer正确
        if 'layer: Layer 8 (人机交互层)' not in content:
            content = re.sub(
                r'layer:\s*Layer\s*\d+\s*\([^)]+\)',
                'layer: Layer 8 (人机交互层)',
                content
            )
            if 'layer:' not in content.split('---\n')[1] if '---\n' in content else True:
                # 在YAML头部添加layer
                content = re.sub(
                    r'(---\n.*?)(---\n)',
                    r'\1layer: Layer 8 (人机交互层)\n\2',
                    content,
                    count=1,
                    flags=re.DOTALL
                )
            self.stats['layer_fixed'] += 1
            print(f"    ✅ Layer已修复")
        
        # 3. 确保responsibility正确
        responsibility = self.responsibility_map.get(filepath.name)
        if responsibility:
            if responsibility not in content:
                # 更新responsibility字段
                content = re.sub(
                    r'responsibility:\s*\n\s*-\s*[^\n]+',
                    f'responsibility:\n  - {responsibility}',
                    content
                )
                self.stats['responsibility_fixed'] += 1
                print(f"    ✅ 职责已修复")
        
        # 保存文件
        try:
            with open(filepath, 'w', encoding='utf-8-sig') as f:
                f.write(content)
        except Exception as e:
            print(f"    ❌ 保存失败: {e}")
            self.stats['errors'].append(f"{filepath.name}: {e}")
    
    def run_fix(self):
        """执行修复"""
        print("="*60)
        print("Layer 8 人机交互层综合修复")
        print("="*60)
        print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        md_files = list(LAYER8_DIR.glob("**/*_BLUEPRINT.md"))
        
        print(f"\n发现 {len(md_files)} 个蓝图文件")
        print("\n开始修复...")
        
        for filepath in md_files:
            self.fix_document(filepath)
        
        print("\n" + "="*60)
        print("修复完成")
        print("="*60)
        print(f"双YAML修复: {self.stats['double_yaml_fixed']}")
        print(f"Layer修复: {self.stats['layer_fixed']}")
        print(f"职责修复: {self.stats['responsibility_fixed']}")
        
        if self.stats['errors']:
            print(f"\n错误: {len(self.stats['errors'])}")
            for err in self.stats['errors']:
                print(f"  - {err}")
        
        return self.stats


def main():
    fixer = Layer8ComprehensiveFixer()
    fixer.run_fix()


if __name__ == "__main__":
    main()
