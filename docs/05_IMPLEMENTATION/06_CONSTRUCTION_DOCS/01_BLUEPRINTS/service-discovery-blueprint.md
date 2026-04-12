---

module_id: SERVICE_DISCOVERY_001

version: 1.0.0

status: Active

created_date: 2026-04-07

last_updated: 2026-04-07

owner: 首席文档架构师

responsibility:

  - 服务注册

  - 服务发现

  - 健康检查

  - 负载均衡

standard_type: 专业量化机构蓝图

compliance_level: 专业标准

layer: layer_05

---



# 服务发现蓝图



> **核心职责**: 提供动态的服务注册与发现机制，支持健康检查和负载均衡

> **职责边界**: 

> - ✅ 本文档负责：服务注册、服务发现、健康检查、负载均衡

> - ❌ 本文档不负责：配置管理（由配置中心模块负责）、API网关（由API网关模块负责）



## 核心定位



负责服务发现模块的设计与构建，提供动态的服务注册与发现、健康检查、负载均衡能力，支持微服务架构下的服务治理，确保服务调用的可靠性和可用性。



## 设计目标



### 主要目标



1. **服务注册**: 服务启动时自动注册到注册中心

2. **服务发现**: 动态发现可用服务实例

3. **健康检查**: 实时监控服务健康状态

4. **负载均衡**: 支持多种负载均衡策略



### 质量目标



- 服务发现延迟: < 100ms

- 健康检查准确性: 99.9%

- 服务可用性: 99.95%

- 故障恢复时间: < 30s



## 开源方案选型



### 推荐方案: Consul



| 属性 | 详情 |

|------|------|

| **GitHub** | https://github.com/hashicorp/consul |

| **Stars** | 28,000+ |

| **License** | MPL 2.0 |

| **语言** | Go |

| **特点** | 服务发现 + 配置管理 + 健康检查 |



**选择理由**:

1. **功能全面**: 服务发现 + 配置管理一体化

2. **成熟稳定**: HashiCorp出品，生产级可靠性

3. **健康检查**: 支持HTTP、TCP、Script多种检查方式

4. **DNS接口**: 支持DNS查询服务，使用简单

5. **服务网格**: 支持Connect服务网格

6. **个人友好**: 单节点即可运行，适合个人开发



### 备选方案



| 项目 | Stars | 特点 | 推荐度 |

|------|-------|------|--------|

| **etcd** | 47k+ | 分布式KV存储 | ⭐⭐⭐⭐ |

| **Eureka** | 12k+ | Netflix开源服务发现 | ⭐⭐⭐ |

| **Nacos** | 29k+ | 阿里开源服务发现 | ⭐⭐⭐⭐ |



## 核心功能设计



### 1. 服务注册模块



```python

import consul

import socket

import time

from typing import Dict, Any, Optional

from datetime import datetime



class ServiceRegistry:

    """服务注册器"""

    

    def __init__(self, consul_host: str = "localhost", consul_port: int = 8500):

        self.client = consul.Consul(host=consul_host, port=consul_port)

        self.registered_services = {}

    

    def register_service(

        self,

        service_name: str,

        service_port: int,

        service_address: str = None,

        tags: list = None,

        meta: dict = None,

        check_interval: str = "10s",

        check_timeout: str = "5s"

    ) -> bool:

        """注册服务"""

        if service_address is None:

            service_address = socket.gethostbyname(socket.gethostname())

        

        service_id = f"{service_name}-{service_address}-{service_port}"

        

        check = consul.Check.http(

            url=f"http://{service_address}:{service_port}/health",

            interval=check_interval,

            timeout=check_timeout,

            deregister=f"60s"

        )

        

        success = self.client.agent.service.register(

            name=service_name,

            service_id=service_id,

            address=service_address,

            port=service_port,

            tags=tags or [],

            meta=meta or {},

            check=check

        )

        

        if success:

            self.registered_services[service_id] = {

                "name": service_name,

                "address": service_address,

                "port": service_port,

                "registered_at": datetime.now().isoformat()

            }

        

        return success

    

    def deregister_service(self, service_id: str) -> bool:

        """注销服务"""

        success = self.client.agent.service.deregister(service_id)

        

        if success and service_id in self.registered_services:

            del self.registered_services[service_id]

        

        return success

    

    def deregister_all(self):

        """注销所有服务"""

        for service_id in list(self.registered_services.keys()):

            self.deregister_service(service_id)

```



