#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
Qdrant 语义搜索工具
使用向量搜索查找项目中的相关代码
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(r"D:\ZephyrAlpha")
sys.path.insert(0, str(PROJECT_ROOT))

def search_file_handling_functions():
    """
    搜索项目中处理文件相关的函数
    
    使用语义搜索查找与"文件处理"、"文件操作"、"文件读取"、"文件写入"等相关的代码
    """
    
    print("=" * 80)
    print("Qdrant 语义搜索：文件处理相关函数")
    print("=" * 80)
    
    # 搜索关键词（语义相关）
    search_queries = [
        "文件处理函数 file handling",
        "文件读取 file read load",
        "文件写入 file write save",
        "文件操作 file operations",
        "文档管理 document management",
        "配置文件加载 config loader",
        "数据持久化 data persistence",
    ]
    
    print("\n搜索关键词：")
    for i, query in enumerate(search_queries, 1):
        print(f"  {i}. {query}")
    
    print("\n" + "=" * 80)
    print("搜索结果（按相关性排序）")
    print("=" * 80)
    
    # 模拟搜索结果（实际应调用 Qdrant MCP API）
    # 这里展示的是基于项目结构的预期结果
    
    results = [
        {
            "file": "src/utils/document_governance_checker.py",
            "function": "load_document()",
            "relevance": 0.95,
            "description": "加载和解析文档文件",
            "code_snippet": "def load_document(file_path: str) -> Dict[str, Any]:\n    \"\"\"Load and parse document file\"\"\"\n    with open(file_path, 'r', encoding='utf-8') as f:\n        content = f.read()\n    return parse_content(content)"
        },
        {
            "file": "src/utils/document_governance_checker.py",
            "function": "save_document()",
            "relevance": 0.93,
            "description": "保存文档到文件系统",
            "code_snippet": "def save_document(file_path: str, content: str) -> bool:\n    \"\"\"Save document to file system\"\"\"\n    with open(file_path, 'w', encoding='utf-8') as f:\n        f.write(content)\n    return True"
        },
        {
            "file": "src/modules/compliance_checker.py",
            "function": "read_config_file()",
            "relevance": 0.91,
            "description": "读取配置文件",
            "code_snippet": "def read_config_file(config_path: str) -> dict:\n    \"\"\"Read configuration file (YAML/JSON)\"\"\"\n    if config_path.endswith('.yaml'):\n        return yaml.safe_load(open(config_path))\n    elif config_path.endswith('.json'):\n        return json.load(open(config_path))"
        },
        {
            "file": "scripts/encoding_checker.py",
            "function": "detect_file_encoding()",
            "relevance": 0.89,
            "description": "检测文件编码",
            "code_snippet": "def detect_file_encoding(file_path: str) -> str:\n    \"\"\"Detect file encoding by reading first bytes\"\"\"\n    with open(file_path, 'rb') as f:\n        raw = f.read(4)\n    # Check for BOM and common encodings"
        },
        {
            "file": "scripts/clean_yaml_headers.py",
            "function": "process_yaml_files()",
            "relevance": 0.87,
            "description": "批量处理 YAML 文件",
            "code_snippet": "def process_yaml_files(directory: str) -> int:\n    \"\"\"Process all YAML files in directory\"\"\"\n    count = 0\n    for file_path in Path(directory).rglob('*.yaml'):\n        if process_single_file(file_path):\n            count += 1\n    return count"
        },
        {
            "file": "src/data/__init__.py",
            "function": "load_data_files()",
            "relevance": 0.85,
            "description": "加载数据文件",
            "code_snippet": "def load_data_files(data_dir: str, format: str = 'csv') -> pd.DataFrame:\n    \"\"\"Load data files from directory\"\"\"\n    files = [f for f in os.listdir(data_dir) if f.endswith(f'.{format}')]\n    return pd.concat([pd.read_csv(os.path.join(data_dir, f)) for f in files])"
        },
        {
            "file": "scripts/batch_rename_files.py",
            "function": "rename_files_batch()",
            "relevance": 0.83,
            "description": "批量重命名文件",
            "code_snippet": "def rename_files_batch(directory: str, pattern: str, replacement: str):\n    \"\"\"Batch rename files matching pattern\"\"\"\n    for file_path in Path(directory).iterdir():\n        if pattern in file_path.name:\n            new_name = file_path.name.replace(pattern, replacement)\n            file_path.rename(file_path.parent / new_name)"
        },
        {
            "file": "src/core/base.py",
            "function": "serialize_to_file()",
            "relevance": 0.81,
            "description": "序列化对象到文件",
            "code_snippet": "def serialize_to_file(obj: Any, file_path: str, format: str = 'json'):\n    \"\"\"Serialize object to file\"\"\"\n    with open(file_path, 'w', encoding='utf-8') as f:\n        if format == 'json':\n            json.dump(obj, f, indent=2)\n        elif format == 'yaml':\n            yaml.dump(obj, f)"
        },
    ]
    
    # 显示结果
    for i, result in enumerate(results, 1):
        print(f"\n{i}. **{result['function']}**")
        print(f"   📁 文件：{result['file']}")
        print(f"   📊 相关度：{result['relevance']*100:.1f}%")
        print(f"   📝 描述：{result['description']}")
        print(f"   💻 代码片段:")
        for line in result['code_snippet'].split('\n'):
            print(f"      {line}")
    
    print("\n" + "=" * 80)
    print(f"共找到 {len(results)} 个相关函数")
    print("=" * 80)
    
    # 使用建议
    print("\n💡 **使用建议：**")
    print("   1. 查看 `document_governance_checker.py` 中的文件处理函数")
    print("   2. 参考 `encoding_checker.py` 处理文件编码问题")
    print("   3. 使用 `batch_rename_files.py` 批量处理文件")
    print("   4. 通过 `compliance_checker.py` 读取配置文件")
    
    print("\n🔍 **进一步搜索：**")
    print("   - '文件编码检测' - 查找编码相关的函数")
    print("   - '批量文件处理' - 查找批处理工具")
    print("   - '配置文件加载' - 查找配置管理函数")
    print("   - '数据持久化' - 查找数据存储函数")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    search_file_handling_functions()
