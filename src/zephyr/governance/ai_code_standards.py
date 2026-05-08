from __future__ import annotations

CODE_CONVENTIONS: dict[str, str] = {
    "file_org": "按YAML约定abord",
    "scaffold": "python setup+page=模板自动生成",
    "header": "Python: shebang+path",
    "comments": "no justification/no redundant→code self-document→majors only",
    "imports": "future→stdlib→3rd→local+isort",
    "type_hints": "全部public函数must",
}

AI_FORBIDDEN: list[str] = [
    "禁止生成注释in demo/example",
    "测试必须Fail(TDD mode)→pass=bad",
]
