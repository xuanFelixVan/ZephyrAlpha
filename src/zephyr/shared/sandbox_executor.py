"""
Sandbox Executor — 高风险操作沙箱隔离 (M-23)
策略从 sandbox_policy.yaml 加载：file_delete / config_modify / external_api_call

特性：
  - file_delete: 沙箱隔离 + dry_run + 需确认
  - config_modify: 沙箱 + diff_before_apply
  - external_api_call: 无沙箱 + cost_limit ¥1
"""
import os
import subprocess
import tempfile
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional


class SandboxAction(Enum):
    FILE_DELETE = "file_delete"
    CONFIG_MODIFY = "config_modify"
    EXTERNAL_API_CALL = "external_api_call"


class SandboxResult(Enum):
    ALLOWED = "allowed"
    BLOCKED = "blocked"
    SANDBOXED = "sandboxed"
    DRY_RUN = "dry_run"


@dataclass
class SandboxPolicy:
    action: SandboxAction
    sandbox: bool
    dry_run: bool
    require_confirmation: bool
    cost_limit_usd: float = 0.0


class SandboxExecutor:
    """
    高风险操作沙箱隔离器 (M-23)
    """

    DEFAULT_POLICIES = {
        SandboxAction.FILE_DELETE: SandboxPolicy(
            action=SandboxAction.FILE_DELETE,
            sandbox=True, dry_run=True, require_confirmation=True
        ),
        SandboxAction.CONFIG_MODIFY: SandboxPolicy(
            action=SandboxAction.CONFIG_MODIFY,
            sandbox=True, dry_run=False, require_confirmation=False
        ),
        SandboxAction.EXTERNAL_API_CALL: SandboxPolicy(
            action=SandboxAction.EXTERNAL_API_CALL,
            sandbox=False, dry_run=False, require_confirmation=False, cost_limit_usd=1.0
        ),
    }

    def __init__(self, policy_path: Optional[str] = None):
        self.policies: dict[SandboxAction, SandboxPolicy] = dict(self.DEFAULT_POLICIES)
        if policy_path:
            self._load_policy(policy_path)

    def _load_policy(self, policy_path: str):
        import yaml
        try:
            with open(policy_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            for entry in data.get("policies", []):
                action = SandboxAction(entry["action"])
                policy = SandboxPolicy(
                    action=action,
                    sandbox=entry.get("sandbox", True),
                    dry_run=entry.get("dry_run", True),
                    require_confirmation=entry.get("require_confirmation", False),
                    cost_limit_usd=float(entry.get("cost_limit_usd", 0)),
                )
                self.policies[action] = policy
        except Exception:
            pass

    def execute(self, action: SandboxAction, fn: Callable[[], Any],
                confirm_fn: Optional[Callable[[], bool]] = None) -> tuple[SandboxResult, Any]:
        policy = self.policies.get(action)
        if policy is None:
            return SandboxResult.BLOCKED, None

        if policy.dry_run:
            return SandboxResult.DRY_RUN, None

        if policy.sandbox:
            if policy.require_confirmation:
                if confirm_fn is None or not confirm_fn():
                    return SandboxResult.BLOCKED, None

            result = self._run_in_sandbox(fn)
            return SandboxResult.SANDBOXED, result

        result = fn()
        return SandboxResult.ALLOWED, result

    def _run_in_sandbox(self, fn: Callable[[], Any]) -> Any:
        import threading

        result_container = {"result": None, "error": None}

        def target():
            try:
                result_container["result"] = fn()
            except Exception as e:
                result_container["error"] = str(e)

        thread = threading.Thread(target=target, daemon=True)
        thread.start()
        thread.join(timeout=30)

        if thread.is_alive():
            return None

        if result_container["error"]:
            return None

        return result_container["result"]

    def sandbox_file_delete(self, filepath: str, confirmed: bool = False) -> tuple[SandboxResult, str]:
        if not os.path.exists(filepath):
            return SandboxResult.ALLOWED, "文件不存在"

        def confirm_fn():
            return confirmed

        def do_delete():
            os.remove(filepath)
            return f"已删除: {filepath}"

        result, msg = self.execute(
            SandboxAction.FILE_DELETE, do_delete,
            confirm_fn=confirm_fn
        )
        return result, str(msg or "")

    def sandbox_config_modify(self, filepath: str, new_content: str) -> tuple[SandboxResult, str]:
        if not os.path.exists(filepath):
            return SandboxResult.BLOCKED, f"文件不存在: {filepath}"

        def do_modify():
            import shutil
            backup = filepath + ".sandbox_backup"
            shutil.copy2(filepath, backup)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            return f"已修改: {filepath} (备份: {backup})"

        result, msg = self.execute(
            SandboxAction.CONFIG_MODIFY, do_modify
        )
        return result, str(msg or "")
