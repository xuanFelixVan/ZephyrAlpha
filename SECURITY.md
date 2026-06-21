# 安全策略（Security）

## 报告漏洞

若你发现与本仓库相关的**安全问题**（例如密钥泄露、可远程利用的接口缺陷），请 **不要** 在公开 Issue 中披露细节。

建议做法：

1. 通过仓库托管方（如 GitHub）的 **Private vulnerability reporting** 联系维护者；或
2. 向项目 Owner 的**私有安全联系渠道**报告。

## 开发侧约定

- **切勿**将真实 API 密钥、账号密码提交到 Git；使用 `.env`（已列入 `.gitignore`）与 `.env.example` 模板
- LLM 安全网关设计见 [llm_security_gateway_interface.md](docs/03_modules/_b_track_interfaces/llm_security_gateway_interface.md)
- 使用 `docker-compose` 启动 Grafana 时，默认管理员口令仅适用于**本地开发**；生产或共享环境必须通过环境变量改写 `GRAFANA_ADMIN_PASSWORD`，勿使用默认值

## 披露时间线

维护者在收到有效报告后，会在合理时间内确认、修复并协调披露。
