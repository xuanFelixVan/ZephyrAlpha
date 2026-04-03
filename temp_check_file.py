import codecs

file_path = r'D:\ZephyrAlpha\docs\01_FRAMEWORK\HUMAN_AI_INTERACTION_BLUEPRINT.md'

with codecs.open(file_path, 'r', encoding='utf-16-le') as f:
    content = f.read()

print("First 500 characters:")
print(content[:500])
print("\n" + "="*50 + "\n")
print("Last 500 characters:")
print(content[-500:])
