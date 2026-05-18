# [BLUEPRINT] MOD-INF-005 | scripts/governance/_shared/__init__.py | §
"""
_shared — 审计脚本共享基础设施

对标 SCRIPT-QUALITY-001 D-D-05（禁止跨脚本复制粘贴逻辑）
所有公共常量、工具函数集中在此，脚本通过 import 引用。

模块清单：
- base      : BaseAuditScript 审计脚本基类（根因修复——统一 Finding/iter_files/退出码）
- constants : REPO_ROOT / EXCLUDE_DIRS / SCAN_EXTENSIONS 等共享常量
- frontmatter : parse_frontmatter() / parse_yaml_header() 统一解析
- encoding : ensure_utf8_stdout() 编码安全
- walk : iter_files() 目录遍历共享工具
- yaml_utils : load_yaml() YAML 文件加载共享工具
"""
