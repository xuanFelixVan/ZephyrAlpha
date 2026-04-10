# 安全策略（Security）

## 报告漏洞

若你发现与本仓库相关的**安全问题**（例如密钥泄露、可远程利用的接口缺陷），请 **不要** 在公开 Issue 中披露细节。

建议做法：

1. 通过仓库托管方（如 GitHub）的 **Private vulnerability reporting** 联系维护者；或  
2. 向项目 Owner 的**私有安全联系渠道**报告（由 Owner 在组织内公布）。

## 开发侧约定

- **切勿**将真实 API 密钥、账号密码提交到 Git；使用 `.env`（已列入 `.gitignore`）与 `.env.example` 模板。
- 更完整的开发与运维安全说明见：  
  [docs/05_IMPLEMENTATION/02_DEVELOPMENT/SECURITY.md](docs/05_IMPLEMENTATION/02_DEVELOPMENT/SECURITY.md)

## 披露时间线

维护者在收到有效报告后，会在合理时间内确认、修复并协调披露（具体取决于严重性与发布节奏）。
