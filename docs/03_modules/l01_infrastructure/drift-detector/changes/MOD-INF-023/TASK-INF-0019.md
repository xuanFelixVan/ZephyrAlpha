---
task_id: "TASK-INF-0019"
title: "文件底层属性漂移检测 file_attr_checker.py（D-023-27）"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P1"
status: "draft"
estimated_effort: "3h"
depends_on: ["TASK-INF-0001"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"]
downstream_outputs: ["D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\file_attr_checker.py"]
acceptance_criteria:
  - "encoding: chardet检测编码→与UTF-8无BOM标准对比；auto_fixable→自动转换UTF-8"
  - "line_ending: 检测\r\n混用→LINE_ENDING_MIXED；auto_fixable→.gitattributes声明LF不自动改已有文件"
  - "file_permissions: .py文件非__main__入口不应有+x；auto_fixable"
  - "gitattributes_enforcement: 检查.gitattributes覆盖所有关键文件类型(∗.py/∗.yaml/∗.md text eol=lf)"
rollback_instructions: "git checkout src/zephyr/drift_detector/file_attr_checker.py"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§2.18"]}]
tags: ["drift-detector","file-attributes","encoding","D-023-27"]
---
# TASK-INF-0019: 文件底层属性漂移（D-023-27）
对标 §2.18。实现编码(BOM/UTF-16/Latin-1)、换行符(CRLF vs LF)、可执行位、.gitattributes 四维检测，auto_fixable。
