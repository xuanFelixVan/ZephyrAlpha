---

module_id: API_DOCUMENTATION_001

version: 1.0.0

status: Active

created_date: 2026-04-07

last_updated: 2026-04-07

owner: 首席文档架构师

responsibility:

  - API文档生成

  - API规范定义

  - API测试

  - API版本管理

standard_type: 专业量化机构蓝图

compliance_level: 专业标准

layer: layer_05

---



# API文档蓝图



> **核心职责**: 提供自动化的API文档生成和管理，确保API文档与代码同步

> **职责边界**: 

> - ✅ 本文档负责：API文档生成、API规范定义、API测试、API版本管理

> - ❌ 本文档不负责：API开发（由API开发团队负责）、API安全（由安全模块负责）



## 核心定位



负责API文档模块的设计与构建，实现自动化API文档生成、API规范定义、API测试，确保API文档与代码同步更新。



## 接口与契约（蓝图终稿）



- 全库 API 与事件约定真源：`API_Contract.md`。本模块对外输出的文档/规范（OpenAPI/Schema/示例）与文档发布事件口径以该真源为准；本蓝图不替代业务接口本身的契约真源。



## 验收标准（可检查）



- 能从至少 1 个服务的代码/注解生成 OpenAPI 文档，并在指定地址访问（例如 `/docs` 或导出文件）。

- 文档与接口版本可追溯：文档产物包含版本号/生成时间/commit 信息（或等价可追溯字段）。

- 对外产物（OpenAPI/Schema）能在 `API_Contract.md` 中定位到契约入口（或在“已知限制”列出未闭合项）。



## 已知限制



- 自动化生成质量依赖代码注解完整度；落地阶段需固化规范约束（lint/门禁）并回填契约真源与模板。



## 设计目标



### 主要目标



1. **自动化文档生成**: 从代码自动生成API文档

2. **交互式文档**: 提供可交互的API文档界面

3. **API测试**: 支持在文档中直接测试API

4. **版本管理**: 管理API版本和变更历史



### 质量目标



- 文档覆盖率: 100%

- 文档准确性: 100%

- 文档可交互性: 100%

- 文档更新及时性: 100%



## 开源方案选型



### 推荐方案: FastAPI + Swagger/OpenAPI



| 属性 | 详情 |

|------|------|

| **FastAPI** | https://github.com/tiangolo/fastapi |

| **Swagger UI** | https://github.com/swagger-api/swagger-ui |

| **Stars** | 70k+ / 25k+ |

| **License** | MIT |

| **特点** | 自动生成OpenAPI文档 |



**选择理由**:

1. **自动生成**: FastAPI自动生成OpenAPI规范

2. **交互式文档**: Swagger UI提供交互式界面

3. **类型安全**: 基于Python类型注解

4. **个人友好**: 简单易用，适合个人开发者

5. **高性能**: 基于Starlette和Pydantic



### 备选方案



| 项目 | Stars | 特点 | 推荐度 |

|------|-------|------|--------|

| **Flask-RESTful** | 6k+ | Flask扩展 | ⭐⭐⭐⭐ |

| **Django REST** | 27k+ | Django框架 | ⭐⭐⭐⭐ |

| **ReDoc** | 22k+ | API文档渲染 | ⭐⭐⭐⭐⭐ |



## 核心功能设计



### 1. FastAPI应用配置



