---
module_id: KE-1773
status: active
title: 2.2 SkillFactory 类实现
category: module_blueprint
---

# 2.2 SkillFactory 类实现

2.2 SkillFactory 类实现

```python
class SkillFactory:
    def generate_domain_skill(self, module_name: str, blueprint_path: str) -> str:
        questions = self._extract_module_info(module_name, blueprint_path)
        template = self._load_template("SKILL_TEMPLATE.md")
        skill_content = self._render_template(template, questions)
        skill_path = self._write_skill_file(module_name, skill_content)
        self._update_registry(module_name, skill_path)
        self._update_trigger_table(module_name)
        return skill_path

    def bootstrap_sequence(self, module_name: str, blueprint_path: str):
        yield "create_blueprint", f"Creating blueprint for {module_name}"
        yield "factory_generate", self.generate_domain_skill(module_name, blueprint_path)
        yield "human_review", "Human reviews SKILL.md and approves"
        yield "register", f"Skill registered in skill-registry.yaml"
```