### 2. 服务发现模块



```python

class ServiceDiscovery:

    """服务发现器"""

    

    def __init__(self, consul_host: str = "localhost", consul_port: int = 8500):

        self.client = consul.Consul(host=consul_host, port=consul_port)

        self.cache = {}

        self.cache_ttl = 30

    

    def discover_service(

        self,

        service_name: str,

        tag: str = None,

        passing_only: bool = True

    ) -> list:

        """发现服务实例"""

        cache_key = f"{service_name}:{tag}:{passing_only}"

        

        if cache_key in self.cache:

            cached_data, cached_time = self.cache[cache_key]

            if time.time() - cached_time < self.cache_ttl:

                return cached_data

        

        _, services = self.client.health.service(

            service_name,

            tag=tag,

            passing=passing_only

        )

        

        instances = []

        for service in services:

            service_info = service['Service']

            instances.append({

                "id": service_info['ID'],

                "name": service_info['Service'],

                "address": service_info['Address'],

                "port": service_info['Port'],

                "tags": service_info['Tags'],

                "meta": service_info['Meta']

            })

        

        self.cache[cache_key] = (instances, time.time())

        

        return instances

    

    def get_service_address(

        self,

        service_name: str,

        tag: str = None

    ) -> Optional[str]:

        """获取单个服务地址（负载均衡）"""

        instances = self.discover_service(service_name, tag)

        

        if not instances:

            return None

        

        instance = self._select_instance(instances)

        

        return f"{instance['address']}:{instance['port']}"

    

    def _select_instance(self, instances: list) -> dict:

        """选择服务实例（简单轮询）"""

        if not instances:

            return None

        

        if not hasattr(self, '_round_robin_index'):

            self._round_robin_index = {}

        

        service_name = instances[0]['name']

        

        if service_name not in self._round_robin_index:

            self._round_robin_index[service_name] = 0

        

        index = self._round_robin_index[service_name] % len(instances)

        self._round_robin_index[service_name] += 1

        

        return instances[index]

    

    def watch_service(

        self,

        service_name: str,

        callback: callable,

        tag: str = None

    ):

        """监听服务变更"""

        index = None

        

        while True:

            try:

                index, services = self.client.health.service(

                    service_name,

                    tag=tag,

                    index=index,

                    wait="10m"

                )

                

                instances = [

                    {

                        "id": s['Service']['ID'],

                        "address": s['Service']['Address'],

                        "port": s['Service']['Port']

                    }

                    for s in services

                ]

                

                callback(instances)

            

            except Exception as e:

                print(f"Watch error: {e}")

                time.sleep(5)

```



### 3. 健康检查模块