```python

from fastapi import FastAPI, HTTPException, Depends, Query, Path, Body

from fastapi.openapi.utils import get_openapi

from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel, Field

from typing import List, Optional, Dict, Any

from datetime import datetime

import uvicorn



app = FastAPI(

    title="清风量化交易系统 API",

    description="专业的量化交易系统API文档",

    version="5.2.0",

    docs_url="/docs",

    redoc_url="/redoc",

    openapi_url="/openapi.json"

)



app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],

)





class FactorRequest(BaseModel):

    """因子计算请求"""

    start_date: str = Field(..., description="开始日期", example="2023-01-01")

    end_date: str = Field(..., description="结束日期", example="2023-12-31")

    factors: List[str] = Field(

        ...,

        description="因子列表",

        example=["momentum", "volatility", "value"]

    )

    

    class Config:

        schema_extra = {

            "example": {

                "start_date": "2023-01-01",

                "end_date": "2023-12-31",

                "factors": ["momentum", "volatility", "value"]

            }

        }





class FactorResponse(BaseModel):

    """因子计算响应"""

    task_id: str = Field(..., description="任务ID")

    status: str = Field(..., description="任务状态")

    created_at: datetime = Field(..., description="创建时间")

    

    class Config:

        schema_extra = {

            "example": {

                "task_id": "task_12345",

                "status": "pending",

                "created_at": "2023-01-01T00:00:00"

            }

        }





class HealthResponse(BaseModel):

    """健康检查响应"""

    status: str = Field(..., description="服务状态")

    version: str = Field(..., description="API版本")

    timestamp: datetime = Field(..., description="时间戳")





@app.get(

    "/health",

    response_model=HealthResponse,

    tags=["系统"],

    summary="健康检查",

    description="检查API服务是否正常运行"

)

async def health_check():

    """健康检查端点"""

    return {

        "status": "healthy",

        "version": "5.2.0",

        "timestamp": datetime.now()

    }





@app.post(

    "/api/v1/factors/calculate",

    response_model=FactorResponse,

    tags=["因子计算"],

    summary="计算因子",

    description="异步计算指定日期范围内的因子",

    responses={

        200: {

            "description": "任务创建成功",

            "content": {

                "application/json": {

                    "example": {

                        "task_id": "task_12345",

                        "status": "pending",

                        "created_at": "2023-01-01T00:00:00"

                    }

                }

            }

        },

        400: {"description": "请求参数错误"},

        500: {"description": "服务器内部错误"}

    }

)

async def calculate_factors(request: FactorRequest):

    """计算因子"""

    task_id = f"task_{datetime.now().timestamp()}"

    

    return {

        "task_id": task_id,

        "status": "pending",

        "created_at": datetime.now()

    }





@app.get(

    "/api/v1/tasks/{task_id}",

    tags=["任务管理"],

    summary="查询任务状态",

    description="根据任务ID查询任务执行状态",

    responses={

        200: {

            "description": "任务状态",

            "content": {

                "application/json": {

                    "example": {

                        "task_id": "task_12345",

                        "status": "completed",

                        "progress": 100,

                        "result": {"factors_count": 10}

                    }

                }

            }

        },

        404: {"description": "任务不存在"}

    }

)

async def get_task_status(

    task_id: str = Path(..., description="任务ID", example="task_12345")

):

    """查询任务状态"""

    return {

        "task_id": task_id,

        "status": "completed",

        "progress": 100,

        "result": {"factors_count": 10}

    }





@app.get(

    "/api/v1/factors",

    tags=["因子数据"],

    summary="获取因子数据",

    description="获取指定日期范围内的因子数据",

    responses={

        200: {

            "description": "因子数据",

            "content": {

                "application/json": {

                    "example": {

                        "factors": [

                            {

                                "date": "2023-01-01",

                                "momentum": 0.05,

                                "volatility": 0.15,

                                "value": 0.08

                            }

                        ],

                        "total": 100

                    }

                }

            }

        }

    }

)

async def get_factors(

    start_date: str = Query(..., description="开始日期", example="2023-01-01"),

    end_date: str = Query(..., description="结束日期", example="2023-12-31"),

    factors: Optional[List[str]] = Query(

        None,

        description="因子列表",

        example=["momentum", "volatility"]

    ),

    limit: int = Query(100, ge=1, le=1000, description="返回数量限制")

):

    """获取因子数据"""

    return {

        "factors": [

            {

                "date": "2023-01-01",

                "momentum": 0.05,

                "volatility": 0.15,

                "value": 0.08

            }

        ],

        "total": 100

    }





def custom_openapi():

    """自定义OpenAPI规范"""

    if app.openapi_schema:

        return app.openapi_schema

    

    openapi_schema = get_openapi(

        title="清风量化交易系统 API",

        version="5.2.0",

        description="""

## 概述



清风量化交易系统API提供完整的量化交易功能，包括：



- **因子计算**: 计算各类量化因子

- **策略回测**: 策略历史回测

- **组合优化**: 投资组合优化

- **风险管理**: 风险监控和管理



## 认证



API使用Bearer Token认证，请在请求头中添加：

```

Authorization: Bearer <your_token>

```



## 限流



- 普通用户: 100次/分钟

- VIP用户: 1000次/分钟



## 错误处理



所有错误响应遵循统一格式：

```json

{

  "error": {

    "code": "ERROR_CODE",

    "message": "错误描述",

    "details": {}

  }

}

