---
module_id: DOC_DOC_001
version: 1.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构�?
standard_type: 专业量化机构文档
applicable_scope: 全系�?
compliance_level: 初始标准
parent_document: INDEX.md
implementation_status: 进行�?
---


# 代码示例

> 清风量化系统 v5.0 的策略开发、因子计算、部署脚本示�?


## 1. 策略开发示�?

### S001: 均线趋势跟踪策略

```python
# src/modules/strategies/s001_trend_follow.py

import numpy as np
import pandas as pd
from typing import Dict, Tuple
from qingfeng.core.base import BaseStrategy

class TrendFollowStrategy(BaseStrategy):
    """
    均线趋势跟踪策略
    
    逻辑�?
    1. 计算20日和50日均�?
    2. 快线 > 慢线 �?买入信号
    3. 快线 < 慢线 �?卖出信号
    """
    
    def __init__(self, ma_short=20, ma_long=50, stop_loss=0.05, take_profit=0.15):
        super().__init__()
        self.ma_short = ma_short
        self.ma_long = ma_long
        self.stop_loss = stop_loss
        self.take_profit = take_profit
    
    def calculate_signal(self, data: pd.DataFrame) -> Dict:
        """计算交易信号"""
        
        # 计算均线
        data['ma_short'] = data['close'].rolling(window=self.ma_short).mean()
        data['ma_long'] = data['close'].rolling(window=self.ma_long).mean()
        
        # 获取最新数�?
        latest = data.iloc[-1]
        prev = data.iloc[-2]
        
        # 生成信号
        signal = {
            'action': 'hold',
            'confidence': 0.0,
            'entry_price': None,
            'stop_loss': None,
            'take_profit': None
        }
        
        # 金叉：快线从下穿上慢�?
        if prev['ma_short'] <= prev['ma_long'] and latest['ma_short'] > latest['ma_long']:
            signal['action'] = 'buy'
            signal['confidence'] = 0.8
            signal['entry_price'] = latest['close']
            signal['stop_loss'] = latest['close'] * (1 - self.stop_loss)
            signal['take_profit'] = latest['close'] * (1 + self.take_profit)
        
        # 死叉：快线从上穿下慢�?
        elif prev['ma_short'] >= prev['ma_long'] and latest['ma_short'] < latest['ma_long']:
            signal['action'] = 'sell'
            signal['confidence'] = 0.8
        
        return signal
    
    def validate_signal(self, signal: Dict, context: Dict) -> bool:
        """验证信号有效�?""
        
        # 检查成交量
        if context.get('volume', 0) < 100000:
            return False
        
        # 检查价�?
        if context.get('price', 0) <= 0:
            return False
        
        return True

# 使用示例
if __name__ == "__main__":
    strategy = TrendFollowStrategy(ma_short=20, ma_long=50)
    
    # 加载数据
    data = pd.read_csv("data/000001.SZ.csv")
    
    # 计算信号
    signal = strategy.calculate_signal(data)
    print(f"信号: {signal['action']}, 信心�? {signal['confidence']}")
```


## 2. 因子计算示例

### ALPHA_001: 动量因子

```python
# src/modules/factors/alpha_001_momentum.py

import numpy as np
import pandas as pd
from typing import Union
from qingfeng.core.base import BaseFactor

class MomentumFactor(BaseFactor):
    """
    动量因子
    
    公式: Momentum = (Close_t - Close_t-n) / Close_t-n
    
    说明�?
    - 计算过去n天的收益�?
    - 正值表示上升趋势，负值表示下降趋�?
    """
    
    def __init__(self, period=20):
        super().__init__()
        self.period = period
        self.factor_id = "ALPHA_001"
        self.factor_name = "动量因子"
    
    def calculate(self, data: pd.DataFrame) -> Union[float, pd.Series]:
        """计算因子�?""
        
        if len(data) < self.period + 1:
            raise ValueError(f"数据长度不足，需要至少{self.period + 1}�?)
        
        # 计算收益�?
        close_prices = data['close'].values
        momentum = (close_prices[-1] - close_prices[-self.period-1]) / close_prices[-self.period-1]
        
        return momentum
    
    def calculate_batch(self, data: pd.DataFrame) -> pd.Series:
        """批量计算因子�?""
        
        close_prices = data['close'].values
        momentum_values = np.zeros(len(data))
        
        for i in range(self.period, len(data)):
            momentum_values[i] = (close_prices[i] - close_prices[i-self.period]) / close_prices[i-self.period]
        
        return pd.Series(momentum_values, index=data.index, name=self.factor_id)
    
    def validate(self, factor_value: float) -> bool:
        """验证因子值有效�?""
        
        # 检查是否为NaN
        if np.isnan(factor_value):
            return False
        
        # 检查是否为无穷�?
        if np.isinf(factor_value):
            return False
        
        return True

# 使用示例
if __name__ == "__main__":
    factor = MomentumFactor(period=20)
    
    # 加载数据
    data = pd.read_csv("data/000001.SZ.csv")
    
    # 计算因子
    momentum = factor.calculate(data)
    print(f"动量因子�? {momentum:.4f}")
    
    # 批量计算
    momentum_series = factor.calculate_batch(data)
    print(f"因子序列:\n{momentum_series.tail()}")
```


## 3. 部署脚本示例

### Docker部署脚本

