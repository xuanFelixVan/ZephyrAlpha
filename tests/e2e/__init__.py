"""E2E 测试共享夹具 — knowledge-base 全链路测试"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