```

        """,

        routes=app.routes,

    )

    

    openapi_schema["info"]["x-logo"] = {

        "url": "https://example.com/logo.png"

    }

    

    app.openapi_schema = openapi_schema

    return app.openapi_schema





app.openapi = custom_openapi





if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8000)

```



### 2. API文档生成工具



```python

import json

from pathlib import Path

from typing import Dict, Any, List

import yaml



class APIDocGenerator:

    """API文档生成器"""

    

    def __init__(self, openapi_spec: Dict[str, Any]):

        self.spec = openapi_spec

    

    def generate_markdown_doc(self, output_path: str):

        """生成Markdown文档"""

        doc = []

        

        doc.append(f"# {self.spec['info']['title']}\n")

        doc.append(f"版本: {self.spec['info']['version']}\n")

        doc.append(f"\n{self.spec['info'].get('description', '')}\n")

        

        doc.append("\n## API端点\n")

        

        for path, methods in self.spec['paths'].items():

            for method, details in methods.items():

                if method in ['get', 'post', 'put', 'delete']:

                    doc.append(f"\n### {method.upper()} {path}\n")

                    doc.append(f"**描述**: {details.get('summary', 'N/A')}\n")

                    doc.append(f"**详细**: {details.get('description', 'N/A')}\n")

        

        output_file = Path(output_path)

        output_file.write_text('\n'.join(doc), encoding='utf-8')

    

    def generate_postman_collection(self, output_path: str):

        """生成Postman集合"""

        collection = {

            "info": {

                "name": self.spec['info']['title'],

                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"

            },

            "item": []

        }

        

        for path, methods in self.spec['paths'].items():

            for method, details in methods.items():

                if method in ['get', 'post', 'put', 'delete']:

                    item = {

                        "name": details.get('summary', path),

                        "request": {

                            "method": method.upper(),

                            "url": {

                                "raw": f"{{base_url}}{path}",

                                "host": ["{{base_url}}"],

                                "path": path.strip('/').split('/')

                            },

                            "description": details.get('description', '')

                        }

                    }

                    collection['item'].append(item)

        

        output_file = Path(output_path)

        output_file.write_text(json.dumps(collection, indent=2), encoding='utf-8')

    

    def generate_openapi_yaml(self, output_path: str):

        """生成OpenAPI YAML文件"""

        output_file = Path(output_path)

        output_file.write_text(yaml.dump(self.spec, allow_unicode=True), encoding='utf-8')

    

    def validate_spec(self) -> List[str]:

        """验证OpenAPI规范"""

        errors = []

        

        if 'openapi' not in self.spec:

            errors.append("缺少openapi版本字段")

        

        if 'info' not in self.spec:

            errors.append("缺少info字段")

        else:

            if 'title' not in self.spec['info']:

                errors.append("缺少info.title字段")

            if 'version' not in self.spec['info']:

                errors.append("缺少info.version字段")

        

        if 'paths' not in self.spec:

            errors.append("缺少paths字段")

        

        return errors





class APIVersionManager:

    """API版本管理器"""

    

    def __init__(self, versions_dir: str = "docs/api/versions"):

        self.versions_dir = Path(versions_dir)

        self.versions_dir.mkdir(parents=True, exist_ok=True)

    

    def save_version(self, version: str, spec: Dict[str, Any]):

        """保存API版本"""

        version_file = self.versions_dir / f"openapi_{version}.json"

        version_file.write_text(json.dumps(spec, indent=2), encoding='utf-8')

    

    def load_version(self, version: str) -> Dict[str, Any]:

        """加载API版本"""

        version_file = self.versions_dir / f"openapi_{version}.json"

        if version_file.exists():

            return json.loads(version_file.read_text(encoding='utf-8'))

        return None

    

    def list_versions(self) -> List[str]:

        """列出所有版本"""

        versions = []

        for file in self.versions_dir.glob("openapi_*.json"):

            version = file.stem.replace("openapi_", "")

            versions.append(version)

        return sorted(versions, reverse=True)

    

    def compare_versions(

        self,

        version1: str,

        version2: str

    ) -> Dict[str, Any]:

        """比较两个版本"""

        spec1 = self.load_version(version1)

        spec2 = self.load_version(version2)

        

        if not spec1 or not spec2:

            return {"error": "版本不存在"}

        

        diff = {

            "version1": version1,

            "version2": version2,

            "changes": {

                "added_paths": [],

                "removed_paths": [],

                "modified_paths": []

            }

        }

        

        paths1 = set(spec1.get('paths', {}).keys())

        paths2 = set(spec2.get('paths', {}).keys())

        

        diff["changes"]["added_paths"] = list(paths2 - paths1)

        diff["changes"]["removed_paths"] = list(paths1 - paths2)

        

        common_paths = paths1 & paths2

        for path in common_paths:

            if spec1['paths'][path] != spec2['paths'][path]:

                diff["changes"]["modified_paths"].append(path)

        

        return diff

```



