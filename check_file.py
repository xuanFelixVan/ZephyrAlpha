file_path = r'D:\ZephyrAlpha\docs\01_FRAMEWORK\HUMAN_AI_INTERACTION_BLUEPRINT.md'

with open(file_path, 'rb') as f:
    raw_bytes = f.read()

print(f"File size: {len(raw_bytes)} bytes")
print(f"First 20 bytes: {raw_bytes[:20]}")
print(f"BOM check: {raw_bytes[:2]}")

if raw_bytes.startswith(b'\xff\xfe'):
    print("File has UTF-16-LE BOM")
elif raw_bytes.startswith(b'\xfe\xff'):
    print("File has UTF-16-BE BOM")
else:
    print("File has no BOM or UTF-8")

try:
    content = raw_bytes.decode('utf-8')
    print(f"UTF-8 decode successful, length: {len(content)}")
    print(f"First 100 chars: {content[:100]}")
except Exception as e:
    print(f"UTF-8 decode failed: {e}")
