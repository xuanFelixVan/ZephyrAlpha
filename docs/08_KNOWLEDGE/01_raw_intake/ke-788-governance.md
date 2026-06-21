---
module_id: KE-711
title: 10. 历史教训记录
category: governance
---

# 10. 历史教训记录

10. 历史教训记录

| 日期 | 事件 | 根因 | 本标准对应条款 |
|------|------|------|-------------|
| 2026-04-24 | 旧体系 tests/unit/ 残留 8 个骨架测试 + 1 个漏迁文件 | T-2-34 搬迁任务只搬 files_in_scope 内文件，未检测 scope 外残留 | §4.3 残留物检测 |
| 2026-04-24 | 旧体系 scripts/infra/ 搬迁后目录空壳残留 | 搬迁脚本不删除空目录 | §4.3 ORPHAN_SHELL 分类 |
| 2026-04-24 | tmp_replace_composer*.py 未清理 | 临时脚本无 TTL 标记 | §4.2 temp_* 清除 |
