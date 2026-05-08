#!/bin/bash
# MOD-INF-022 Sandbox Wrapper - v0.14.0
export ESCALATION_SANDBOX_MODE=true
exec "$@"