```python

class HealthChecker:

    """健康检查器"""

    

    def __init__(self, consul_host: str = "localhost", consul_port: int = 8500):

        self.client = consul.Consul(host=consul_host, port=consul_port)

    

    def check_service_health(self, service_name: str) -> Dict[str, Any]:

        """检查服务健康状态"""

        _, checks = self.client.health.checks(service_name)

        

        health_status = {

            "service": service_name,

            "total": len(checks),

            "passing": 0,

            "warning": 0,

            "critical": 0,

            "instances": []

        }

        

        for check in checks:

            status = check['Status']

            

            if status == "passing":

                health_status["passing"] += 1

            elif status == "warning":

                health_status["warning"] += 1

            else:

                health_status["critical"] += 1

            

            health_status["instances"].append({

                "node": check['Node'],

                "check_id": check['CheckID'],

                "status": status,

                "output": check['Output']

            })

        

        return health_status

    

    def get_healthy_instances(self, service_name: str) -> list:

        """获取健康的服务实例"""

        _, services = self.client.health.service(service_name, passing=True)

        

        return [

            {

                "id": s['Service']['ID'],

                "address": s['Service']['Address'],

                "port": s['Service']['Port']

            }

            for s in services

        ]

    

    def register_health_check(

        self,

        check_name: str,

        check_type: str,

        target: str,

        interval: str = "10s",

        timeout: str = "5s"

    ):

        """注册健康检查"""

        if check_type == "http":

            check = consul.Check.http(

                url=target,

                interval=interval,

                timeout=timeout

            )

        elif check_type == "tcp":

            check = consul.Check.tcp(

                target=target,

                interval=interval,

                timeout=timeout

            )

        else:

            raise ValueError(f"Unsupported check type: {check_type}")

        

        return self.client.agent.check.register(

            name=check_name,

            check=check

        )

```



### 4. 负载均衡模块



```python

import random

from typing import List, Dict

from collections import defaultdict



class LoadBalancer:

    """负载均衡器"""

    

    def __init__(self, service_discovery: ServiceDiscovery):

        self.discovery = service_discovery

        self.strategies = {

            "round_robin": self._round_robin,

            "random": self._random,

            "least_connections": self._least_connections,

            "weighted": self._weighted

        }

        self.strategy = "round_robin"

        self.connections = defaultdict(int)

        self._round_robin_index = defaultdict(int)

    

    def set_strategy(self, strategy: str):

        """设置负载均衡策略"""

        if strategy not in self.strategies:

            raise ValueError(f"Unknown strategy: {strategy}")

        self.strategy = strategy

    

    def get_instance(

        self,

        service_name: str,

        tag: str = None

    ) -> Optional[Dict]:

        """获取服务实例"""

        instances = self.discovery.discover_service(service_name, tag)

        

        if not instances:

            return None

        

        _fn = self.strategies[self.strategy]

        return _fn(instances, service_name)

    

    def _round_robin(self, instances: List[Dict], service_name: str) -> Dict:

        """轮询策略"""

        index = self._round_robin_index[service_name] % len(instances)

        self._round_robin_index[service_name] += 1

        return instances[index]

    

    def _random(self, instances: List[Dict], service_name: str) -> Dict:

        """随机策略"""

        return random.choice(instances)

    

    def _least_connections(self, instances: List[Dict], service_name: str) -> Dict:

        """最少连接策略"""

        min_conn = float('inf')

        selected = instances[0]

        

        for instance in instances:

            instance_id = instance['id']

            conn_count = self.connections.get(instance_id, 0)

            

            if conn_count < min_conn:

                min_conn = conn_count

                selected = instance

        

        return selected

    

    def _weighted(self, instances: List[Dict], service_name: str) -> Dict:

        """加权策略"""

        weights = []

        for instance in instances:

            weight = instance.get('meta', {}).get('weight', 1)

            weights.extend([instance] * weight)

        

        return random.choice(weights)

    

    def increment_connection(self, instance_id: str):

        """增加连接计数"""

        self.connections[instance_id] += 1

    

    def decrement_connection(self, instance_id: str):

        """减少连接计数"""

        if instance_id in self.connections:

            self.connections[instance_id] -= 1

            if self.connections[instance_id] <= 0:

                del self.connections[instance_id]

```



## 技术实现



### 1. Consul部署配置



```yaml

version: '3.8'



services:

  consul:

    image: consul:1.15

    container_name: zephyr-consul

    ports:

      - "8500:8500"

      - "8600:8600/udp"

    command: agent -server -ui -bootstrap-expect=1 -client=0.0.0.0

    volumes:

      - consul_data:/consul/data

    environment:

      - CONSUL_BIND_INTERFACE=eth0

    healthcheck:

      test: ["CMD", "consul", "members"]

      interval: 10s

      timeout: 5s

      retries: 3

    networks:

      - zephyr-network



volumes:

  consul_data:



networks:

  zephyr-network:

    external: true

```