```bash
#!/bin/bash
# scripts/deploy-docker.sh

set -e

echo "=== 清风量化系统 Docker部署脚本 ==="

# 1. 构建镜像
echo "1. 构建Docker镜像..."
docker build -t qingfeng:v4.0.2 .

# 2. 启动容器
echo "2. 启动容器..."
docker-compose -f docker-compose.prod.yml up -d

# 3. 等待服务启动
echo "3. 等待服务启动..."
sleep 10

# 4. 健康检�?
echo "4. 执行健康检�?.."
for i in {1..30}; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "�?服务已启�?
        break
    fi
    echo "等待服务启动... ($i/30)"
    sleep 1
done

# 5. 初始化数据库
echo "5. 初始化数据库..."
docker-compose exec -T datahub python scripts/init_db.py

# 6. 加载历史数据
echo "6. 加载历史数据..."
docker-compose exec -T datahub python scripts/download_data.py \
    --start-date 2021-01-01 \
    --end-date 2026-03-28

# 7. 验证部署
echo "7. 验证部署..."
docker-compose ps
docker-compose logs --tail=20

echo "�?部署完成�?
```

### Kubernetes部署脚本

```bash
#!/bin/bash
# scripts/deploy-k8s.sh

set -e

echo "=== 清风量化系统 Kubernetes部署脚本 ==="

# 1. 创建命名空间
echo "1. 创建命名空间..."
kubectl create namespace qingfeng || true

# 2. 创建ConfigMap
echo "2. 创建ConfigMap..."
kubectl create configmap qingfeng-config \
    --from-file=config/system.yaml \
    --from-file=config/strategies.yaml \
    -n qingfeng || true

# 3. 创建Secret
echo "3. 创建Secret..."
kubectl create secret generic qingfeng-secret \
    --from-literal=db-password=$DB_PASSWORD \
    --from-literal=api-key=$API_KEY \
    -n qingfeng || true

# 4. 部署应用
echo "4. 部署应用..."
kubectl apply -f k8s/datahub-deployment.yaml -n qingfeng
kubectl apply -f k8s/factor-calculator-deployment.yaml -n qingfeng
kubectl apply -f k8s/strategy-engine-deployment.yaml -n qingfeng
kubectl apply -f k8s/trade-executor-deployment.yaml -n qingfeng

# 5. 等待部署完成
echo "5. 等待部署完成..."
kubectl rollout status deployment/qingfeng-datahub -n qingfeng
kubectl rollout status deployment/qingfeng-factor-calculator -n qingfeng

# 6. 验证部署
echo "6. 验证部署..."
kubectl get pods -n qingfeng
kubectl get svc -n qingfeng

echo "�?部署完成�?
```

### 监控配置脚本

```bash
#!/bin/bash
# scripts/setup-monitoring.sh

set -e

echo "=== 清风量化系统 监控配置脚本 ==="

# 1. 部署Prometheus
echo "1. 部署Prometheus..."
docker run -d \
    --name prometheus \
    -p 9090:9090 \
    -v $(pwd)/config/prometheus.yml:/etc/prometheus/prometheus.yml \
    prom/prometheus

# 2. 部署Grafana
echo "2. 部署Grafana..."
docker run -d \
    --name grafana \
    -p 3000:3000 \
    -e GF_SECURITY_ADMIN_PASSWORD=admin \
    grafana/grafana

# 3. 部署AlertManager
echo "3. 部署AlertManager..."
docker run -d \
    --name alertmanager \
    -p 9093:9093 \
    -v $(pwd)/config/alertmanager.yml:/etc/alertmanager/alertmanager.yml \
    prom/alertmanager

# 4. 部署ELK日志系统
echo "4. 部署ELK日志系统..."
docker-compose -f docker-compose.elk.yml up -d

# 5. 配置告警规则
echo "5. 配置告警规则..."
curl -X POST http://localhost:9093/api/v1/alerts \
    -H "Content-Type: application/json" \
    -d @config/alert-rules.json

echo "�?监控配置完成�?
echo "Prometheus: http://localhost:9090"
echo "Grafana: http://localhost:3000"
echo "AlertManager: http://localhost:9093"
```


## 4. 回测运行示例

```python
# scripts/backtest.py

import argparse
import pandas as pd
from qingfeng.modules import BacktestEngine
from qingfeng.modules.strategies import TrendFollowStrategy

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--strategy', default='S001')
    parser.add_argument('--start-date', default='2025-01-01')
    parser.add_argument('--end-date', default='2026-03-28')
    parser.add_argument('--output', default='results/backtest.html')
    args = parser.parse_args()
    
    # 初始化回测引�?
    engine = BacktestEngine()
    
    # 加载策略
    if args.strategy == 'S001':
        strategy = TrendFollowStrategy(ma_short=20, ma_long=50)
    else:
        raise ValueError(f"未知策略: {args.strategy}")
    
    # 加载数据
    data = pd.read_csv(f"data/000001.SZ.csv")
    data['date'] = pd.to_datetime(data['date'])
    data = data[(data['date'] >= args.start_date) & (data['date'] <= args.end_date)]
    
    # 运行回测
    results = engine.backtest(
        strategy=strategy,
        data=data,
        initial_capital=1000000,
        commission=0.001
    )
    
    # 生成报告
    print(f"年化收益: {results['annual_return']:.2%}")
    print(f"夏普比率: {results['sharpe_ratio']:.2f}")
    print(f"最大回�? {results['max_drawdown']:.2%}")
    print(f"胜率: {results['win_rate']:.2%}")
    
    # 保存报告
    engine.save_report(results, args.output)
    print(f"报告已保存到: {args.output}")

if __name__ == "__main__":
    main()
```


**最后更�?*: 2026-03-28  
**维护�?*: 清风量化系统
