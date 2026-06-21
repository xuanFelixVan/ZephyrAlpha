---
module_id: KE-2710
status: active
title: dispatch 过程中记录每个模块的副作用
category: module_blueprint
---

# dispatch 过程中记录每个模块的副作用

dispatch 过程中记录每个模块的副作用
class SagaLogEntry(BaseModel):
    module_id: str
    action: str              # "created_file" | "modified_file" | "deleted_file"
    target_path: str
    backup_content: str|None # 回滚时恢复的原始内容
