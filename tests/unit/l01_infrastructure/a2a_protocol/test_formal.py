"""测试: FormalVerification"""

from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.a2a_formal_verification import (
    A2AFormalVerification,
    VerificationReport,
    VerificationStatus,
)


def test_verify_default_graph():
    fv = A2AFormalVerification()
    report = fv.verify()
    assert isinstance(report, VerificationReport)
    assert report.verified


def test_verify_with_deadlock():
    graph = {
        "QUEUED": ["ASSIGNED"],
        "ASSIGNED": ["IN_PROGRESS"],
        "IN_PROGRESS": ["BLOCKED"],
        "BLOCKED": ["IN_PROGRESS"],
        "FAILED": [],
        "COMPLETED": [],
    }
    fv = A2AFormalVerification(state_graph=graph)
    report = fv.verify()
    assert not report.verified


def test_verify_no_terminal_states():
    graph = {
        "QUEUED": ["ASSIGNED"],
        "ASSIGNED": ["IN_PROGRESS"],
        "IN_PROGRESS": ["BLOCKED"],
        "BLOCKED": ["IN_PROGRESS"],
    }
    fv = A2AFormalVerification(state_graph=graph)
    report = fv.verify()
    assert not report.verified


def test_violation_count():
    graph = {
        "QUEUED": ["ASSIGNED"],
        "ASSIGNED": ["IN_PROGRESS"],
        "IN_PROGRESS": [],
    }
    fv = A2AFormalVerification(state_graph=graph)
    report = fv.verify()
    assert report.violation_count > 0
