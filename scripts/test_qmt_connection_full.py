#!/usr/bin/env python3
"""
QMT接口完整连接测试脚本
支持从环境变量读取账号信息，测试模拟和实盘账户连接

使用前提:
1. 已安装xtquant库: pip install xtquant
2. QMT客户端已启动并登录
3. 配置.env.qmt文件存储账号信息
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
import yaml

class QMTConnectionTester:
    """QMT连接测试器"""
    
    def __init__(self):
        self.results = {
            'xtquant_import': False,
            'xtdata_import': False,
            'xttrader_import': False,
            'data_connection': False,
            'simulation_connection': False,
            'simulation_account_query': False,
            'simulation_position_query': False,
            'live_connection': False,
            'live_account_query': False,
            'live_position_query': False
        }
        self.errors = []
        self.config = self._load_config()
        self._load_env()
        
    def _load_config(self) -> Dict:
        """加载配置文件"""
        config_path = Path("config/qmt_config.yaml")
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}
    
    def _load_env(self):
        """加载环境变量"""
        env_path = Path(".env.qmt")
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
    
    def print_header(self, title: str):
        """打印标题"""
        print("\n" + "=" * 70)
        print(f"  {title}")
        print("=" * 70)
    
    def print_result(self, test_name: str, success: bool, message: str = ""):
        """打印测试结果"""
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{status} - {test_name}")
        if message:
            print(f"     {message}")
    
    def test_xtquant_import(self) -> bool:
        """测试xtquant库导入"""
        try:
            import xtquant
            self.results['xtquant_import'] = True
            version = xtquant.__version__ if hasattr(xtquant, '__version__') else '未知'
            self.print_result("xtquant库导入", True, f"版本: {version}")
            return True
        except ImportError as e:
            self.errors.append(f"xtquant导入失败: {e}")
            self.print_result("xtquant库导入", False, "请执行: pip install xtquant")
            return False
    
    def test_xtdata_import(self) -> bool:
        """测试xtdata模块导入"""
        try:
            from xtquant import xtdata
            self.results['xtdata_import'] = True
            self.print_result("xtdata模块导入", True, "数据API可用")
            return True
        except ImportError as e:
            self.errors.append(f"xtdata导入失败: {e}")
            self.print_result("xtdata模块导入", False, str(e))
            return False
    
    def test_xttrader_import(self) -> bool:
        """测试xttrader模块导入"""
        try:
            from xtquant import xttrader
            self.results['xttrader_import'] = True
            self.print_result("xttrader模块导入", True, "交易API可用")
            return True
        except ImportError as e:
            self.errors.append(f"xttrader导入失败: {e}")
            self.print_result("xttrader模块导入", False, str(e))
            return False
    
    def test_data_connection(self) -> bool:
        """测试数据连接"""
        try:
            from xtquant import xtdata
            
            test_symbol = "000001.SZ"
            data = xtdata.get_full_tick([test_symbol])
            
            if data and test_symbol in data:
                self.results['data_connection'] = True
                tick_data = data[test_symbol]
                last_price = tick_data.get('lastPrice', 'N/A')
                self.print_result(
                    "数据连接测试", 
                    True, 
                    f"成功获取{test_symbol}行情: 最新价 {last_price}"
                )
                return True
            else:
                self.errors.append("数据连接失败: 无法获取行情数据")
                self.print_result("数据连接测试", False, "无法获取行情数据，请确认QMT客户端已启动")
                return False
                
        except Exception as e:
            self.errors.append(f"数据连接异常: {e}")
            self.print_result("数据连接测试", False, str(e))
            return False
    
    def test_trading_connection(
        self, 
        account_id: str, 
        password: str, 
        account_type: str = "simulation"
    ) -> bool:
        """测试交易连接
        
        参数:
            account_id: 交易账号
            password: 交易密码
            account_type: 账户类型 (simulation/live)
        """
        try:
            from xtquant.xttrader import XtQuantTrader
            
            session_id = int(datetime.now().timestamp())
            trader = XtQuantTrader(account_id, session_id)
            
            trader.start()
            
            connect_result = trader.connect()
            
            if connect_result == 0:
                result_key = f"{account_type}_connection"
                self.results[result_key] = True
                
                account_label = "模拟账户" if account_type == "simulation" else "实盘账户"
                self.print_result(
                    f"{account_label}连接测试", 
                    True, 
                    f"账号 {account_id} 连接成功"
                )
                
                try:
                    asset = trader.query_stock_asset(account_id)
                    if asset:
                        self.results[f"{account_type}_account_query"] = True
                        self.print_result(
                            f"{account_label}资产查询", 
                            True, 
                            f"总资产: {asset.total_asset:.2f}, 可用资金: {asset.cash:.2f}, 市值: {asset.market_value:.2f}"
                        )
                except Exception as e:
                    self.errors.append(f"{account_label}资产查询失败: {e}")
                    self.print_result(f"{account_label}资产查询", False, str(e))
                
                try:
                    positions = trader.query_stock_positions(account_id)
                    self.results[f"{account_type}_position_query"] = True
                    position_count = len(positions) if positions else 0
                    self.print_result(
                        f"{account_label}持仓查询", 
                        True, 
                        f"当前持仓: {position_count}只股票"
                    )
                    
                    if positions and len(positions) > 0:
                        print(f"\n     持仓明细:")
                        for pos in positions[:5]:
                            print(f"       - {pos.stock_code}: {pos.volume}股, 市值{pos.market_value:.2f}元")
                        if len(positions) > 5:
                            print(f"       ... 还有{len(positions)-5}只股票")
                            
                except Exception as e:
                    self.errors.append(f"{account_label}持仓查询失败: {e}")
                    self.print_result(f"{account_label}持仓查询", False, str(e))
                
                trader.disconnect()
                return True
            else:
                self.errors.append(f"{account_type}交易连接失败: 返回码 {connect_result}")
                account_label = "模拟账户" if account_type == "simulation" else "实盘账户"
                self.print_result(
                    f"{account_label}连接测试", 
                    False, 
                    f"连接失败，返回码: {connect_result}"
                )
                return False
                
        except Exception as e:
            self.errors.append(f"{account_type}交易连接异常: {e}")
            account_label = "模拟账户" if account_type == "simulation" else "实盘账户"
            self.print_result(f"{account_label}连接测试", False, str(e))
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        self.print_header("QMT接口完整连接测试")
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 基础库导入测试
        self.print_header("1. 基础库导入测试")
        self.test_xtquant_import()
        if self.results['xtquant_import']:
            self.test_xtdata_import()
            self.test_xttrader_import()
        
        # 数据连接测试
        if self.results['xtdata_import']:
            self.print_header("2. 数据接口测试")
            self.test_data_connection()
        
        # 交易连接测试
        if self.results['xttrader_import']:
            self.print_header("3. 模拟账户测试")
            
            sim_account = os.getenv('QMT_SIMULATION_ACCOUNT')
            sim_password = os.getenv('QMT_SIMULATION_PASSWORD')
            
            if sim_account and sim_password:
                self.test_trading_connection(sim_account, sim_password, "simulation")
            else:
                self.print_result("模拟账户测试", False, "未配置模拟账户信息，请检查.env.qmt文件")
            
            self.print_header("4. 实盘账户测试")
            
            live_account = os.getenv('QMT_LIVE_ACCOUNT')
            live_password = os.getenv('QMT_LIVE_PASSWORD')
            
            if live_account and live_password:
                print("⚠️  警告: 即将测试实盘账户，涉及真实资金！")
                self.test_trading_connection(live_account, live_password, "live")
            else:
                self.print_result("实盘账户测试", False, "未配置实盘账户信息，请检查.env.qmt文件")
        
        # 测试总结
        self.print_header("测试总结")
        total_tests = len(self.results)
        passed_tests = sum(self.results.values())
        
        print(f"\n总测试项: {total_tests}")
        print(f"通过项: {passed_tests}")
        print(f"失败项: {total_tests - passed_tests}")
        print(f"通过率: {passed_tests/total_tests*100:.1f}%")
        
        if self.errors:
            print("\n错误详情:")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
        
        # 给出建议
        print("\n" + "=" * 70)
        print("诊断建议:")
        print("=" * 70)
        
        if not self.results['xtquant_import']:
            print("❌ xtquant库未安装")
            print("   解决方案: pip install xtquant")
        elif not self.results['data_connection']:
            print("❌ 数据连接失败")
            print("   可能原因:")
            print("   1. QMT客户端未启动")
            print("   2. QMT客户端未登录")
            print("   3. 网络连接问题")
            print("   解决方案:")
            print("   1. 启动QMT客户端并登录")
            print("   2. 检查网络连接")
            print("   3. 确认已下载必要的历史数据")
        elif not self.results['simulation_connection']:
            print("⚠️  模拟账户连接失败")
            print("   请检查.env.qmt文件中的账号密码是否正确")
        elif not self.results['live_connection']:
            print("⚠️  实盘账户连接失败")
            print("   请检查.env.qmt文件中的账号密码是否正确")
        else:
            print("✅ 所有测试通过！QMT接口工作正常")
            print("\n📊 账户状态:")
            print("   - 模拟账户: ✅ 已连接")
            print("   - 实盘账户: ✅ 已连接")
            print("\n💡 下一步操作:")
            print("   - 可以开始使用QMT接口进行交易")
            print("   - 建议先在模拟账户测试策略")
            print("   - 实盘交易请谨慎操作")
        
        print("=" * 70)
        
        return self.results


def main():
    """主函数"""
    tester = QMTConnectionTester()
    results = tester.run_all_tests()
    
    sys.exit(0 if all(results.values()) else 1)


if __name__ == "__main__":
    main()
