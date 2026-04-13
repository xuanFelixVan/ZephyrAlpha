---
module_id: DOCUMENTATION_GENERATION_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - 文档自动生成
  - API文档生成
  - 代码文档生成
  - 文档发布
standard_type: 专业量化机构蓝图
compliance_level: 专业标准
layer: layer_05
---

# 文档生成蓝图

> **核心职责**: 提供自动化的文档生成能力，支持API文档、代码文档、用户文档的自动生成和发布
> **职责边界**: 
> - ✅ 本文档负责：文档自动生成、API文档生成、代码文档生成、文档发布
> - ❌ 本文档不负责：文档内容编写（由开发团队负责）、文档版本管理（由Git负责）

## 核心定位

负责文档生成模块的设计与构建，提供自动化的文档生成能力，支持API文档、代码文档、用户文档的自动生成和发布，确保文档与代码同步更新。

## 设计目标

### 主要目标

1. **API文档生成**: 自动生成RESTful API文档
2. **代码文档生成**: 自动生成代码注释文档
3. **用户文档生成**: 自动生成用户手册和教程
4. **文档发布**: 自动发布文档到Web站点

### 质量目标

- 文档生成自动化率: 100%
- API文档覆盖率: 100%
- 代码文档覆盖率: ≥ 80%
- 文档更新及时性: 实时

## 开源方案选型

### 推荐方案: Sphinx

| 属性 | 详情 |
|------|------|
| **GitHub** | https://github.com/sphinx-doc/sphinx |
| **Stars** | 6,000+ |
| **License** | BSD |
| **语言** | Python |
| **特点** | 强大的文档生成工具，支持多种格式 |

**选择理由**:
1. **功能强大**: 支持多种文档格式和输出格式
2. **生态完善**: 支持Python、C++、JavaScript等多种语言
3. **易于使用**: reStructuredText语法简单
4. **可扩展**: 支持丰富的插件和主题
5. **个人友好**: 免费开源，适合个人使用
6. **社区活跃**: 文档完善，社区支持好

## 核心功能设计

### 1. API文档生成模块

```python
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
import json
from typing import Dict, List

class APIDocGenerator:
    """API文档生成器"""
    
    def __init__(self, app: FastAPI):
        self.app = app
    
    def generate_openapi_spec(
        self,
        title: str = "ZephyrAlpha API",
        version: str = "1.0.0",
        description: str = "清风量化交易系统API文档"
    ) -> Dict:
        """生成OpenAPI规范"""
        return get_openapi(
            title=title,
            version=version,
            description=description,
            routes=self.app.routes
        )
    
    def save_openapi_spec(
        self,
        output_path: str = "docs/api/openapi.json"
    ):
        """保存OpenAPI规范"""
        spec = self.generate_openapi_spec()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(spec, f, indent=2, ensure_ascii=False)
    
    def generate_markdown_docs(
        self,
        output_dir: str = "docs/api/"
    ):
        """生成Markdown格式API文档"""
        spec = self.generate_openapi_spec()
        
        for path, methods in spec.get("paths", {}).items():
            for method, details in methods.items():
                doc_content = self._generate_endpoint_doc(
                    path,
                    method,
                    details
                )
                
                filename = f"{method}_{path.replace('/', '_')}.md"
                filepath = f"{output_dir}/{filename}"
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(doc_content)
    
    def _generate_endpoint_doc(
        self,
        path: str,
        method: str,
        details: Dict
    ) -> str:
        """生成端点文档"""
        doc = f"""# {method.upper()} {path}

## 描述
{details.get('summary', '无描述')}

## 请求参数

"""
        
        if 'parameters' in details:
            doc += "| 参数名 | 类型 | 必需 | 描述 |\n"
            doc += "|--------|------|------|------|\n"
            
            for param in details['parameters']:
                doc += f"| {param.get('name')} | {param.get('schema', {}).get('type', 'unknown')} | {'是' if param.get('required') else '否'} | {param.get('description', '')} |\n"
        
        if 'requestBody' in details:
            doc += "\n## 请求体\n\n"
            doc += f"```json\n{json.dumps(details['requestBody'], indent=2, ensure_ascii=False)}\n```\n"
        
        doc += "\n## 响应\n\n"
        
        for status_code, response in details.get('responses', {}).items():
            doc += f"### {status_code}\n\n"
            doc += f"{response.get('description', '')}\n\n"
            
            if 'content' in response:
                doc += "```json\n"
                doc += json.dumps(response['content'], indent=2, ensure_ascii=False)
                doc += "\n```\n"
        
        return doc
