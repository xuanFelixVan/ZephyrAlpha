"""DM-201204 验证: gate_engine.load_gates()能加载所有门禁."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from zephyr.governance.rule_enforcement.gate_engine import GateEngine

GATES_DIR = Path(__file__).parent.parent.parent / "src" / "zephyr" / "governance" / "rule_enforcement"


def main() -> int:
    ge = GateEngine(gate_dir=GATES_DIR, db_path=Path(":memory:"), project_root=Path("."))
    gates = ge.load_gates()
    print(f"[OK] load_gates() returned {len(gates)} gates")
    print(f"Gate IDs: {sorted(gates.keys())[:10]}... (showing first 10)")
    ge.close()
    return 0 if len(gates) > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