### 2. 服务注册装饰器



```python

import functools

import signal

import sys



def register_service(

    service_name: str,

    service_port: int,

    consul_host: str = "localhost",

    consul_port: int = 8500,

    tags: list = None,

    meta: dict = None

):

    """服务注册装饰器"""

    def decorator(func):

        @functools.wraps(func)

        def wrapper(*args, **kwargs):

            registry = ServiceRegistry(consul_host, consul_port)

            

            registry.register_service(

                service_name=service_name,

                service_port=service_port,

                tags=tags,

                meta=meta

            )

            

            def cleanup(signum, frame):

                print("\nDeregistering service...")

                registry.deregister_all()

                sys.exit(0)

            

            signal.signal(signal.SIGINT, cleanup)

            signal.signal(signal.SIGTERM, cleanup)

            

            try:

                return func(*args, **kwargs)

            finally:

                registry.deregister_all()

        

        return wrapper

    return decorator



@register_service(

    service_name="factor-engine",

    service_port=8001,

    tags=["factor", "engine"],

    meta={"version": "1.0.0"}

)

def start_factor_engine():

    """启动因子引擎服务"""

    from fastapi import FastAPI

    import uvicorn

    

    app = FastAPI()

    

    @app.get("/health")

    def health():

        return {"status": "healthy"}

    

    uvicorn.run(app, host="0.0.0.0", port=8001)

```



### 3. 服务客户端



```python

import requests

from typing import Optional, Dict, Any



class ServiceClient:

    """服务客户端"""

    

    def __init__(

        self,

        service_name: str,

        consul_host: str = "localhost",

        consul_port: int = 8500,

        load_balance_strategy: str = "round_robin"

    ):

        self.service_name = service_name

        self.discovery = ServiceDiscovery(consul_host, consul_port)

        self.load_balancer = LoadBalancer(self.discovery)

        self.load_balancer.set_strategy(load_balance_strategy)

    

    def request(

        self,

        method: str,

        path: str,

        **kwargs

    ) -> Optional[requests.Response]:

        """发送请求"""

        instance = self.load_balancer.get_instance(self.service_name)

        

        if not instance:

            raise Exception(f"No available instances for {self.service_name}")

        

        instance_id = instance['id']

        url = f"http://{instance['address']}:{instance['port']}{path}"

        

        try:

            self.load_balancer.increment_connection(instance_id)

            response = requests.request(method, url, **kwargs)

            return response

        finally:

            self.load_balancer.decrement_connection(instance_id)

    

    def get(self, path: str, **kwargs) -> Optional[requests.Response]:

        """GET请求"""

        return self.request("GET", path, **kwargs)

    

    def post(self, path: str, **kwargs) -> Optional[requests.Response]:

        """POST请求"""

        return self.request("POST", path, **kwargs)

    

    def put(self, path: str, **kwargs) -> Optional[requests.Response]:

        """PUT请求"""

        return self.request("PUT", path, **kwargs)

    

    def delete(self, path: str, **kwargs) -> Optional[requests.Response]:

        """DELETE请求"""

        return self.request("DELETE", path, **kwargs)

```



## 数据模型



### 1. 服务实例模型



