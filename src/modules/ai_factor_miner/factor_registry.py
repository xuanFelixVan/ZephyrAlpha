"""
因子注册器

管理因子注册、存储、版本控制
"""

from typing import Dict, Optional
import sqlite3
import json
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)


class FactorRegistry:
    """因子注册器
    
    管理因子注册、存储、版本控制
    """
    
    def __init__(self, config: Dict):
        """
        初始化因子注册器
        
        Args:
            config: 配置字典
                - db_path: 数据库路径
        """
        self.config = config
        self.db_path = config.get('db_path', 'data/factors/factor_registry.db')
        
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        self._init_database()
        
        logger.info(f"因子注册器初始化完成,数据库: {self.db_path}")
        
    def _init_database(self):
        """
        初始化数据库
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS factor_registry (
                factor_id TEXT PRIMARY KEY,
                factor_name TEXT NOT NULL,
                method TEXT NOT NULL,
                expression TEXT,
                ic_mean REAL,
                ic_ir REAL,
                ic_std REAL,
                complexity INTEGER,
                status TEXT DEFAULT 'experimental',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT,
                metadata TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mining_tasks (
                task_id TEXT PRIMARY KEY,
                task_name TEXT,
                methods TEXT,
                config TEXT,
                status TEXT,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                duration_seconds INTEGER,
                total_mined INTEGER,
                passed_filter INTEGER,
                registered INTEGER,
                error_message TEXT,
                created_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info("数据库初始化完成")
        
    def register(self, factor: Dict) -> str:
        """
        注册因子
        
        Args:
            factor: 因子字典
            
        Returns:
            factor_id: 注册后的因子ID
            
        Raises:
            ValueError: 因子验证失败
        """
        factor_id = factor.get('factor_id')
        if not factor_id:
            factor_id = f"AI_{factor.get('method', 'UNKNOWN')}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            factor['factor_id'] = factor_id
        
        self._validate_factor(factor)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO factor_registry 
            (factor_id, factor_name, method, expression, ic_mean, ic_ir, ic_std, 
             complexity, status, created_at, updated_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            factor_id,
            factor.get('factor_name', 'Unknown'),
            factor.get('method', 'unknown'),
            factor.get('expression', ''),
            factor.get('ic_mean', 0.0),
            factor.get('ic_ir', 0.0),
            factor.get('ic_std', 0.0),
            factor.get('complexity', 0),
            'experimental',
            datetime.now().isoformat(),
            datetime.now().isoformat(),
            json.dumps(factor)
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"因子注册成功: {factor_id}")
        return factor_id
    
    def _validate_factor(self, factor: Dict):
        """
        验证因子
        
        Args:
            factor: 因子字典
            
        Raises:
            ValueError: 验证失败
        """
        required_fields = ['factor_name', 'method']
        for field in required_fields:
            if field not in factor:
                raise ValueError(f"缺少必需字段: {field}")
        
        ic_mean = factor.get('ic_mean', 0)
        if abs(ic_mean) < 0.01:
            logger.warning(f"因子IC值较低: {ic_mean}")
    
    def get_factor(self, factor_id: str) -> Optional[Dict]:
        """
        获取因子
        
        Args:
            factor_id: 因子ID
            
        Returns:
            因子字典
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT factor_id, factor_name, method, expression, ic_mean, ic_ir, 
                   ic_std, complexity, status, created_at, metadata
            FROM factor_registry
            WHERE factor_id = ?
        ''', (factor_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'factor_id': row[0],
                'factor_name': row[1],
                'method': row[2],
                'expression': row[3],
                'ic_mean': row[4],
                'ic_ir': row[5],
                'ic_std': row[6],
                'complexity': row[7],
                'status': row[8],
                'created_at': row[9],
                'metadata': json.loads(row[10]) if row[10] else {}
            }
        
        return None
    
    def list_factors(self, method: Optional[str] = None, status: Optional[str] = None) -> list:
        """
        列出因子
        
        Args:
            method: 方法过滤
            status: 状态过滤
            
        Returns:
            因子列表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = 'SELECT factor_id, factor_name, method, ic_mean, status FROM factor_registry WHERE 1=1'
        params = []
        
        if method:
            query += ' AND method = ?'
            params.append(method)
        
        if status:
            query += ' AND status = ?'
            params.append(status)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'factor_id': row[0],
                'factor_name': row[1],
                'method': row[2],
                'ic_mean': row[3],
                'status': row[4]
            }
            for row in rows
        ]
    
    def update_status(self, factor_id: str, status: str):
        """
        更新因子状态
        
        Args:
            factor_id: 因子ID
            status: 新状态
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE factor_registry
            SET status = ?, updated_at = ?
            WHERE factor_id = ?
        ''', (status, datetime.now().isoformat(), factor_id))
        
        conn.commit()
        conn.close()
        
        logger.info(f"因子状态更新: {factor_id} -> {status}")
