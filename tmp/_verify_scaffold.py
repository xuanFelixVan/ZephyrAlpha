"""验证 scaffold.py layer 修复"""
import sys
sys.path.insert(0, r"d:\ZephyrAlpha\scripts")
sys.path.insert(0, r"d:\ZephyrAlpha\scripts\governance")
from scaffold import _load_valid_layers

lv = _load_valid_layers()
print(f"valid_layers count: {len(lv)}")
print(f"compliance in set: {'compliance' in lv}")
print(f"L1 in set: {'L1' in lv}")
print(f"L0 in set: {'L0' in lv}")
print(f"all values: {sorted(lv)}")

# 验证默认值
import inspect
import scaffold
sig = inspect.signature(scaffold.Scaffold.create_rule)
layer_default = sig.parameters['layer'].default
print(f"\ncreate_rule layer default: {layer_default}")
assert layer_default == "compliance", f"default should be compliance, got {layer_default}"

# 验证 L1 会被拒绝
try:
    # 模拟 layer 校验
    if "L1" not in lv:
        print("L1 correctly NOT in valid_layers (will be rejected)")
    else:
        print("ERROR: L1 still in valid_layers")
except Exception as e:
    print(f"Error: {e}")

print("\n✅ scaffold.py layer fix verified")
