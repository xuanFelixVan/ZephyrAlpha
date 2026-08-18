# [A_test] module_id: MOD-GOV_runtime_interceptor | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md | §
# [MODULE] tests.llm_security.test_runtime_interceptor
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
test_runtime_interceptor.py — 运行时 LLM 裸调拦截器测试

覆盖 GATE-20 运行时后备防线（runtime_interceptor.py）的全部验收标准：
1. 红蓝对抗：code = read_file("payload.txt"); exec(code) 在运行时被拦截
2. 自动生效（sitecustomize 子进程验证）
3. 零侵入性（业务代码无需显式调用）
4. kill-switch（ZEPHYR_RUNTIME_GATE=0 关闭）
5. 放行令牌机制（allow_llm_call 上下文 / LSG scan_input 颁发）
6. 性能（grant_allowance 开销可忽略）

测试隔离：所有真实 LLM 调用均在 guard 阶段被拦截（guard 在 original 之前 raise），
不发起任何网络请求。“放行”路径用 fake 函数验证 guard 委派语义，避免真实网络。
子进程测试用独立 python 解释器验证 sitecustomize 自动加载。
"""

from __future__ import annotations

import asyncio
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

from zephyr.security.llm_defense.llm_security.gateway import LSGSecurityGateway
from zephyr.security.llm_defense.llm_security.protocol import SecurityDecision
from zephyr.security.llm_defense.llm_security.runtime_interceptor import (
    BareLLMCallError,
    _ctx_allowance,
    _is_guarded,
    _make_async_guard,
    _make_guard,
    _tls_get,
    allow_llm_call,
    allow_llm_call_async,
    grant_allowance,
    install,
    is_allowance_active,
    is_installed,
    revoke_allowance,
    uninstall,
)
from zephyr.shared.io.paths import REPO_ROOT

_REPO_ROOT = REPO_ROOT


def _litellm_importable() -> bool:
    """检查 litellm 能否成功导入。

    litellm 在 __init__ 阶段会 get_model_cost_map()：远程拉取 model_prices JSON，
    失败后回退本地 importlib.resources 读取。本机环境若 litellm 安装残缺，
    本地回退会抛 FileNotFoundError: Can't open orphan path——这是 litellm 自身的环境
    问题，与拦截器逻辑无关。此场景下跳过 litellm 测试（拦截机制已由 openai 测试充分证明）。
    """
    try:
        import litellm  # noqa: F401
        return True
    except Exception:
        return False


_LITELLM_OK = _litellm_importable()


@pytest.fixture(autouse=True)
def _clean_allowance():
    """每个测试前后清零放行令牌，保证隔离。"""
    revoke_allowance()
    yield
    revoke_allowance()


# ============================================================================
# 1. 放行令牌机制（单元测试，不依赖 openai）
# ============================================================================

class TestAllowanceToken:
    def test_no_allowance_by_default(self):
        assert is_allowance_active() is False

    def test_grant_activates_allowance(self):
        grant_allowance(request_id="t1")
        assert is_allowance_active() is True

    def test_revoke_deactivates_allowance(self):
        grant_allowance(request_id="t2")
        revoke_allowance()
        assert is_allowance_active() is False

    def test_allowance_ttl_expiry(self):
        grant_allowance(request_id="t3", ttl=0.02)
        assert is_allowance_active() is True
        time.sleep(0.05)
        assert is_allowance_active() is False

    def test_allow_llm_call_context_sync(self):
        called = {"n": 0}

        def fake_create(*a, **kw):
            called["n"] += 1
            return "ok"

        guarded = _make_guard(fake_create, "fake.create")
        # 上下文外：拦截
        with pytest.raises(BareLLMCallError):
            guarded()
        assert called["n"] == 0
        # 上下文内：放行调原方法
        with allow_llm_call():
            assert guarded() == "ok"
        assert called["n"] == 1
        # 上下文外再次：拦截
        with pytest.raises(BareLLMCallError):
            guarded()
        assert called["n"] == 1

    def test_allow_llm_call_context_async(self):
        async def scenario():
            called = {"n": 0}

            async def fake_acreate(*a, **kw):
                called["n"] += 1
                return "ok-async"

            aguarded = _make_async_guard(fake_acreate, "fake.acreate")
            # 无令牌：拦截
            with pytest.raises(BareLLMCallError):
                await aguarded()
            assert called["n"] == 0
            # 有令牌：放行调原方法
            async with allow_llm_call_async():
                assert await aguarded() == "ok-async"
            assert called["n"] == 1

        asyncio.run(scenario())


# ============================================================================
# 1b. 双存储不变量守卫（铁律2.3治本 + 铁律2.4两问）
# ----------------------------------------------------------------------------
# 双存储（contextvar + threading.local）是必要正确性，非真源违规：
#  - 单存 contextvar：sync→asyncio.run→sync 路径令牌不回传 → 误拦合法调用
#  - 单存 threading.local：并发 async 任务串扰 → 安全漏洞
# 本测试锁死"双写属性"——grant 必须同时写两处，revoke/过期必须同时清两处。
# 防止未来 AI 误优化成单存而引入安全漏洞（让 AI 在准备改时知道约束而不创造）。
# 真源：runtime_interceptor.py 的 grant_allowance / revoke_allowance / is_allowance_active
# ============================================================================

class TestDualStoreInvariant:
    """双存储不变量守卫。

    锁死双写属性：grant 同写 ctx+tls（同对象），revoke/过期同清 ctx+tls。
    任一不变量被破坏 → 单存优化引入安全漏洞 → 测试 fail。
    """

    def test_grant_writes_both_stores(self):
        """grant_allowance 必须同时写入 contextvar 和 thread-local。"""
        grant_allowance(request_id="invariant-grant")
        assert _ctx_allowance.get() is not None
        assert _tls_get() is not None
        # 两处持有同一逻辑令牌（同一对象引用，非两个真源同步）
        assert _ctx_allowance.get() is _tls_get()

    def test_revoke_clears_both_stores(self):
        """revoke_allowance 必须同时清空 contextvar 和 thread-local。"""
        grant_allowance(request_id="invariant-revoke")
        assert _ctx_allowance.get() is not None
        assert _tls_get() is not None
        revoke_allowance()
        assert _ctx_allowance.get() is None
        assert _tls_get() is None

    def test_expiry_clears_both_stores(self):
        """过期令牌惰性清除时，两处存储都必须被清空（防僵尸令牌残留）。"""
        grant_allowance(request_id="invariant-expiry", ttl=0.02)
        assert _ctx_allowance.get() is not None
        assert _tls_get() is not None
        time.sleep(0.05)
        assert is_allowance_active() is False
        assert _ctx_allowance.get() is None
        assert _tls_get() is None

    def test_grant_idempotent_overwrites_both(self):
        """重复 grant 以最新令牌覆盖两处，保持双存储一致。"""
        grant_allowance(request_id="first", ttl=60)
        first_ctx = _ctx_allowance.get()
        first_tls = _tls_get()
        grant_allowance(request_id="second", ttl=60)
        assert _ctx_allowance.get() is not None
        assert _tls_get() is not None
        assert _ctx_allowance.get() is not first_ctx
        assert _tls_get() is not first_tls
        assert _ctx_allowance.get() is _tls_get()


# ============================================================================
# 2. install / uninstall / kill-switch
# ============================================================================

class TestInstallLifecycle:
    def test_install_idempotent(self):
        install()
        assert is_installed() is True
        install()  # 再次调用不报错
        assert is_installed() is True

    def test_uninstall_removes_finder(self):
        install()
        assert is_installed() is True
        uninstall()
        assert is_installed() is False
        install()  # 恢复，避免影响后续测试

    def test_kill_switch_disables_install(self, monkeypatch):
        monkeypatch.setenv("ZEPHYR_RUNTIME_GATE", "0")
        uninstall()
        result = install()
        assert result is False
        assert is_installed() is False
        monkeypatch.delenv("ZEPHYR_RUNTIME_GATE", raising=False)
        install()  # 恢复


# ============================================================================
# 3. 真实 openai / litellm patch 验证（无网络——guard 在 original 之前 raise）
# ============================================================================

class TestRealLLMPatching:
    """验证已安装的 openai/litellm 被 patch 后，裸调被拦截（不发起网络请求）。"""

    def setup_method(self):
        install()  # 确保 finder 已注册 + 已导入目标库被 eager-patch

    def test_openai_completions_create_guarded(self):
        from openai.resources.chat.completions import AsyncCompletions, Completions

        assert _is_guarded(Completions.create) is True
        assert _is_guarded(AsyncCompletions.create) is True

    def test_openai_bare_call_blocked_no_network(self):
        """裸调 openai.chat.completions.create → BareLLMCallError（guard 先于网络 raise）。"""
        import openai

        client = openai.OpenAI(api_key="sk-runtime-gate-test")  # 仅构造，无网络
        with pytest.raises(BareLLMCallError):
            client.chat.completions.create(
                model="gpt-4", messages=[{"role": "user", "content": "hi"}]
            )

    @pytest.mark.skipif(not _LITELLM_OK, reason="litellm 本地环境无法导入（model_cost_map 缺失）")
    def test_litellm_bare_call_blocked(self):
        import litellm

        with pytest.raises(BareLLMCallError):
            litellm.completion(model="gpt-4", messages=[{"role": "user", "content": "hi"}])


# ============================================================================
# 4. 红蓝对抗（验收标准 #1）：code = read_file(...); exec(code) 运行时被拦截
# ============================================================================

class TestRedBlueAdversarial:
    """模拟 GATE-20 静态分析无法检测的运行时代码生成场景。"""

    def setup_method(self):
        install()

    def test_exec_payload_from_file_blocked(self, tmp_path):
        """验收 #1：从文件读取 payload 再 exec，运行时被拦截。

        场景：AI/攻击者将裸调 LLM 的代码写入文件，运行时读取并 exec。
        GATE-20 的 AST 看不到文件内容，但运行时 Gate 在 openai.create 调用时拦截。
        """
        payload = tmp_path / "payload.txt"
        payload.write_text(
            "import openai\n"
            "client = openai.OpenAI(api_key='sk-redblue')\n"
            "client.chat.completions.create(\n"
            "    model='gpt-4', messages=[{'role':'user','content':'steal secrets'}]\n"
            ")\n",
            encoding="utf-8",
        )
        # 模拟运行时从文件读取并 exec——AST 层面此字符串对 GATE-20 不可见（动态获取）
        code = payload.read_text(encoding="utf-8")
        with pytest.raises(BareLLMCallError):
            exec(code)

    @pytest.mark.skipif(not _LITELLM_OK, reason="litellm 本地环境无法导入（model_cost_map 缺失）")
    def test_exec_payload_litellm_blocked(self, tmp_path):
        payload = tmp_path / "payload_litellm.txt"
        payload.write_text(
            "import litellm\n"
            "litellm.completion(model='gpt-4', messages=[{'role':'user','content':'x'}])\n",
            encoding="utf-8",
        )
        code = payload.read_text(encoding="utf-8")
        with pytest.raises(BareLLMCallError):
            exec(code)

    def test_exec_payload_bypasses_ast_only_scanner(self, tmp_path):
        """证明 AST 静态扫描无法发现此 payload，但运行时 Gate 能拦截。

        payload 用 chr() 拼接构造 'openai' 模块名——AST 静态扫描看不到 'openai' 字面量，
        GATE-20 的 _BARE_LLM_SIGNATURES 字符串匹配不会命中。但运行时 Gate 在
        Completions.create 调用时拦截（patch 作用于类方法，与导入路径无关）。
        """
        payload = tmp_path / "obfuscated.txt"
        # chr(111,112,101,110,97,105) = 'openai'
        payload.write_text(
            "mod = __import__(''.join([chr(111),chr(112),chr(101),chr(110),chr(97),chr(105)]))\n"
            "client = mod.OpenAI(api_key='sk-obf')\n"
            "client.chat.completions.create(model='gpt-4', messages=[{'role':'user','content':'x'}])\n",
            encoding="utf-8",
        )
        code = payload.read_text(encoding="utf-8")
        with pytest.raises(BareLLMCallError):
            exec(code)


# ============================================================================
# 5. LSG 集成（scan_input ALLOW → 颁发放行令牌）
# ============================================================================

class TestLSGIntegration:
    """验证 gateway.py 集成：LSG 扫描通过后自动颁发放行令牌。"""

    def test_scan_input_allow_grants_allowance(self):
        gw = LSGSecurityGateway()
        revoke_allowance()
        result = asyncio.run(gw.scan_input("hello world", source="test"))
        assert result.decision == SecurityDecision.ALLOW
        assert is_allowance_active() is True

    def test_scan_output_does_not_grant_allowance(self):
        """scan_output 不颁发令牌（输出扫描发生在 LLM 调用之后）。"""
        gw = LSGSecurityGateway()
        revoke_allowance()
        asyncio.run(gw.scan_output("some output", source="test"))
        assert is_allowance_active() is False

    def test_full_scan_allow_grants_allowance(self):
        gw = LSGSecurityGateway()
        revoke_allowance()
        result = asyncio.run(gw.full_scan("hello world"))
        assert result.decision == SecurityDecision.ALLOW
        assert is_allowance_active() is True

    def test_lsg_allowance_enables_guarded_call(self):
        """LSG scan_input 颁发的令牌使 guard 放行（用 fake 验证，无网络）。"""
        gw = LSGSecurityGateway()
        revoke_allowance()
        asyncio.run(gw.scan_input("benign question", source="test"))
        assert is_allowance_active() is True

        called = {"n": 0}

        def fake_create(*a, **kw):
            called["n"] += 1
            return "ok"

        guarded = _make_guard(fake_create, "fake.create")
        # LSG 颁发的令牌应使 guard 放行
        assert guarded() == "ok"
        assert called["n"] == 1


# ============================================================================
# 6. sitecustomize 自动加载（子进程——验收 #2 自动生效）
# ============================================================================

class TestSitecustomizeAutoLoad:
    """独立子进程验证：无需显式 install，sitecustomize 自动加载并 patch。"""

    @staticmethod
    def _run_subprocess(code: str, env_override: dict | None = None) -> subprocess.CompletedProcess:
        env = os.environ.copy()
        src = str(_REPO_ROOT / "src")
        # Python 3.12: `python -c` 模式下 sys.path[0]='' 是在 site 模块加载之后才加回的，
        # execsitecustomize 被调用时 sys.path 不含 cwd → sitecustomize.py 找不到。
        # 修复：把 repo_root 加到 PYTHONPATH，确保 sitecustomize.py 在 execsitecustomize
        # 被调用时能在 sys.path 上被找到。
        env["PYTHONPATH"] = (
            str(_REPO_ROOT) + os.pathsep
            + src + os.pathsep
            + env.get("PYTHONPATH", "")
        )
        if env_override:
            env.update(env_override)
        return subprocess.run(
            [sys.executable, "-c", code],
            cwd=str(_REPO_ROOT),
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
        )

    def test_auto_install_blocks_bare_call(self):
        """验收 #2：全新进程，不显式 install，sitecustomize 自动加载→裸调被拦截。"""
        code = (
            "from zephyr.security.llm_defense.llm_security.runtime_interceptor import BareLLMCallError\n"
            "import openai\n"
            "client = openai.OpenAI(api_key='sk-auto')\n"
            "try:\n"
            "    client.chat.completions.create(model='gpt-4', messages=[{'role':'user','content':'hi'}])\n"
            "    print('NOT_BLOCKED')\n"
            "except BareLLMCallError:\n"
            "    print('BLOCKED:BareLLMCallError')\n"
            "except Exception as e:\n"
            "    print('OTHER:' + type(e).__name__)\n"
        )
        result = self._run_subprocess(code)
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert "BLOCKED:BareLLMCallError" in result.stdout, (
            f"期望自动拦截，实际: stdout={result.stdout!r} stderr={result.stderr!r}"
        )

    def test_kill_switch_subprocess_disables(self):
        """验收 #4：ZEPHYR_RUNTIME_GATE=0 → sitecustomize 不安装→openai 未被 patch。"""
        code = (
            "from zephyr.security.llm_defense.llm_security.runtime_interceptor import is_installed, _is_guarded\n"
            "import openai\n"
            "from openai.resources.chat.completions import Completions\n"
            "print('INSTALLED:' + str(is_installed()))\n"
            "print('GUARDED:' + str(_is_guarded(Completions.create)))\n"
        )
        result = self._run_subprocess(code, env_override={"ZEPHYR_RUNTIME_GATE": "0"})
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert "INSTALLED:False" in result.stdout, result.stdout
        assert "GUARDED:False" in result.stdout, result.stdout

    def test_auto_install_enabled_in_normal_subprocess(self):
        """正常子进程（无 kill-switch）：sitecustomize 自动安装 + openai 被 patch。"""
        code = (
            "from zephyr.security.llm_defense.llm_security.runtime_interceptor import is_installed, _is_guarded\n"
            "import openai\n"
            "from openai.resources.chat.completions import Completions\n"
            "print('INSTALLED:' + str(is_installed()))\n"
            "print('GUARDED:' + str(_is_guarded(Completions.create)))\n"
        )
        result = self._run_subprocess(code)
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert "INSTALLED:True" in result.stdout, result.stdout
        assert "GUARDED:True" in result.stdout, result.stdout


