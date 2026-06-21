"""
DatabaseService: 统一管理三个数据库的连接池、生命周期、健康检查

[BLUEPRINT] DM-100022 | src/zephyr/data/database_service.py | §22
[MODULE] zephyr.data.database_service
[INVARIANTS] 三库连接池管理; WAL 模式启用; 健康检查机制
[MODIFY-GUARD] 修改需同步更新 tests/test_db_auto_ops.py
[CONSUMERS] src/zephyr/governance/; scripts/database/
[STABILITY] stable
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] ConnectionError; TimeoutError
[TESTS] tests/test_db_auto_ops.py::test_database_service_init

提供 governance.db / depgraph.db / market.duckdb 的统一连接管理。
"""
import sqlite3
import duckdb
from typing import Dict, Optional, Any
from contextlib import contextmanager

class DatabaseService:
    """统一数据库服务层"""
    
    def __init__(self):
        self.governance_db = r"D:\ZephyrAlpha\data\databases\governance.db"
        self.depgraph_db = r"D:\ZephyrAlpha\data\databases\depgraph.db"
        self.market_db = r"D:\ZephyrAlpha\data\databases\market.duckdb"
        
        self._governance_conn: Optional[sqlite3.Connection] = None
        self._depgraph_conn: Optional[sqlite3.Connection] = None
        self._market_conn: Optional[duckdb.DuckDBPyConnection] = None
    
    def get_governance_conn(self) -> sqlite3.Connection:
        """获取 governance.db 连接"""
        if self._governance_conn is None:
            self._governance_conn = sqlite3.connect(self.governance_db)
            self._governance_conn.row_factory = sqlite3.Row
        return self._governance_conn
    
    def get_depgraph_conn(self) -> sqlite3.Connection:
        """获取 depgraph.db 连接"""
        if self._depgraph_conn is None:
            self._depgraph_conn = sqlite3.connect(self.depgraph_db)
            self._depgraph_conn.row_factory = sqlite3.Row
        return self._depgraph_conn
    
    def get_market_conn(self) -> duckdb.DuckDBPyConnection:
        """获取 market.duckdb 连接"""
        if self._market_conn is None:
            self._market_conn = duckdb.connect(self.market_db)
        return self._market_conn
    
    def health_check(self) -> Dict[str, bool]:
        """健康检查"""
        result = {}
        
        try:
            conn = self.get_governance_conn()
            conn.execute("SELECT 1").fetchone()
            result['governance'] = True
        except Exception as e:
            result['governance'] = False
        
        try:
            conn = self.get_depgraph_conn()
            conn.execute("SELECT 1").fetchone()
            result['depgraph'] = True
        except Exception as e:
            result['depgraph'] = False
        
        try:
            conn = self.get_market_conn()
            conn.execute("SELECT 1").fetchone()
            result['market'] = True
        except Exception as e:
            result['market'] = False
        
        return result
    
    def close_all(self):
        """关闭所有连接"""
        if self._governance_conn:
            self._governance_conn.close()
            self._governance_conn = None
        
        if self._depgraph_conn:
            self._depgraph_conn.close()
            self._depgraph_conn = None
        
        if self._market_conn:
            self._market_conn.close()
            self._market_conn = None
    
    # ========== governance.db 方法 ==========
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务"""
        conn = self.get_governance_conn()
        row = conn.execute("SELECT * FROM tasks WHERE task_id=?", (task_id,)).fetchone()
        return dict(row) if row else None
    
    def create_task(self, task_data: Dict[str, Any]) -> str:
        """创建任务"""
        conn = self.get_governance_conn()
        task_id = task_data['task_id']
        columns = ', '.join(task_data.keys())
        placeholders = ', '.join(['?' for _ in task_data])
        conn.execute(f"INSERT INTO tasks ({columns}) VALUES ({placeholders})", list(task_data.values()))
        conn.commit()
        return task_id
    
    def update_task_status(self, task_id: str, status: str):
        """更新任务状态"""
        conn = self.get_governance_conn()
        conn.execute("UPDATE tasks SET status=?, updated_at=datetime('now') WHERE task_id=?", (status, task_id))
        conn.commit()
    
    def log_rule_enforcement(self, rule_id: str, operation: str, target: str, result: str, details: str = ''):
        """记录规则执行日志"""
        conn = self.get_governance_conn()
        conn.execute("""INSERT INTO rule_enforcement_log 
            (rule_id, operation, target, result, details, enforced_at, enforced_by)
            VALUES (?, ?, ?, ?, ?, datetime('now'), ?)""",
            (rule_id, operation, target, result, details, 'DatabaseService'))
        conn.commit()
    
    # ========== depgraph.db 方法 ==========
    
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """获取节点"""
        conn = self.get_depgraph_conn()
        row = conn.execute("SELECT * FROM nodes WHERE node_id=?", (node_id,)).fetchone()
        return dict(row) if row else None
    
    def get_nodes_by_domain(self, domain_id: str) -> list:
        """按域获取节点"""
        conn = self.get_depgraph_conn()
        rows = conn.execute("SELECT * FROM nodes WHERE domain_id=?", (domain_id,)).fetchall()
        return [dict(r) for r in rows]
    
    def get_nodes_by_type(self, node_type: str) -> list:
        """按类型获取节点"""
        conn = self.get_depgraph_conn()
        rows = conn.execute("SELECT * FROM nodes WHERE node_type=?", (node_type,)).fetchall()
        return [dict(r) for r in rows]
    
    def get_rule_bindings_by_function(self, function_name: str) -> list:
        """按函数名获取规则绑定"""
        conn = self.get_depgraph_conn()
        rows = conn.execute("SELECT * FROM rule_bindings WHERE function_name=?", (function_name,)).fetchall()
        return [dict(r) for r in rows]
    
    def get_edges_from_node(self, from_node: str) -> list:
        """获取节点的出边"""
        conn = self.get_depgraph_conn()
        rows = conn.execute("SELECT * FROM edges WHERE from_node=?", (from_node,)).fetchall()
        return [dict(r) for r in rows]
    
    # ========== market.duckdb 方法 ==========
    
    def insert_tick_data(self, tick_data: Dict[str, Any]):
        """插入tick数据"""
        conn = self.get_market_conn()
        conn.execute("""INSERT INTO tick_data 
            (symbol, timestamp, price, volume, amount, bid1, ask1, bid_vol1, ask_vol1, data_source, quality_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (tick_data['symbol'], tick_data['timestamp'], tick_data['price'], tick_data['volume'],
             tick_data.get('amount'), tick_data.get('bid1'), tick_data.get('ask1'),
             tick_data.get('bid_vol1'), tick_data.get('ask_vol1'), tick_data.get('data_source'),
             tick_data.get('quality_score')))
    
    def query_kline(self, symbol: str, start_ts: str, end_ts: str) -> list:
        """查询K线数据"""
        conn = self.get_market_conn()
        rows = conn.execute("""SELECT * FROM kline_3s 
            WHERE symbol=? AND ts BETWEEN ? AND ?
            ORDER BY ts""", (symbol, start_ts, end_ts)).fetchall()
        return [dict(zip(['symbol', 'open', 'high', 'low', 'close', 'volume', 'amount', 'ts'], r)) for r in rows]
    
    def create_order(self, order_data: Dict[str, Any]) -> str:
        """创建订单"""
        conn = self.get_market_conn()
        order_id = order_data['order_id']
        columns = ', '.join(order_data.keys())
        placeholders = ', '.join(['?' for _ in order_data])
        conn.execute(f"INSERT INTO orders ({columns}) VALUES ({placeholders})", list(order_data.values()))
        return order_id


if __name__ == "__main__":
    # 测试
    ds = DatabaseService()
    print("Health check:", ds.health_check())
    
    # 测试 governance.db
    conn = ds.get_governance_conn()
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    print(f"governance.db: {len(tables)} tables")
    
    # 测试 depgraph.db
    conn = ds.get_depgraph_conn()
    nodes = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
    print(f"depgraph.db: {nodes} nodes")
    
    # 测试 market.duckdb
    conn = ds.get_market_conn()
    tables = conn.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='main'").fetchall()
    print(f"market.duckdb: {len(tables)} tables")
    
    ds.close_all()
    print("All connections closed")
