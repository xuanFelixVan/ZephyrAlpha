"""schema subsystem — 遥测 Schema 版本追踪（最小可用骨架）."""


class SchemaSubsystem:
    def __init__(self, module_id: str, test_mode: bool = False):
        self._module_id = module_id
        self._test_mode = test_mode
        self._current_version = "0.9.0"

    def get_version(self) -> str:
        return self._current_version

    def check_compatibility(self, module_version: str) -> bool:
        return module_version == self._current_version

    def register_schema(self, schema_name: str, version: str) -> None:
        pass