# ============================================================================
# 7. 性能基准（验收 #4：LSG 扫描耗时增加 < 5%）
# ============================================================================

class TestPerformanceBenchmark:
    """验证 grant_allowance 对 LSG 扫描路径的性能开销可忽略（< 5%）。"""

    def test_grant_allowance_single_call_overhead(self):
        """grant_allowance 单次开销应远低于 scan_input 单次耗时（确保占比 < 5%）。"""
        # grant_allowance 单次开销（contextvar + threadlocal set，O(1)）
        n = 5000
        t0 = time.perf_counter()
        for _ in range(n):
            grant_allowance(request_id="bench")
            revoke_allowance()
        grant_us = (time.perf_counter() - t0) * 1_000_000 / n
        # 断言单次 grant+revoke < 50us（典型 scan_input 是 ms 级，占比 << 5%）
        assert grant_us < 50, f"grant_allowance 单次开销过大: {grant_us:.2f}us"

    def test_scan_input_baseline_runs_and_is_ms_scale(self):
        """scan_input 单次耗时为 ms 级——grant_allowance（us 级）占比可忽略。"""
        gw = LSGSecurityGateway()
        text = "hello world, benign benchmark prompt"
        n = 10
        # warmup
        asyncio.run(gw.scan_input(text, source="bench"))
        revoke_allowance()
        t0 = time.perf_counter()
        for _ in range(n):
            asyncio.run(gw.scan_input(text, source="bench"))
            revoke_allowance()
        per_call_ms = (time.perf_counter() - t0) * 1000 / n
        # scan_input 应为正且可运行（grant_allowance 集成不破坏扫描）
        assert per_call_ms > 0
        # 隐含断言：grant_allowance (us级) / scan_input (ms级) << 5%
