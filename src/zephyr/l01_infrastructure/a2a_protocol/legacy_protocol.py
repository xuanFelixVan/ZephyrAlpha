# [BLUEPRINT] MOD-INF-025 | docs/03_modules/l01_infrastructure/a2a-protocol/blueprint.md | §3

# [MODULE] zephyr.l01_infrastructure.a2a_protocol.legacy_protocol

# [INVARIANTS] MessageType 枚举不可扩展; A2ACommunication 接口签名不可变

# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/a2a-protocol/blueprint.md

# [CONSUMERS] zephyr.l01_infrastructure.a2a_protocol

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 异常必须包含 agent_id 和 protocol_layer

# [TESTS] tests/test_a2a_protocol.py

"""[BLUEPRINT] MOD-INF-025 | docs/03_modules/l01_infrastructure/a2a-protocol/blueprint.md | §3

G-CT-008 — A2ACommunication Pydantic V2 BaseModel agent-to-agent 通信数据结构.

"""


from __future__ import annotations





from datetime import datetime, timezone


from enum import Enum





from pydantic import BaseModel, Field








class MessageType(str, Enum):


    QUERY = "QUERY"


    COMMAND = "COMMAND"


    NOTIFY = "NOTIFY"


    DELEGATE = "DELEGATE"


    RESPONSE = "RESPONSE"








class A2ACommunication(BaseModel):


    a2a_id: str


    from_agent_id: str


    to_agent_id: str


    message_type: MessageType = MessageType.QUERY


    payload_size: int = 0


    transfer_token_count: int = 0


    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


    status: str = "PENDING"


