---
module_id: KE-2769
status: active
title: Leader Election via SQLite Lease（多节点主选举）
category: module_blueprint
ttl: permanent
---

# Leader Election via SQLite Lease（多节点主选举）

Leader Election via SQLite Lease（多节点主选举）

```python
class SqliteLeaderElection:
    """最简单的 Leader Election——SQLite 做租约存储。
    只适用于单数据中心3-5节点——不是 Raft，是"轻量级主选举"。
    """
    _lease_table = "leader_lease"
    _lease_id = "global_leader"
    _lease_ttl: float = 30.0    # 租约 TTL 30s
    _renew_interval: float = 10.0  # 每 10s 续约

    async def try_become_leader(self) -> bool:
        """INSERT OR REPLACE 原子操作竞争 Leader"""
        now = time.time()
        result = await self.db.execute(
            f"""INSERT OR REPLACE INTO {self._lease_table}
                (lease_id, node_id, acquired_at, expires_at)
                VALUES (?, ?, ?, ?)
                WHERE NOT EXISTS (
                    SELECT 1 FROM {self._lease_table}
                    WHERE lease_id = ? AND expires_at > ?
                )""",
            (self._lease_id, self.node_id, now, now + self._lease_ttl,
             self._lease_id, now)
        )
        return result.rowcount > 0

    async def is_leader(self) -> bool:
        """检查当前节点是否仍为 Leader"""
        row = await self.db.fetchone(
            f"SELECT node_id FROM {self._lease_table} "
            f"WHERE lease_id = ? AND expires_at > ?",
            (self._lease_id, time.time())
        )
        return row is not None and row[0] == self.node_id

    async def step_down(self) -> None:
        """主动让位——退出前通知集群"""
        await self.db.execute(
            f"DELETE FROM {self._lease_table} WHERE node_id = ?",
            (self.node_id,)
        )
```
