---
module_id: KE-module_blu-2_1_ide-000
title: 2.1 IDE 热重载
category: module_blueprint
---

# 2.1 IDE 热重载

2.1 IDE 热重载

```python
class IDEWatcher:
    """监视 Skill 文件变更 → 自动刷新 AGENTS.md → 下一个对话生效"""
    def watch_skill_files(self):
        import watchdog
        observer = watchdog.observers.Observer()
        observer.schedule(SkillChangeHandler(), self.skills_dir, recursive=True)
        observer.start()

    def on_skill_changed(self, skill_path: str):
        self._validate_skill(skill_path)
        self._update_agents_md(skill_path)
        self._increment_skill_version(skill_path)
```
