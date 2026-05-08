---
module_id: KE-module_blu-dx-000
title: === 开发者体验 (DX) ===
category: module_blueprint
---

# === 开发者体验 (DX) ===

=== 开发者体验 (DX) ===

class PipelineCLICommand(BaseModel):
    model_config = ConfigDict(frozen=True)

    command_name: str
    subcommands: list[str] = Field(default_factory=list)
    flags: dict[str, str] = Field(default_factory=dict)
    description: str
    example: str


class CLIOutput(BaseModel):
    model_config = ConfigDict(frozen=True)

    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    rich_output: str = ""
