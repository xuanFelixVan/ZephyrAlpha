# scripts 局部宪法（投影，立法权在根宪法）

- 本目录是什么：脚本区（700+ 个 .py；治理生成器在 governance/generators/）。
- 真源指针：脚本清单=scripts/script-manifest.yaml（机生，REG-SCRIPT-001）；governance 子集=scripts/governance/script_manifest.yaml。
- 禁止：裸 `git commit`——一律 `python scripts/git_commit.py --session <sid>`。
- 禁止：新建脚本不登记 manifest；.ps1 含非 ASCII 字符（GBK 假语法错误，根宪法 §9 条目 7）；向 `.runtime` 根直写。
- 单口：再生清单 `python scripts/governance/generators/generate_script_manifest.py`。
- 单口：查脚本 `python -m zephyr.library.lookup <名>`；提交队列 `python scripts/commit_queue.py enqueue/status/drain`。
- 静态清单禁手工维护：条目列表+计数一律生成器产出（根宪法 §9 条目 5）。
- 冲突裁决：以根宪法为准；本文件仅局部提醒，不新增规则。
- 引用格式：引用根宪法用"根宪法 §N"字样。
