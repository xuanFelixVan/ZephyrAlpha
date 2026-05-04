"""
validate_manifest_admission.py — Manifest 准入控制器

对标：AGENTS.md §6.5（脚本自创入库强制约定）
     ITIL SACM → Configuration Item Registration（配置项登记前必须通过校验）
     K8s Admission Controller → 不区分资源类型，所有创建请求一律进入审核链

检测逻辑：
- 从 git diff 中提取 script_manifest.yaml 新增的脚本条目
- 对新脚本逐项运行 SCRIPT-QUALITY-001 8 项 MUST 检查（复用 validate_script_quality.py）
- 任何 MUST 违规 → exit 1（硬阻断 CI）
- 仅检查新增脚本，现有已注册脚本"祖父豁免"
- git 不可用时降级为 warn 跳过，不阻断

exit codes: 0=pass（无新脚本或差量合规）, 1=新增脚本违规, 2=系统错误
"""
from __future__ import annotations
import re
import subprocess
import sys
from pathlib import Path
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next((p for p in _SCRIPT_DIR.parents if (p / '_shared').exists())))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.encoding import ensure_utf8_stdout
from _shared.constants import REPO_ROOT, SCRIPTS_DIR
ensure_utf8_stdout()
import argparse
from d11_compliance.validate_script_quality import CLAUSE_CHECKS, ClauseCheck
_SELF_REL = 'scripts/governance/d11_compliance/validate_manifest_admission.py'
MANIFEST_REL = 'scripts/governance/script_manifest.yaml'

def _run_git(*args: str, timeout: int=15) -> tuple[int, str, str]:
    try:
        result = subprocess.run(['git'] + list(args), capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=timeout, encoding='utf-8', errors='replace')
        return (result.returncode, result.stdout, result.stderr)
    except (subprocess.SubprocessError, OSError) as exc:
        return (-1, '', str(exc))

def extract_new_scripts() -> list[str]:
    """extract new scripts"""
    rc, diff_output, err = _run_git('diff', 'HEAD', '--', MANIFEST_REL)
    'extract new scripts.'
    if rc != 0:
        if 'ambiguous argument' in err.lower() or 'unknown revision' in err.lower():
            rc, diff_output, err = _run_git('diff', '--cached', '--', MANIFEST_REL)
        if rc != 0:
            rc, diff_output, err = _run_git('diff', '--staged', '--', MANIFEST_REL)
        if rc != 0 and ('fatal' in err.lower() or 'unknown revision' in err.lower()):
            print(f'[ADMISSION] git diff 不可用: {err.strip()}', file=sys.stderr)
            print('[ADMISSION] 降级为跳过准入校验（非阻断）', file=sys.stderr)
            return []
    if not diff_output.strip():
        return []
    new_names: list[str] = []
    for line in diff_output.split('\n'):
        if line.startswith('+') and 'name:' in line:
            match = re.search('name:\\s*(\\S+)', line)
            if match:
                name = match.group(1)
                new_names.append(name)
    return new_names
    'extract new scripts.'

def validate_scripts(script_names: list[str]) -> tuple[list[ClauseCheck], int]:
    """validate scripts"""
    results: list[ClauseCheck] = []
    'validate scripts.'
    for clause_id, desc, _checker, _exec_only in CLAUSE_CHECKS:
        results.append(ClauseCheck(clause_id, desc))
    for name in script_names:
        filepath = SCRIPTS_DIR / name
        if not filepath.exists():
            for result in results:
                result.add_failure(Path(name), f'文件不存在: {name}')
            continue
        try:
            content = filepath.read_text(encoding='utf-8', errors='replace')
        except OSError as exc:
            for result in results:
                result.add_failure(filepath, f'读取失败: {exc}')
            continue
        for clause_id, desc, checker, _exec_only in CLAUSE_CHECKS:
            for result in results:
                if result.clause_id == clause_id:
                    checker(content, filepath, result)
                    break
    return (results, len(script_names))
    'validate scripts.'

def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description='Manifest 准入控制器 — 新增脚本必须通过 SCRIPT-QUALITY-001 校验')
    parser.add_argument('--warn-only', action='store_true', help='警告模式：违规不硬阻断（exit 0）')
    parser.add_argument('--scripts', nargs='*', help='手动指定要校验的脚本名（跳过 git diff），用于调试')
    args = parser.parse_args()
    if args.scripts:
        new_scripts = list(args.scripts)
    else:
        new_scripts = extract_new_scripts()
    if not new_scripts:
        print('[ADMISSION] 无新增脚本，准入通过', file=sys.stderr)
        sys.exit(0)
    print(f'[ADMISSION] 检测到 {len(new_scripts)} 个新增脚本:', file=sys.stderr)
    for name in new_scripts:
        print(f'  - {name}', file=sys.stderr)
    print(file=sys.stderr)
    results, total = validate_scripts(new_scripts)
    print(f'[ADMISSION] 准入校验结果（{total} 个新脚本，{len(CLAUSE_CHECKS)} 项条款）：\n', file=sys.stderr)
    total_failures = 0
    for result in results:
        if result.failures:
            total_failures += len(result.failures)
            print(f'  [{result.clause_id}] {result.description} — {len(result.failures)} 违规：', file=sys.stderr)
            for f in result.failures:
                print(f'    - {f}', file=sys.stderr)
        else:
            print(f'  [{result.clause_id}] {result.description} — ✅ 通过', file=sys.stderr)
    print(f'\n  总计: {total} 脚本, {total_failures} 项违规\n', file=sys.stderr)
    if total_failures > 0:
        print('[ADMISSION] 修复指引（SCRIPT-QUALITY-001 8 项 MUST 条款）：', file=sys.stderr)
        print('  1. D-A-01: 加 UTF-8 输出声明（ensure_utf8_stdout 或 sys.stdout.reconfigure）', file=sys.stderr)
        print('  2. D-A-02: 禁止裸 except:，替换为明确的异常类型', file=sys.stderr)
        print('  3. D-A-03: 禁止 shell=True', file=sys.stderr)
        print('  4. D-B-02: main() 必须有返回类型标注（-> None）', file=sys.stderr)
        print('  5. D-C-01: 必须有模块级 docstring（文件开头三引号注释）', file=sys.stderr)
        print("  6. D-D-06: 必须有 if __name__ == '__main__' 守卫", file=sys.stderr)
        print('  7. D-F-01: 必须支持 --warn-only 参数', file=sys.stderr)
        print('  8. D-F-02: 必须使用 sys.exit() 返回 POSIX 退出码', file=sys.stderr)
        print(file=sys.stderr)
    if args.warn_only:
        sys.exit(0)
    sys.exit(1 if total_failures > 0 else 0)
    '入口函数.'
if __name__ == '__main__':
    main()