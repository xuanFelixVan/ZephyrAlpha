# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.l10_compliance.test_artifact_scanner_rules
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""
单元测试：src/zephyr/l10_compliance/artifact_scanner.py — S-02~S-08 规则
=========================================================================

覆盖矩阵：
  S-01 SSRF:
    - 原始 IP URL × 1
    - localhost URL × 1
    - 云元数据端点 × 1
  S-02 Path Traversal:
    - 深层遍历 /etc × 1
    - 绝对路径 /var × 1
  S-03 Credential:
    - hardcoded api_key × 1
    - hardcoded password × 1
  S-04 Token Leak:
    - GitHub PAT × 1
    - OpenAI key × 1
    - JWT token × 1
  S-05 Sensitive File:
    - .env 引用 × 1
    - .ssh/id_rsa 引用 × 1
  S-06 Command Injection:
    - os.system + f-string × 1
  S-07 Config Secret:
    - YAML hardcoded secret × 1
  S-08 Notebook:
    - os.system in notebook × 1
    - !pip install × 1
"""

from pathlib import Path

from zephyr.l10_compliance.artifact_scanner import ArtifactScanner


_scanner = ArtifactScanner()


class TestS01SSRF:
    def test_raw_ip_url(self):
        report = _scanner.scan_content('url = "http://192.168.1.1/internal"')
        assert report.error_count >= 1
        assert any(f.rule_id == "S-01-SSRF-IP" for f in report.findings)

    def test_localhost_url(self):
        report = _scanner.scan_content('requests.get("http://localhost:8080/api")')
        assert report.error_count >= 1
        assert any(f.rule_id == "S-01-SSRF-LOCALHOST" for f in report.findings)

    def test_cloud_metadata_endpoint(self):
        report = _scanner.scan_content('resp = requests.get("http://169.254.169.254/latest/meta-data/")')
        assert report.error_count >= 1
        assert any(f.rule_id == "S-01-SSRF-METADATA" for f in report.findings)


class TestS02PathTraversal:
    def test_deep_traversal_etc(self):
        report = _scanner.scan_content('path = "../../etc/passwd"')
        assert report.error_count >= 1
        assert any(f.rule_id == "S-02-PATH-TRAVERSAL" for f in report.findings)

    def test_absolute_path_var(self):
        report = _scanner.scan_content('log_path = "/var/log/app.log"')
        assert any(f.rule_id == "S-02-PATH-ABSOLUTE" for f in report.findings)


class TestS03Credential:
    def test_hardcoded_api_key(self):
        report = _scanner.scan_content('api_key = "sk-abc123def456ghi789jkl012mno345pqr"')
        assert report.error_count >= 1
        assert any(f.rule_id == "S-03-CRED-HARDCODED" for f in report.findings)

    def test_hardcoded_password(self):
        report = _scanner.scan_content('password = "supersecretpassword123"')
        assert report.error_count >= 1
        assert any(f.rule_id == "S-03-CRED-HARDCODED" for f in report.findings)


class TestS04TokenLeak:
    def test_github_pat(self):
        report = _scanner.scan_content('token = "ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghij"')
        assert report.error_count >= 1
        assert any(f.rule_id == "S-04-TOKEN-GITHUB" for f in report.findings)

    def test_openai_key(self):
        report = _scanner.scan_content('key = "sk-proj-abcdefghijklmnopqrstuvwxyz1234567890ABCD"')
        assert report.error_count >= 1
        assert any(f.rule_id == "S-04-TOKEN-OPENAI" for f in report.findings)

    def test_jwt_token(self):
        report = _scanner.scan_content('token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"')
        assert any(f.rule_id == "S-04-TOKEN-JWT" for f in report.findings)


class TestS05SensitiveFile:
    def test_env_reference(self):
        report = _scanner.scan_content('load_dotenv(".env.production")')
        assert any(f.rule_id == "S-05-FILE-ENV" for f in report.findings)

    def test_ssh_key_reference(self):
        report = _scanner.scan_content('key_path = "~/.ssh/id_rsa"')
        assert any(f.rule_id == "S-05-FILE-ENV" for f in report.findings)


class TestS06CommandInjection:
    def test_os_system_fstring(self):
        report = _scanner.scan_content('os.system(f"ping {user_input}")')
        assert report.error_count >= 1
        assert any(f.rule_id == "S-06-CMD-INJECT" for f in report.findings)


class TestS07ConfigSecret:
    def test_yaml_hardcoded_secret(self):
        import tempfile
        import os

        yaml_content = "database:\n  password: mysecretpassword123\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
            f.write(yaml_content)
            tmp_path = Path(f.name)

        try:
            report = _scanner.scan_file(tmp_path)
            assert any(f.rule_id == "S-07-CONFIG-SECRET" for f in report.findings)
        finally:
            os.unlink(tmp_path)


class TestS08Notebook:
    def test_notebook_os_system(self):
        import tempfile
        import os

        nb_content = '{"cells":[{"cell_type":"code","source":["os.system(\\"ls\\")"]}]}'
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ipynb", delete=False, encoding="utf-8") as f:
            f.write(nb_content)
            tmp_path = Path(f.name)

        try:
            report = _scanner.scan_file(tmp_path)
            assert any(f.rule_id == "S-08-NB-SYSTEM" for f in report.findings)
        finally:
            os.unlink(tmp_path)

    def test_notebook_pip_install(self):
        import tempfile
        import os

        nb_content = '{"cells":[{"cell_type":"code","source":["!pip install requests"]}]}'
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ipynb", delete=False, encoding="utf-8") as f:
            f.write(nb_content)
            tmp_path = Path(f.name)

        try:
            report = _scanner.scan_file(tmp_path)
            assert any(f.rule_id == "S-08-NB-PIP" for f in report.findings)
        finally:
            os.unlink(tmp_path)