### 3. GitHub Actions集成



```yaml

# .github/workflows/api-docs.yml

name: API Documentation



on:

  push:

    branches: [ main, develop ]

  pull_request:

    branches: [ main ]



jobs:

  generate-docs:

    runs-on: ubuntu-latest

    

    steps:

    - uses: actions/checkout@v4

    

    - name: Set up Python

      uses: actions/setup-python@v4

      with:

        python-version: '3.10'

    

    - name: Install dependencies

      run: |

        python -m pip install --upgrade pip

        pip install fastapi uvicorn pyyaml

    

    - name: Generate OpenAPI spec

      run: python scripts/generate_openapi.py

    

    - name: Generate Markdown docs

      run: python scripts/generate_api_docs.py

    

    - name: Deploy to GitHub Pages

      uses: peaceiris/actions-gh-pages@v3

      with:

        github_token: ${{ secrets.GITHUB_TOKEN }}

        publish_dir: ./docs/api

```



## 部署架构



### 本地开发环境



```bash

# 启动API服务

uvicorn main:app --reload



# 访问Swagger UI

open http://localhost:8000/docs



# 访问ReDoc

open http://localhost:8000/redoc



# 导出OpenAPI规范

curl http://localhost:8000/openapi.json > openapi.json

```



### 生产环境



```yaml

# docker-compose.yml

version: '3.8'



services:

  api:

    build: .

    ports:

      - "8000:8000"

    environment:

      - ENV=production

    volumes:

      - ./docs:/app/docs

```



## 实施计划



### 阶段1: 基础配置 (Day 1)



| 任务 | 工时 | 负责人 | 交付物 |

|------|------|--------|--------|

| FastAPI配置 | 2h | 开发者 | FastAPI应用 |

| API端点定义 | 3h | 开发者 | API端点 |

| 文档生成工具 | 2h | 开发者 | 工具代码 |



### 阶段2: 文档完善 (Day 2)



| 任务 | 工时 | 负责人 | 交付物 |

|------|------|--------|--------|

| API示例编写 | 2h | 开发者 | 示例代码 |

| 错误处理文档 | 1h | 开发者 | 错误文档 |

| 版本管理 | 1h | 开发者 | 版本管理 |



## 性能指标



| 指标 | 目标值 | 测量方法 |

|------|--------|---------|

| **文档覆盖率** | 100% | API端点文档化比例 |

| **文档准确性** | 100% | 文档与代码一致性 |

| **文档可交互性** | 100% | Swagger UI功能 |

| **文档更新及时性** | 100% | 自动生成 |



## 成本估算



| 项目 | 开源方案成本 | 商业方案成本 |

|------|-------------|-------------|

| **软件许可** | $0 | $0 |

| **FastAPI** | 免费 | 免费 |

| **Swagger UI** | 免费 | 免费 |

| **总成本** | **$0** | **$0** |



## 最佳实践



### 1. API命名规范



```

GET    /api/v1/factors          # 获取因子列表

POST   /api/v1/factors/calculate # 计算因子

GET    /api/v1/factors/{id}     # 获取单个因子

PUT    /api/v1/factors/{id}     # 更新因子

DELETE /api/v1/factors/{id}     # 删除因子

```



### 2. 响应格式规范



```json

{

  "data": {},

  "meta": {

    "total": 100,

    "page": 1,

    "per_page": 20

  },

  "links": {

    "self": "/api/v1/factors?page=1",

    "next": "/api/v1/factors?page=2"

  }

}

```



### 3. 错误处理规范



```json

{

  "error": {

    "code": "VALIDATION_ERROR",

    "message": "参数验证失败",

    "details": {

      "field": "start_date",

      "reason": "日期格式错误"

    }

  }

}

```



---



**文档版本**: v1.0.0

**创建日期**: 2026-04-07

**最后更新**: 2026-04-07

**状态**: Active

