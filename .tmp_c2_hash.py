import hashlib, sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from pathlib import Path

REPO = Path(".")

pairs = [
    (
        "docs/01_FRAMEWORK/dynamic-risk-budgeting-blueprint.md",
        "docs/11_STRATEGIC_DECISION/risk-budgeting-framework-blueprint.md",
    ),
    (
        "docs/01_FRAMEWORK/LAYER4_ML/market-regime-blueprint.md",
        "docs/11_STRATEGIC_DECISION/market-environment-monitoring-blueprint.md",
    ),
    (
        "docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/portfolio-performance-evaluation-blueprint.md",
        "docs/11_STRATEGIC_DECISION/strategy-evaluation-engine-blueprint.md",
    ),
    (
        "docs/09_AUDIT/STATE/SENTINEL_L1_SCAN_20260408.md",
        "docs/09_AUDIT/STATE/SENTINEL_L2_SCAN_20260413.md",
    ),
]

def md5(p):
    return hashlib.md5((REPO / p).read_bytes()).hexdigest()

for a, b in pairs:
    ha, hb = md5(a), md5(b)
    identical = ha == hb
    sa = (REPO / a).stat().st_size
    sb = (REPO / b).stat().st_size
    tag = "IDENTICAL" if identical else "DIFFERENT"
    print(f"[{tag}]")
    print(f"  A: {a}  ({sa:,} B)  md5={ha[:8]}")
    print(f"  B: {b}  ({sb:,} B)  md5={hb[:8]}")
    print()
