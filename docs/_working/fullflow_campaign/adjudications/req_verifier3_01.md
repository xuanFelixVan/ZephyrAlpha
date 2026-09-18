---
ttl: task_bound
completes_when: 总包据本处方修复后关闭
---

# 处方 req_verifier3_01 — sanctioned 工具 `add_module_translation.py` 已坏（缺 re-export）

请求方=`st-ff-verifier3-20260918`　处置方=总包（本车道禁改 `src/zephyr/**` 与他人共享件）
严重度=**中（阻断面）**：TRANSLATION-COVERAGE 门禁指定的唯一修复入口不可用，
任何新建 `.py` 的车道都会在此撞死，且报错信息不指向真因。

## 现象（本会话亲验）

```
$ python scripts/governance/d3_metadata/add_module_translation.py --help
Traceback (most recent call last):
  File "D:\ZephyrAlpha\scripts\governance\d3_metadata\add_module_translation.py", line 105, in <module>
    from _shared.yaml_utils import (  # noqa: E402 — re-export of SSoT src/zephyr/shared/io/yaml_utils
ImportError: cannot import name 'DEFAULT_REGISTRY_CATALOG_DIR' from '_shared.yaml_utils'
  (D:\ZephyrAlpha\scripts\governance\_shared\yaml_utils.py)
```

## 根因

- 符号在 SSoT 里**存在**：`src/zephyr/shared/io/yaml_utils.py:48`
  `DEFAULT_REGISTRY_CATALOG_DIR: Final[Path] = REPO_ROOT / "docs" / ... / "catalogs"`
- `scripts/governance/_shared/yaml_utils.py` 是它的 **re-export shim**，但 shim 里
  `grep -n "DEFAULT_REGISTRY_CATALOG_DIR"` → **0 命中**（亲验），即 shim 漏转出一项。
- 消费方 `add_module_translation.py:105` 按注释声明的契约（"re-export of SSoT"）导入 → ImportError。

## 请办

1. 在 `scripts/governance/_shared/yaml_utils.py` 的 re-export 清单中补
   `DEFAULT_REGISTRY_CATALOG_DIR`（与其 `__all__` 同步），使之真正兑现"SSoT re-export"契约。
2. 加一条**契约测试**：shim 的 `__all__` ⊇ SSoT 模块中被 `scripts/**` 引用的全部符号
   （现故障模式=SSoT 增符号、shim 不同步、只在运行期 ImportError，无静态检出面）。
   建议放 `tests/governance/test_shared_yaml_utils_reexport.py`，零写生产路径。
3. 顺带核 `scripts/governance/_shared/` 下其余 shim 是否同型漏转出（同家族大概率同病）。

## 本车道的绕行（已做，不构成长期方案）

用 `zephyr.shared.io.file_utils.safe_write_text` 直写
`module_translation_registry.yaml`，带 `expected_base_sha256`（CAS）+ `newline="\n"`，
写后 `yaml.safe_load` 复验 `entries` 7117→7119、`git diff --stat` 仅 16 行纯增、无外来内容。
热文件写前遇 `PermissionError`（并发窗口）2 次，第 3 次成功 → 绕行代价是需自带退避重试，
这正是 sanctioned 工具应替调用方承担的事。**故本处方仍须办，绕行不是治本。**
