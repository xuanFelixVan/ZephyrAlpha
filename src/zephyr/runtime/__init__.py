"""ZephyrAlpha 交易运行时入口层。

承载盘中/盘后等运行时编排器，把各域组件（D-DATA/D-FACTOR/D-INFRA）组装成
可运行的单进程。区别于 orchestrator/（AI 开发流程编排），本包聚焦交易运行时。
"""