```

### 2. 代码文档生成模块

```python
import os
import ast
from typing import List, Dict

class CodeDocGenerator:
    """代码文档生成器"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
    
    def generate_python_docs(
        self,
        source_dir: str,
        output_dir: str = "docs/code/"
    ):
        """生成Python代码文档"""
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    
                    doc_content = self._generate_module_doc(filepath)
                    
                    relative_path = os.path.relpath(filepath, source_dir)
                    output_path = os.path.join(
                        output_dir,
                        relative_path.replace('.py', '.md')
                    )
                    
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(doc_content)
    
    def _generate_module_doc(self, filepath: str) -> str:
        """生成模块文档"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        doc = f"# {os.path.basename(filepath)}\n\n"
        
        module_doc = ast.get_docstring(tree)
        if module_doc:
            doc += f"## 模块描述\n\n{module_doc}\n\n"
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                doc += self._generate_function_doc(node)
            elif isinstance(node, ast.ClassDef):
                doc += self._generate_class_doc(node)
        
        return doc
    
    def _generate_function_doc(self, node: ast.FunctionDef) -> str:
        """生成函数文档"""
        doc = f"## {node.name}\n\n"
        
        func_doc = ast.get_docstring(node)
        if func_doc:
            doc += f"{func_doc}\n\n"
        
        doc += "**参数**:\n\n"
        
        for arg in node.args.args:
            doc += f"- `{arg.arg}`\n"
        
        doc += "\n"
        
        return doc
    
    def _generate_class_doc(self, node: ast.ClassDef) -> str:
        """生成类文档"""
        doc = f"## class {node.name}\n\n"
        
        class_doc = ast.get_docstring(node)
        if class_doc:
            doc += f"{class_doc}\n\n"
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                doc += self._generate_function_doc(item)
        
        return doc
```

### 3. Sphinx文档生成模块

```python
import subprocess
import os
from typing import List

