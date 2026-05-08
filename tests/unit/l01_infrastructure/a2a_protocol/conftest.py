import pytest
from pathlib import Path


@pytest.fixture
def a2a_protocol_root():
    return Path(__file__).resolve().parent.parent.parent.parent.parent / "src" / "zephyr" / "l01_infrastructure" / "a2a_protocol"


@pytest.fixture
def blueprint_path():
    return Path(__file__).resolve().parent.parent.parent.parent.parent / "docs" / "03_modules" / "l01_infrastructure" / "a2a-protocol" / "blueprint.md"