```python

from pydantic import BaseModel, Field

from typing import List, Dict, Optional

from datetime import datetime



class ServiceInstance(BaseModel):

    """服务实例"""

    id: str = Field(..., description="服务实例ID")

    name: str = Field(..., description="服务名称")

    address: str = Field(..., description="服务地址")

    port: int = Field(..., description="服务端口")

    tags: List[str] = Field(default_factory=list, description="服务标签")

    meta: Dict[str, Any] = Field(default_factory=dict, description="服务元数据")

    status: str = Field(default="passing", description="健康状态")

    registered_at: datetime = Field(default_factory=datetime.now)



class HealthCheckResult(BaseModel):

    """健康检查结果"""

    service_name: str = Field(..., description="服务名称")

    total: int = Field(..., description="总实例数")

    passing: int = Field(..., description="健康实例数")

    warning: int = Field(..., description="警告实例数")

    critical: int = Field(..., description="异常实例数")

    instances: List[Dict[str, Any]] = Field(default_factory=list)



class ServiceRegistration(BaseModel):

    """服务注册信息"""

    name: str = Field(..., description="服务名称")

    port: int = Field(..., description="服务端口")

    address: Optional[str] = Field(None, description="服务地址")

    tags: List[str] = Field(default_factory=list, description="服务标签")

    meta: Dict[str, Any] = Field(default_factory=dict, description="服务元数据")

    check_interval: str = Field(default="10s", description="健康检查间隔")

    check_timeout: str = Field(default="5s", description="健康检查超时")

```



### 2. Consul服务结构



```json

{

  "Service": {

    "ID": "factor-engine-192.168.1.100-8001",

    "Service": "factor-engine",

    "Tags": ["factor", "engine"],

    "Address": "192.168.1.100",

    "Port": 8001,

    "Meta": {

      "version": "1.0.0",

      "weight": "10"

    }

  },

  "Checks": [

    {

      "Node": "node-1",

      "CheckID": "service:factor-engine-192.168.1.100-8001",

      "Name": "Service 'factor-engine' check",

      "Status": "passing",

      "Output": "HTTP GET http://192.168.1.100:8001/health: 200 OK"

    }

  ]

}

```



## 实施路径



### Phase 1: 核心功能（Week 1）



**目标**: 实现基础服务注册与发现



**任务清单**:

- [ ] 部署Consul服务（Docker）

- [ ] 实现服务注册模块

- [ ] 实现服务发现模块

- [ ] 实现健康检查

- [ ] 编写单元测试



**交付物**:

- Consul部署配置

- ServiceRegistry核心类

- ServiceDiscovery核心类

- 单元测试覆盖率≥80%



### Phase 2: 高级功能（Week 2）



**目标**: 实现负载均衡和服务治理



**任务清单**:

- [ ] 实现负载均衡模块

- [ ] 实现服务客户端

- [ ] 实现服务监听

- [ ] 实现故障转移

- [ ] 编写集成测试



**交付物**:

- LoadBalancer类

- ServiceClient类

- 集成测试覆盖率≥70%



### Phase 3: 生产优化（Week 3）



**目标**: 生产环境优化和监控



**任务清单**:

- [ ] 性能优化（缓存、连接池）

- [ ] 监控指标集成

- [ ] 服务治理策略

- [ ] 文档完善

- [ ] 生产部署验证



**交付物**:

- 性能优化方案

- 监控仪表板

- 运维文档



## 文档治理



### System_Manifest.md索引



```markdown

#### Layer 5: 策略执行层



##### 服务发现模块

- **模块ID**: SERVICE_DISCOVERY_001

- **文档**: 服务发现蓝图

- **职责**: 服务注册、服务发现、健康检查、负载均衡

- **开源方案**: Consul

- **状态**: Active

```



### 模块职责边界



| 模块 | 职责 | 不负责 |

|------|------|--------|

| **服务发现** | 服务注册、服务发现、健康检查 | 配置管理、API网关 |

| **配置中心** | 配置存储、版本管理 | 服务发现 |

| **API网关** | 请求路由、限流熔断 | 服务发现 |



### 版本管理策略



- **v1.0.0**: 初始版本，核心功能实现

- **v1.1.0**: 负载均衡优化

- **v1.2.0**: 服务治理增强



## 风险评估



### 技术风险



| 风险 | 等级 | 影响 | 缓解措施 |

|------|------|------|----------|

