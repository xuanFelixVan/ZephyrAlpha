---
module_id: KE-1363
status: active
title: 10.3 反向测试——"不动"的边界
category: module_blueprint
---

# 10.3 反向测试——"不动"的边界

10.3 反向测试——"不动"的边界

```python
def test_forbidden_patterns_are_untouched():
    """验证禁碰规则真的不会被触发。"""
    auditor = SemanticAuditor()
    safe_doc = """
    # 不应该被改的规则
    我们选择了 SQLite 作为数据库（架构决策）
    TTL 设置为 30 分钟
    """
    report = auditor.audit(safe_doc)
    assert len(report.red_issues) == 0   # 任何禁碰模式都不应触发
```

---