class SphinxDocGenerator:
    """Sphinx文档生成器"""
    
    def __init__(self, docs_dir: str = "docs"):
        self.docs_dir = docs_dir
        self.source_dir = os.path.join(docs_dir, "source")
        self.build_dir = os.path.join(docs_dir, "build")
    
    def init_sphinx_project(self):
        """初始化Sphinx项目"""
        os.makedirs(self.source_dir, exist_ok=True)
        
        subprocess.run([
            "sphinx-quickstart",
            "-q",
            "-p", "ZephyrAlpha",
            "-a", "Zephyr Team",
            "-v", "1.0.0",
            "--sep",
            self.docs_dir
        ])
    
    def generate_html_docs(self):
        """生成HTML文档"""
        subprocess.run([
            "sphinx-build",
            "-b", "html",
            self.source_dir,
            os.path.join(self.build_dir, "html")
        ])
    
    def generate_pdf_docs(self):
        """生成PDF文档"""
        subprocess.run([
            "sphinx-build",
            "-b", "latex",
            self.source_dir,
            os.path.join(self.build_dir, "latex")
        ])
        
        subprocess.run([
            "make",
            "-C",
            os.path.join(self.build_dir, "latex"),
            "all-pdf"
        ])
    
    def update_conf_py(self, config: Dict):
        """更新Sphinx配置"""
        conf_path = os.path.join(self.source_dir, "conf.py")
        
        with open(conf_path, 'a', encoding='utf-8') as f:
            for key, value in config.items():
                if isinstance(value, str):
                    f.write(f"{key} = '{value}'\n")
                elif isinstance(value, list):
                    f.write(f"{key} = {value}\n")
                else:
                    f.write(f"{key} = {value}\n")
    
    def add_extensions(self, extensions: List[str]):
        """添加Sphinx扩展"""
        conf_path = os.path.join(self.source_dir, "conf.py")
        
        with open(conf_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        extensions_str = f"extensions = {extensions}\n"
        
        if "extensions = " in content:
            content = content.replace(
                "extensions = []",
                extensions_str
            )
        else:
            content += "\n" + extensions_str
        
        with open(conf_path, 'w', encoding='utf-8') as f:
            f.write(content)
```

### 4. 文档发布模块

```python
import subprocess
import os
from datetime import datetime

class DocPublisher:
    """文档发布器"""
    
    def __init__(self, build_dir: str = "docs/build/html"):
        self.build_dir = build_dir
    
    def publish_to_github_pages(
        self,
        repo_url: str,
        branch: str = "gh-pages"
    ):
        """发布到GitHub Pages"""
        temp_dir = "/tmp/docs_publish"
        
        subprocess.run([
            "git", "clone",
            "--branch", branch,
            repo_url,
            temp_dir
        ])
        
        subprocess.run(["rm", "-rf", f"{temp_dir}/*"])
        
        subprocess.run([
            "cp", "-r",
            f"{self.build_dir}/*",
            temp_dir
        ])
        
        subprocess.run(["git", "add", "."], cwd=temp_dir)
        subprocess.run(
            ["git", "commit", "-m", f"Update docs {datetime.now().isoformat()}"],
            cwd=temp_dir
        )
        subprocess.run(["git", "push"], cwd=temp_dir)
    
    def publish_to_s3(
        self,
        bucket_name: str,
        aws_region: str = "us-east-1"
    ):
        """发布到S3"""
        subprocess.run([
            "aws", "s3", "sync",
            self.build_dir,
            f"s3://{bucket_name}",
            "--region", aws_region
        ])
    
    def publish_to_netlify(
        self,
        site_id: str,
        auth_token: str
    ):
        """发布到Netlify"""
        subprocess.run([
            "netlify", "deploy",
            "--dir", self.build_dir,
            "--site", site_id,
            "--auth", auth_token,
            "--prod"
        ])
```

## 技术实现

### 1. Sphinx配置文件

```python
project = 'ZephyrAlpha'
copyright = '2026, Zephyr Team'
author = 'Zephyr Team'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx_rtd_theme',
    'myst_parser',
]

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
}
```

### 2. 文档生成流水线

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'zephyr',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'documentation_generation',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False
)

def generate_api_docs():
    from fastapi import FastAPI
    app = FastAPI()
    
    generator = APIDocGenerator(app)
    generator.save_openapi_spec()
    generator.generate_markdown_docs()

def generate_code_docs():
    generator = CodeDocGenerator("/path/to/project")
    generator.generate_python_docs("src/")

def generate_sphinx_docs():
    generator = SphinxDocGenerator("docs")
    generator.generate_html_docs()

def publish_docs():
    publisher = DocPublisher()
    publisher.publish_to_github_pages("https://github.com/user/repo.git")

generate_api_task = PythonOperator(
    task_id='generate_api_docs',
    python_callable=generate_api_docs,
    dag=dag
)

generate_code_task = PythonOperator(
    task_id='generate_code_docs',
    python_callable=generate_code_docs,
    dag=dag
)

generate_sphinx_task = PythonOperator(
    task_id='generate_sphinx_docs',
    python_callable=generate_sphinx_docs,
    dag=dag
)

publish_task = PythonOperator(
    task_id='publish_docs',
    python_callable=publish_docs,
    dag=dag
)

generate_api_task >> generate_sphinx_task
generate_code_task >> generate_sphinx_task
generate_sphinx_task >> publish_task
```

## 实施路径

### Phase 1: 核心功能（Week 1）

**目标**: 实现基础文档生成

**任务清单**:
- [ ] 安装和配置Sphinx
- [ ] 实现API文档生成
- [ ] 实现代码文档生成
- [ ] 配置文档主题
- [ ] 编写单元测试

**交付物**:
- Sphinx配置
- APIDocGenerator类
- CodeDocGenerator类
- 单元测试覆盖率≥80%

### Phase 2: 高级功能（Week 2）

**目标**: 实现文档发布和自动化

**任务清单**:
- [ ] 实现文档发布
- [ ] 集成到CI/CD
- [ ] 实现文档搜索
- [ ] 配置文档版本管理
- [ ] 编写集成测试

**交付物**:
- DocPublisher类
- CI/CD集成配置
- 文档搜索功能
- 集成测试覆盖率≥70%

```
```---
```

**文档版本**: v1.0.0
**创建日期**: 2026-04-07
**最后更新**: 2026-04-07
**状态**: Active

## 接口与契约（蓝图终稿）

- **契约真源**：`API_Contract.md`
- **对外接口边界**：本模块提供文档生成、发布与索引更新的接口与流程约束；不替代各业务模块蓝图的权威内容，不直接定义业务 API 细节。

## 验收标准（可检查）

- 能够对至少 1 个目标目录/模块运行文档生成流程并产出可浏览文档产物，且生成过程与输入（版本、源文件集合）可追溯记录。

## 已知限制

- 文档生成质量依赖上游源文档一致性与模板；实施阶段需在契约真源中固化模板版本、失败回滚策略与增量生成规则。
