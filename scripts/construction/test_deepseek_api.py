# [BLUEPRINT]
# [MODULE] scripts.construction.test_deepseek_api
# [DOMAIN]
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""测试 DeepSeek API 连通性 — 验证 deepseek-v4-flash 和 deepseek-v4-pro 可用"""
import os
import sys
import time
import json
from pathlib import Path

# bootstrap: 定位 scripts/governance/ 以 import _shared.constants（REPO_ROOT SSoT 真源）
_GOV_DIR = str(Path(__file__).resolve().parents[1] / "governance")
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import REPO_ROOT  # noqa: E402

# 加载 .env
env_path = REPO_ROOT / ".env"
if env_path.exists():
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

api_key = os.getenv("DEEPSEEK_API_KEY", "")
base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")

print(f"API Key: {api_key[:8]}...{api_key[-4:]}")
print(f"Base URL: {base_url}")
print()

try:
    import requests
except ImportError:
    print("ERROR: requests package not installed — pip install requests")
    sys.exit(1)

models_to_test = ["deepseek-v4-flash", "deepseek-v4-pro"]

for model in models_to_test:
    print(f"--- Testing {model} ---")
    start = time.monotonic()
    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant. Reply in Chinese."},
                    {"role": "user", "content": "说一句话证明你能工作"},
                ],
                "temperature": 0.3,
                "max_tokens": 100,
            },
            timeout=30,
        )
        latency = int((time.monotonic() - start) * 1000)

        if response.status_code == 200:
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            usage = data.get("usage", {})
            tokens_in = usage.get("prompt_tokens", 0)
            tokens_out = usage.get("completion_tokens", 0)
            print(f"  Status: OK")
            print(f"  Latency: {latency}ms")
            print(f"  Tokens: in={tokens_in} out={tokens_out}")
            print(f"  Response: {content[:100]}")
        else:
            print(f"  Status: HTTP {response.status_code} ({latency}ms)")
            print(f"  Error: {response.text[:200]}")
    except Exception as e:
        latency = int((time.monotonic() - start) * 1000)
        print(f"  Status: FAIL ({latency}ms)")
        print(f"  Error: {type(e).__name__}: {e}")
    print()

print("Done.")
