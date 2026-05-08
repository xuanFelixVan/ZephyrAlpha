"""L06 券商适配器包（INV-005 Broker ACL）。

仅本包内代码允许直接引用券商 SDK（如 ib_insync、futu、longport）及 broker 下单调用。
其他层须通过 L06 对外契约与适配器交互，禁止直连券商 API。
"""

__all__ = ['simulation_broker']
