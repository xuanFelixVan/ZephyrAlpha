#!/usr/bin/env python3
"""
QMT接口连接测试脚本
用于检测国金证券QMT实盘和模拟交易接口的可用性

使用前提:
1. 已安装xtquant库: pip install xtquant
2. QMT客户端已启动并登录
3. 确保Python版本为3.6-3.12（64位）
"""

import sys
import os
from pathlib import Path
from datetime import datetime

class QMTConnectionTester:
    """QMT连接测试器"""
    
    def __init__(self):
        self.results = {
            'xtquant_import': False,
            'xtdata_import': False,
            'xttrader_import': False,
            'data_connection': False,
            'trading_connection': False,
            'account_query': False,
            'position_query': False
        }
        self.errors = []
        
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
            self.print_result("xtquant库导入", True, f"版本: {xtquant.__version__ if hasattr(xtquant, '__version__') else '未知'}")
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
            
            # 尝试获取一个简单的行情数据
            test_symbol = "000001.SZ"  # 平安银行
            
            # 尝试获取最新行情
            data = xtdata.get_full_tick([test_symbol])
            
            if data and test_symbol in data:
                self.results['data_connection'] = True
                tick_data = data[test_symbol]
                self.print_result(
                    "数据连接测试", 
                    True, 
                    f"成功获取{test_symbol}行情: 最新价 {tick_data.get('lastPrice', 'N/A')}"
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
    
    def test_trading_connection(self, account_id: str = None, password: str = None) -> bool:
        """测试交易连接
        
        参数:
            account_id: 交易账号（可选，如不提供则跳过实盘测试）
            password: 交易密码（可选）
        """
        if not account_id:
            self.print_result("交易连接测试", False, "未提供账号信息，跳过实盘连接测试")
            print("     提示: 如需测试实盘连接，请提供账号参数")
            return False
            
        try:
            from xtquant.xttrader import XtQuantTrader
            
            # 创建交易会话
            session_id = 123456  # 自定义会话ID
            trader = XtQuantTrader(account_id, session_id)
            
            # 启动交易线程
            trader.start()
            
            # 连接交易账户
            connect_result = trader.connect()
            
            if connect_result == 0:
                self.results['trading_connection'] = True
                self.print_result("交易连接测试", True, f"账号 {account_id} 连接成功")
                
                # 测试账户查询
                try:
                    asset = trader.query_stock_asset(account_id)
                    if asset:
                        self.results['account_query'] = True
                        self.print_result(
                            "账户资产查询", 
                            True, 
                            f"总资产: {asset.total_asset:.2f}, 可用资金: {asset.cash:.2f}"
                        )
                except Exception as e:
                    self.errors.append(f"账户查询失败: {e}")
                    self.print_result("账户资产查询", False, str(e))
                
                # 测试持仓查询
                try:
                    positions = trader.query_stock_positions(account_id)
                    self.results['position_query'] = True
                    self.print_result(
                        "持仓查询", 
                        True, 
                        f"当前持仓: {len(positions)}只股票"
                    )
                except Exception as e:
                    self.errors.append(f"持仓查询失败: {e}")
                    self.print_result("持仓查询", False, str(e))
                
                # 断开连接
                trader.disconnect()
                return True
            else:
                self.errors.append(f"交易连接失败: 返回码 {connect_result}")
                self.print_result("交易连接测试", False, f"连接失败，返回码: {connect_result}")
                return False
                
        except Exception as e:
            self.errors.append(f"交易连接异常: {e}")
            self.print_result("交易连接测试", False, str(e))
            return False
    
    def run_all_tests(self, account_id: str = None, password: str = None):
        """运行所有测试"""
        self.print_header("QMT接口连接测试")
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
            self.print_header("3. 交易接口测试")
            self.test_trading_connection(account_id, password)
        
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
        elif not self.results['trading_connection']:
            print("⚠️  交易连接未测试")
            print("   如需测试实盘交易，请提供账号信息:")
            print("   python test_qmt_connection.py --account 您的账号 --password 您的密码")
        else:
            print("✅ 所有测试通过！QMT接口工作正常")
        
        print("=" * 70)
        
        return self.results


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='QMT接口连接测试工具')
    parser.add_argument('--account', type=str, help='交易账号（可选）')
    parser.add_argument('--password', type=str, help='交易密码（可选）')
    
    args = parser.parse_args()
    
    tester = QMTConnectionTester()
    results = tester.run_all_tests(args.account, args.password)
    
    # 返回退出码
    sys.exit(0 if all(results.values()) else 1)


if __name__ == "__main__":
    main()