| Consul单点故障 | P1 | 服务不可发现 | 部署Consul集群 |

| 服务雪崩 | P1 | 系统崩溃 | 熔断降级机制 |

| 网络分区 | P2 | 服务发现延迟 | 本地缓存机制 |



### 实施风险



| 风险 | 等级 | 影响 | 缓解措施 |

|------|------|------|----------|

| 服务迁移复杂 | P2 | 迁移时间长 | 分阶段迁移 |

| 团队学习成本 | P2 | 开发效率降低 | 编写详细文档 |



### 治理风险



| 风险 | 等级 | 影响 | 缓解措施 |

|------|------|------|----------|

| 服务文档缺失 | P2 | 维护困难 | 完善文档模板 |

| 服务命名混乱 | P2 | 发现困难 | 制定命名规范 |



## 监控指标



### 关键指标



```python

from prometheus_client import Counter, Histogram, Gauge



service_discovery_total = Counter(

    'service_discovery_total',

    '服务发现总数',

    ['service_name', 'status']

)



service_discovery_duration = Histogram(

    'service_discovery_duration_seconds',

    '服务发现耗时',

    ['service_name']

)



service_instances_count = Gauge(

    'service_instances_count',

    '服务实例数量',

    ['service_name', 'status']

)



load_balance_requests = Counter(

    'load_balance_requests_total',

    '负载均衡请求总数',

    ['service_name', 'strategy']

)

```



### 告警规则



```yaml

groups:

  - name: service_discovery_alerts

    rules:

      - alert: ServiceDiscoveryDown

        expr: up{job="consul"} == 0

        for: 1m

        labels:

          severity: critical

        annotations:

          summary: "服务发现服务不可用"

          description: "Consul服务已停止运行超过1分钟"

      

      - alert: NoHealthyInstances

        expr: service_instances_count{status="passing"} == 0

        for: 2m

        labels:

          severity: critical

        annotations:

          summary: "服务无健康实例"

          description: "服务{{ $labels.service_name }}没有健康的实例"

```



## 最佳实践



### 1. 服务命名规范



```python

SERVICE_NAME_PATTERNS = {

    "factor_engine": "factor-engine",

    "strategy_engine": "strategy-engine",

    "data_service": "data-service",

    "api_gateway": "api-gateway"

}



def generate_service_id(service_name: str, address: str, port: int) -> str:

    """生成服务ID"""

    return f"{service_name}-{address.replace('.', '-')}-{port}"

```



### 2. 健康检查端点



```python

from fastapi import FastAPI

from datetime import datetime



app = FastAPI()



@app.get("/health")

def health_check():

    """健康检查端点"""

    return {

        "status": "healthy",

        "timestamp": datetime.now().isoformat(),

        "service": "factor-engine",

        "version": "1.0.0"

    }



@app.get("/ready")

def readiness_check():

    """就绪检查端点"""

    return {

        "status": "ready",

        "timestamp": datetime.now().isoformat()

    }

```



### 3. 服务元数据



```python

SERVICE_METADATA = {

    "version": "1.0.0",

    "weight": "10",

    "region": "cn-east-1",

    "zone": "zone-a",

    "environment": "production"

}

```



---



**文档版本**: v1.0.0

**创建日期**: 2026-04-07

**最后更新**: 2026-04-07

**状态**: Active



## 接口与契约（蓝图终稿）



- **契约真源**：`API_Contract.md`

- **对外接口边界**：本模块对外提供服务注册/发现/健康检查与元数据查询能力；不替代网关鉴权/流量治理，不直接承诺业务 API 的语义正确性。



## 验收标准（可检查）



- 在测试环境中完成至少 1 个服务的注册→发现→健康检查闭环，并可按服务名/标签查询到一致的实例列表与元数据。



## 已知限制



- 不同运行环境（K8s/VM/本地）服务发现机制存在差异；实施阶段需在契约真源或子契约中固化默认实现、回滚策略与兼容矩阵。

