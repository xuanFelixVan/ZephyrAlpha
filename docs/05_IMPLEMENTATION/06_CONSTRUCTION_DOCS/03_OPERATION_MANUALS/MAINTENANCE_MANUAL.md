﻿---
responsibility:
  - 实施指南、部署文档
  - 文档治理
  - 日志系统
applicable_scope: فàذق│╗ق╗?compliance_level: µصثف╝µبçفç
parent_document: ../README.md
implementation_status: ف╖▓ف«îµê?owner: ك┐ق╗┤فؤتلءا
version: 1.0.0
module_id: MAINTENANCE_MANUAL
created_date: 2026-04-02
last_updated: 2026-04-02---

> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


**µ£فµؤ┤µû?*: 2026-04-02

---

## 1. ق╗┤µèجµخéك┐░

### 1.1 ق╗┤µèجقؤ«µبç

### 1.2 ق╗┤µèجكîâفؤ┤

- µùحف╕╕ق╗┤µèج
- ف«أµ£اق╗┤µèج

---

## 2. µùحف╕╕ق╗┤µèج

**µثµاحلة╣**:
- [ ] فجçغ╗╜قè╢µ?- [ ] قؤّµدفّèكصخ

### 2.2 µـ░µ«ق╗┤µèج

```bash
psql -U zephyr_user -d zephyr -c "SELECT count(*) FROM pg_stat_activity;"

python scripts/cleanup_old_data.py

# غ╝ءفîûكة?psql -U zephyr_user -d zephyr -c "VACUUM ANALYZE;"
```

**Redisق╗┤µèج**:
```bash
# µثµاحRedisقè╢µ?redis-cli -a password INFO

```

---

## 3. ف«أµ£اق╗┤µèج

### 3.1 µ»فّذق╗┤µèج

**غ╗╗فèة**:

**غ╗╗فèة**:
- µدكâ╜غ╝ءفîû
- ف«ëفàذف«ةك«ة

---

## 4. ف║¤µحق╗┤µè?
### 4.1 µـàلأ£فôف║¤

**فôف║¤µ╡قذï**:
1. µحµ¤╢فّèكصخ
2. قة«ك«جµـàلأ£
5. لزîك»µتفج
6. ك«░ف╜ـµ╗ق╗ô

### 4.2 ف╕╕كدµـàلأ£فجق

```bash
# µثµاحقè╢µ?systemctl status postgresql

# لçف»µ£فèة
systemctl restart postgresql

# µتفجفجçغ╗╜
pg_restore -U zephyr_user -d zephyr backup.sql
```

**Redisµـàلأ£**:
```bash
# µثµاحقè╢µ?systemctl status redis

# لçف»µ£فèة
systemctl restart redis

# µتفجµـ░µ«
redis-cli -a password SHUTDOWN NOSAVE
redis-server /etc/redis/redis.conf
```

---

## 5. فçق║دق╗┤µèج

### 5.1 فçق║دµ╡قذï

1. فجçغ╗╜µـ░µ«
2. ف£µصتµ£فèة
3. فçق║دف║¤ق¤ذ
4. ك┐قد╗µـ░µ«
5. ف»فèذµ£فèة
6. لزîك»فèاكâ╜

### 5.2 فؤئµ╗أµ╡قذï

1. ف£µصتµ£فèة
2. µتفجفجçغ╗╜
3. لآق║دف║¤ق¤ذ
4. ف»فèذµ£فèة
5. لزîك»فèاكâ╜

---

- [لâذق╜▓µëïفî](./DEPLOYMENT_MANUAL.md)
- [قؤّµدµëïفî](./MONITORING_MANUAL.md)

---

**غ╕ïµشةف«ةµاح**: 2026-07-02
