---

task_id: TASK-INF-0209
task_title: "§7 Vibe Coding与1人+AI维护专属优化——IDE热重载/零上下文启动/新文件自动注册"
parent_ticket: TASK-INF-0201
module: MOD-INF-019
blueprint_file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-spec\\blueprint.md"
blueprint_sections: ["§7 Vibe Coding与1人+AI维护专属优化"]
status: backlog
priority: P1
type: optimization
estimated_effort: "8h"
assignee: implementer-skill
reviewer: governor-skill
created_date: 2026-05-06
target_completion_date: 2026-05-07
dependencies:
  - TASK-INF-0205
tags:
  - vibe-coding
  - solo-maintenance
  - ide-hot-reload
  - zero-context
severity: medium
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-spec\\blueprint.md"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\ide_watcher.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\file_autorregister.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\context_optimizer.py"
acceptance_criteria:
  - "IDE热重载：Skill 文件变更 → AGENTS.md 自动刷新 → 下一个对话自动加载新版 Skill，无需重启 IDE"
  - "零上下文启动：新对话前三轮自动加载 Onboarding Skill → 第4轮起跳过"
  - "新文件自动注册：新建 .py → 自动在 script_manifest.yaml 注册 → 关联 Domain Skill 创建"
  - "单命令部署：python -m zephyr.agent_spec deploy --all 一键部署全部 Skill"
rollback_instructions: "删除 ide_watcher.py, file_autorregister.py, context_optimizer.py"
context_assembly_manifest:
  blueprint_content: "§7 Vibe Coding专属优化——针对1人+AI维护场景的IDE热重载、零上下文启动、新文件自动注册三大优化"
  template_version: "task-card-template.md v1.0.0"
blueprint_id: DOM-GOV-001
---


# TASK-INF-0209: Vibe Coding 专属优化

## 1. 任务描述

实现 §7 定义的 Vibe Coding 场景三大优化：IDE 热重载、零上下文启动、新文件自动注册。针对 1 人 + AI 维护场景，降低 IDE 切换、重启和手动配置的 friction。

## 2. 实施方案

### 2.1 IDE 热重载

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

### 2.2 零上下文启动

```python
class ContextOptimizer:
    def warm_start(self, session_count: int):
        if session_count <= 3:
            return self._load_onboarding_skill()
        return None

    def progressive_context_build(self, task_description: str):
        """从零上下文开始，按需加载，避免一次性加载全部 Skill metadata"""
        ...
```

### 2.3 新文件自动注册

```python
class FileAutoRegister:
    def on_new_python_file(self, file_path: str):
        if file_path.startswith(self.src_zephyr_path):
            self._register_in_script_manifest(file_path)
            if self._is_new_module(file_path):
                self._trigger_skill_factory(file_path)
```

### 2.4 一键部署

```bash
python -m zephyr.agent_spec deploy --all
# → 遍历所有 Domain/Role Skills → 验证 → 编译触发表 → 生成 AGENTS.md → 发布
```

## 3. 验收标准

- [ ] IDE 热重载延迟 < 2s
- [ ] 前三对话 Onboarding Skill 正常加载
- [ ] 新 .py 自动注册延迟 < 5s
- [ ] 一键部署可用

## 4. 回滚说明

`git revert <commit_hash>`