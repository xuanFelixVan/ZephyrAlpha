"""
经济范式判断引擎 - 数据采集模块

负责从各种数据源采集宏观经济数据。

模块ID: ECONOMIC_REGIME_ENGINE_002
版本: v2.0.0
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import pandas as pd
import numpy as np
import logging
from pathlib import Path
import json
import sqlite3
from abc import ABC, abstractmethod


@dataclass
class MacroIndicatorConfig:
    """宏观经济指标配置"""
    name: str
    code: str
    source: str
    frequency: str
    unit: str
    description: str


class MacroDataCollector(ABC):
    """宏观经济数据采集器基类"""
    
    @abstractmethod
    def fetch_data(self, indicator: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        采集宏观经济数据
        
        Args:
            indicator: 指标代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            DataFrame: 宏观经济数据
        """
        pass


class MockMacroDataCollector(MacroDataCollector):
    """模拟宏观经济数据采集器（用于测试和开发）"""
    
    def __init__(self):
        """初始化模拟数据采集器"""
        self.logger = logging.getLogger(__name__)
        
    def fetch_data(self, indicator: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        生成模拟宏观经济数据
        
        Args:
            indicator: 指标代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            DataFrame: 模拟宏观经济数据
        """
        self.logger.info(f"生成模拟数据: {indicator}, {start_date} 至 {end_date}")
        
        date_range = pd.date_range(start=start_date, end=end_date, freq='M')
        
        np.random.seed(hash(indicator) % 2**32)
        
        if indicator == 'gdp_growth':
            values = np.random.normal(6.5, 1.5, len(date_range))
        elif indicator == 'cpi':
            values = np.random.normal(2.5, 1.0, len(date_range))
        elif indicator == 'ppi':
            values = np.random.normal(1.5, 2.0, len(date_range))
        elif indicator == 'pmi':
            values = np.random.normal(51.0, 3.0, len(date_range))
        elif indicator == 'interest_rate':
            values = np.random.normal(3.5, 0.5, len(date_range))
        elif indicator == 'm2_growth':
            values = np.random.normal(10.0, 2.0, len(date_range))
        elif indicator == 'credit_growth':
            values = np.random.normal(12.0, 3.0, len(date_range))
        elif indicator == 'industrial_output':
            values = np.random.normal(6.5, 2.0, len(date_range))
        else:
            values = np.random.normal(0, 1, len(date_range))
        
        df = pd.DataFrame({
            'date': date_range,
            'value': values
        })
        
        df.set_index('date', inplace=True)
        
        return df


class WindMacroDataCollector(MacroDataCollector):
    """Wind宏观经济数据采集器"""
    
    def __init__(self, api_client=None):
        """
        初始化Wind数据采集器
        
        Args:
            api_client: Wind API客户端
        """
        self.logger = logging.getLogger(__name__)
        self.api_client = api_client
        
    def fetch_data(self, indicator: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        从Wind采集宏观经济数据
        
        Args:
            indicator: 指标代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            DataFrame: 宏观经济数据
        """
        if self.api_client is None:
            self.logger.warning("Wind API客户端未配置，使用模拟数据")
            return MockMacroDataCollector().fetch_data(indicator, start_date, end_date)
        
        try:
            self.logger.info(f"从Wind采集数据: {indicator}")
            
            wind_code_map = {
                'gdp_growth': 'M0000272',
                'cpi': 'M0000612',
                'ppi': 'M0001229',
                'pmi': 'M0017126',
                'interest_rate': 'M0000612',
                'm2_growth': 'M0001382',
                'credit_growth': 'M0001383',
                'industrial_output': 'M0000272'
            }
            
            wind_code = wind_code_map.get(indicator, indicator)
            
            data = self.api_client.edb(
                wind_code, 
                start_date.strftime('%Y-%m-%d'), 
                end_date.strftime('%Y-%m-%d')
            )
            
            df = pd.DataFrame(data.Data, index=data.Times).T
            df.columns = ['value']
            df.index.name = 'date'
            
            return df
            
        except Exception as e:
            self.logger.error(f"Wind数据采集失败: {e}")
            raise


class IFindMacroDataCollector(MacroDataCollector):
    """iFind宏观经济数据采集器"""
    
    def __init__(self, api_client=None):
        """
        初始化iFind数据采集器
        
        Args:
            api_client: iFind API客户端
        """
        self.logger = logging.getLogger(__name__)
        self.api_client = api_client
        
    def fetch_data(self, indicator: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        从iFind采集宏观经济数据
        
        Args:
            indicator: 指标代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            DataFrame: 宏观经济数据
        """
        if self.api_client is None:
            self.logger.warning("iFind API客户端未配置，使用模拟数据")
            return MockMacroDataCollector().fetch_data(indicator, start_date, end_date)
        
        try:
            self.logger.info(f"从iFind采集数据: {indicator}")
            
            ifind_code_map = {
                'gdp_growth': 'EDB_GDP_YOY',
                'cpi': 'EDB_CPI_YOY',
                'ppi': 'EDB_PPI_YOY',
                'pmi': 'EDB_PMI',
                'interest_rate': 'EDB_INTEREST_RATE',
                'm2_growth': 'EDB_M2_YOY',
                'credit_growth': 'EDB_CREDIT_YOY',
                'industrial_output': 'EDB_INDUSTRIAL_YOY'
            }
            
            ifind_code = ifind_code_map.get(indicator, indicator)
            
            data = self.api_client.macro(
                ifind_code, 
                start_date.strftime('%Y-%m-%d'), 
                end_date.strftime('%Y-%m-%d')
            )
            
            df = pd.DataFrame(data)
            df.columns = ['date', 'value']
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            return df
            
        except Exception as e:
            self.logger.error(f"iFind数据采集失败: {e}")
            raise


class MacroDataManager:
    """宏观经济数据管理器"""
    
    INDICATORS = {
        'gdp_growth': MacroIndicatorConfig(
            name='GDP增长率',
            code='gdp_growth',
            source='wind',
            frequency='quarterly',
            unit='%',
            description='国内生产总值同比增长率'
        ),
        'cpi': MacroIndicatorConfig(
            name='CPI',
            code='cpi',
            source='wind',
            frequency='monthly',
            unit='%',
            description='消费者物价指数同比增长率'
        ),
        'ppi': MacroIndicatorConfig(
            name='PPI',
            code='ppi',
            source='wind',
            frequency='monthly',
            unit='%',
            description='生产者物价指数同比增长率'
        ),
        'pmi': MacroIndicatorConfig(
            name='PMI',
            code='pmi',
            source='wind',
            frequency='monthly',
            unit='',
            description='制造业采购经理指数'
        ),
        'interest_rate': MacroIndicatorConfig(
            name='利率',
            code='interest_rate',
            source='wind',
            frequency='monthly',
            unit='%',
            description='基准利率'
        ),
        'm2_growth': MacroIndicatorConfig(
            name='M2增速',
            code='m2_growth',
            source='wind',
            frequency='monthly',
            unit='%',
            description='广义货币供应量同比增长率'
        ),
        'credit_growth': MacroIndicatorConfig(
            name='信贷增速',
            code='credit_growth',
            source='wind',
            frequency='monthly',
            unit='%',
            description='金融机构贷款余额同比增长率'
        ),
        'industrial_output': MacroIndicatorConfig(
            name='工业增加值',
            code='industrial_output',
            source='wind',
            frequency='monthly',
            unit='%',
            description='工业增加值同比增长率'
        )
    }
    
    def __init__(self, 
                 db_path: str = 'data/economic_regime.db',
                 use_mock_data: bool = True,
                 wind_client=None,
                 ifind_client=None):
        """
        初始化宏观经济数据管理器
        
        Args:
            db_path: 数据库路径
            use_mock_data: 是否使用模拟数据
            wind_client: Wind API客户端
            ifind_client: iFind API客户端
        """
        self.logger = logging.getLogger(__name__)
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.use_mock_data = use_mock_data
        
        if use_mock_data:
            self.collector = MockMacroDataCollector()
        else:
            self.collector = WindMacroDataCollector(wind_client)
        
        self._init_database()
        
    def _init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS macro_indicators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                indicator_date DATE NOT NULL,
                indicator_code VARCHAR(50) NOT NULL,
                indicator_value DECIMAL(10, 4),
                source VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(indicator_date, indicator_code),
                INDEX idx_indicator_date (indicator_date),
                INDEX idx_indicator_code (indicator_code)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"数据库初始化完成: {self.db_path}")
        
    def collect_all_indicators(self, 
                               start_date: datetime,
                               end_date: datetime,
                               save_to_db: bool = True) -> pd.DataFrame:
        """
        采集所有宏观经济指标
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            save_to_db: 是否保存到数据库
            
        Returns:
            DataFrame: 所有宏观经济指标数据
        """
        self.logger.info(f"开始采集宏观经济数据: {start_date} 至 {end_date}")
        
        all_data = {}
        
        for indicator_code in self.INDICATORS.keys():
            try:
                df = self.collector.fetch_data(indicator_code, start_date, end_date)
                all_data[indicator_code] = df['value']
                
                if save_to_db:
                    self._save_to_db(indicator_code, df)
                    
            except Exception as e:
                self.logger.error(f"采集指标 {indicator_code} 失败: {e}")
                continue
        
        combined_df = pd.DataFrame(all_data)
        
        self.logger.info(f"宏观经济数据采集完成: {len(combined_df)} 条记录")
        
        return combined_df
    
    def _save_to_db(self, indicator_code: str, df: pd.DataFrame):
        """
        保存数据到数据库
        
        Args:
            indicator_code: 指标代码
            df: 数据DataFrame
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for date, row in df.iterrows():
            cursor.execute('''
                INSERT OR REPLACE INTO macro_indicators 
                (indicator_date, indicator_code, indicator_value, source, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (date.strftime('%Y-%m-%d'), indicator_code, float(row['value']), 
                  'mock' if self.use_mock_data else 'wind'))
        
        conn.commit()
        conn.close()
        
    def load_from_db(self, 
                     start_date: datetime,
                     end_date: datetime,
                     indicators: Optional[List[str]] = None) -> pd.DataFrame:
        """
        从数据库加载宏观经济数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            indicators: 指标列表（可选）
            
        Returns:
            DataFrame: 宏观经济数据
        """
        conn = sqlite3.connect(self.db_path)
        
        if indicators is None:
            indicators = list(self.INDICATORS.keys())
        
        all_data = {}
        
        for indicator_code in indicators:
            query = '''
                SELECT indicator_date, indicator_value
                FROM macro_indicators
                WHERE indicator_code = ?
                AND indicator_date BETWEEN ? AND ?
                ORDER BY indicator_date
            '''
            
            df = pd.read_sql_query(
                query, 
                conn, 
                params=(indicator_code, 
                       start_date.strftime('%Y-%m-%d'), 
                       end_date.strftime('%Y-%m-%d'))
            )
            
            if not df.empty:
                df['indicator_date'] = pd.to_datetime(df['indicator_date'])
                df.set_index('indicator_date', inplace=True)
                all_data[indicator_code] = df['indicator_value']
        
        conn.close()
        
        combined_df = pd.DataFrame(all_data)
        
        return combined_df
    
    def update_data(self, days: int = 30):
        """
        更新宏观经济数据（增量更新）
        
        Args:
            days: 更新最近N天的数据
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        self.logger.info(f"增量更新宏观经济数据: {start_date} 至 {end_date}")
        
        self.collect_all_indicators(start_date, end_date, save_to_db=True)


def main():
    """主函数 - 数据采集示例"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    manager = MacroDataManager(use_mock_data=True)
    
    start_date = datetime(2010, 1, 1)
    end_date = datetime(2025, 12, 31)
    
    df = manager.collect_all_indicators(start_date, end_date, save_to_db=True)
    
    print("\n宏观经济数据采集结果:")
    print(df.head())
    print(f"\n数据形状: {df.shape}")
    print(f"\n数据统计:")
    print(df.describe())
    
    df.to_csv('data/macro_indicators.csv')
    print("\n数据已保存到: data/macro_indicators.csv")


if __name__ == '__main__':
    main()
