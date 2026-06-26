---
module_id: KE-2908
status: active
title: === SQLite 完整性 ===
category: module_blueprint
ttl: permanent
---

# === SQLite 完整性 ===

=== SQLite 完整性 ===

class SQLiteIntegrityReport(BaseModel):
    """SQLite 完整性检查报告（B436）"""
    model_config = ConfigDict(frozen=True)

    report_id: UUID = Field(default_factory=uuid4)
    check_type: Literal["integrity_check", "quick_check", "checksum_verify", "backup_verify"]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    database_path: str
    result: Literal["ok", "error", "corrupt"]
    error_details: Optional[str] = None
    corrupted_pages: list[int] = Field(default_factory=list)

    checksum_sha256: Optional[str] = None
    previous_checksum_sha256: Optional[str] = None
    checksum_match: Optional[bool] = None

    automatic_recovery_attempted: bool = False
    recovery_success: Optional[bool] = None
    backup_path: Optional[str] = None

    next_scheduled_check: Optional[datetime] = None
