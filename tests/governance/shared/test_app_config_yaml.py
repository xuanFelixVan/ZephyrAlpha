# [A_test] module_id: SRC-TST-1974 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-591 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_app_config_yaml
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""l01 infrastructure config.load_config — YAML + 环境变量覆盖。"""


from pathlib import Path

import pytest
import yaml

from zephyr.gov_code_quality.code_dedup.config import AppConfig, load_config, reload_config


def test_load_config_default_when_missing_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, caplog) -> None:
    monkeypatch.chdir(tmp_path)
    caplog.set_level("WARNING")
    c = load_config(env_override=False)
    assert isinstance(c, AppConfig)
    assert c.env == "dev"
    assert "未找到 YAML" in caplog.text


def test_load_config_from_yaml_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir()
    payload = {"env": "staging", "log_level": "DEBUG", "data_source_priority": ["a", "b"]}
    (cfg_dir / "zephyr_app.yaml").write_text(yaml.safe_dump(payload), encoding="utf-8")
    c = load_config(env_override=False)
    assert c.env == "staging"
    assert c.log_level == "DEBUG"
    assert c.data_source_priority == ("a", "b")


def test_env_overrides_yaml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir()
    (cfg_dir / "app.yaml").write_text(
        yaml.safe_dump({"env": "dev", "log_level": "INFO"}),
        encoding="utf-8",
    )
    monkeypatch.setenv("ZEPHYR_ENV", "prod")
    monkeypatch.setenv("ZEPHYR_LOG_LEVEL", "ERROR")
    c = load_config(env_override=True)
    assert c.env == "prod"
    assert c.log_level == "ERROR"


def test_reload_config_uses_last_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir()
    p = cfg_dir / "zephyr_app.yaml"
    p.write_text(yaml.safe_dump({"env": "v1"}), encoding="utf-8")
    assert load_config(env_override=False).env == "v1"
    p.write_text(yaml.safe_dump({"env": "v2"}), encoding="utf-8")
    assert reload_config(env_override=False).env == "v2"
