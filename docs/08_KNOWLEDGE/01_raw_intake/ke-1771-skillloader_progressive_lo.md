---
module_id: KE-1680
status: active
title: 2.1 SkillLoader.progressive_load()
category: module_blueprint
---

# 2.1 SkillLoader.progressive_load()

2.1 SkillLoader.progressive_load()

```python
class SkillLoader:
    def progressive_load(self, skill_id: str) -> dict:
        l1 = self._load_l1_frontmatter(skill_id)
        l2 = self._load_l2_body(skill_id)
        result = {"l1": l1, "l2": l2}
        result["l3_available"] = self._list_l3_references(skill_id)
        return result

    def _load_l1_frontmatter(self, skill_id: str) -> dict:
        """从 SKILL.md YAML frontmatter 加载 ~50 tokens metadata"""
        with open(self._resolve_skill_path(skill_id), 'r', encoding='utf-8') as f:
            content = f.read()
        frontmatter = self._parse_yaml_frontmatter(content)
        return {
            "skill_id": frontmatter.get("skill_id"),
            "name": frontmatter.get("name"),
            "description": frontmatter.get("description"),
            "allowed_tools": frontmatter.get("allowed-tools", []),
            "model_hint": frontmatter.get("model_hint"),
            "freshness_score": frontmatter.get("freshness_score", 100.0),
            "last_validated": frontmatter.get("last_validated"),
        }

    def _load_l2_body(self, skill_id: str) -> str:
        """从 SKILL.md 正文加载 ~500 tokens body"""
        body = self._extract_body_from_skill_file(skill_id)
        if len(self._tokenize(body)) > 500:
            body = self._compress_to_critical_rules(body)
        return body

    def load_l3_reference(self, skill_id: str, ref_name: str) -> str:
        """按需加载 L3 reference 文件"""
        ref_path = self._resolve_reference_path(skill_id, ref_name)
        with open(ref_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _compress_to_critical_rules(self, body: str) -> str:
        """提取仅 CRITICAL 规则段落，文本降级为关键词列表"""
        ...
```
