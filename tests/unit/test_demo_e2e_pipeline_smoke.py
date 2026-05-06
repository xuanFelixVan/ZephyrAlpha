"""demo_e2e_pipeline.py 语法自检（不执行全链路——需网络与 akshare）。"""

from __future__ import annotations

from pathlib import Path


def test_demo_e2e_pipeline_compiles() -> None:
    root = Path(__file__).resolve().parents[2]
    script = root / "demo_e2e_pipeline.py"
    src = script.read_text(encoding="utf-8")
    compile(src, str(script), "exec", dont_inherit=True)
