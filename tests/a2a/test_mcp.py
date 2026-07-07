# [A_test] module_id: SRC-TST-1249 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-013 | docs/03_modules/_cross_layer/model_context_protocol_servers/blueprint.md | §test
# [MODULE] zephyr.infrastructure.a2a_protocol.governance
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_mcp.py
# [TTL] task_bound

import json
from io import StringIO

import pytest

base_mod = pytest.importorskip("zephyr.integration.mcp._base_server", reason="mcp._base_server not available")
BaseMCPServer = base_mod.BaseMCPServer
ToolDefinition = base_mod.ToolDefinition
MCPError = base_mod.MCPError
ERR_PARSE_ERROR = base_mod.ERR_PARSE_ERROR
ERR_INVALID_REQUEST = base_mod.ERR_INVALID_REQUEST
ERR_METHOD_NOT_FOUND = base_mod.ERR_METHOD_NOT_FOUND
ERR_INVALID_PARAMS = base_mod.ERR_INVALID_PARAMS
ERR_INTERNAL_ERROR = base_mod.ERR_INTERNAL_ERROR
ERR_TOOL_NOT_FOUND = base_mod.ERR_TOOL_NOT_FOUND
ERR_TOOL_EXECUTION = base_mod.ERR_TOOL_EXECUTION
ERR_GATE_FAILED = base_mod.ERR_GATE_FAILED
ERR_RBAC_DENIED = base_mod.ERR_RBAC_DENIED

ec_mod = pytest.importorskip("zephyr.integration.mcp.error_codes", reason="mcp.error_codes not available")
error_message = ec_mod.error_message
lookup = ec_mod.lookup


class TestErrorCodes:
    def test_standard_jsonrpc_codes(self):
        assert ERR_PARSE_ERROR == -32700
        assert ERR_INVALID_REQUEST == -32600
        assert ERR_METHOD_NOT_FOUND == -32601
        assert ERR_INVALID_PARAMS == -32602
        assert ERR_INTERNAL_ERROR == -32603

    def test_mcp_extension_codes(self):
        assert ERR_TOOL_NOT_FOUND == -32001
        assert ERR_TOOL_EXECUTION == -32002
        assert ERR_GATE_FAILED == -32003
        assert ERR_RBAC_DENIED == -32004

    def test_error_message_known_code(self):
        assert error_message(ERR_PARSE_ERROR) == "Parse error"
        assert error_message(ERR_TOOL_NOT_FOUND) == "Tool not found"

    def test_error_message_unknown_code(self):
        msg = error_message(99999)
        assert "Unknown" in msg or "99999" in msg

    def test_lookup_known_code(self):
        assert lookup(ERR_METHOD_NOT_FOUND) == "Method not found"

    def test_lookup_unknown_code(self):
        result = lookup(99999)
        assert "UNKNOWN" in result


class TestMCPError:
    def test_creation(self):
        err = MCPError(code=-32001, message="Tool not found")
        assert err.code == -32001
        assert err.message == "Tool not found"
        assert err.data is None

    def test_with_data(self):
        err = MCPError(code=-32002, message="Execution error", data={"detail": "timeout"})
        assert err.data == {"detail": "timeout"}

    def test_is_exception(self):
        assert issubclass(MCPError, Exception)

    def test_str_representation(self):
        err = MCPError(code=-32001, message="Tool not found")
        assert "Tool not found" in str(err)


class TestToolDefinition:
    def test_creation(self):
        def handler(x: str) -> dict:
            return {"result": x}

        td = ToolDefinition(
            name="test.tool",
            description="A test tool",
            input_schema={"type": "object", "properties": {"x": {"type": "string"}}},
            handler=handler,
        )
        assert td.name == "test.tool"
        assert td.description == "A test tool"
        assert td.safety_level == "L"

    def test_custom_safety_level(self):
        def handler() -> dict:
            return {}

        td = ToolDefinition(
            name="test.tool",
            description="test",
            input_schema={"type": "object"},
            handler=handler,
            safety_level="H",
        )
        assert td.safety_level == "H"


class TestBaseMCPServer:
    def test_creation(self):
        server = BaseMCPServer("test_server", "1.0.0", "Test MCP server", enable_rbac=False)
        assert server.server_id == "test_server"
        assert server.version == "1.0.0"
        assert server.description == "Test MCP server"

    def test_register_tool(self):
        server = BaseMCPServer("test_server", "1.0.0", "Test", enable_rbac=False)

        def my_handler(arg: str) -> dict:
            return {"result": arg}

        server.register_tool(
            name="test_server.echo",
            description="Echo tool",
            input_schema={"type": "object", "properties": {"arg": {"type": "string"}}},
            handler=my_handler,
        )
        assert "test_server.echo" in server.tool_names

    def test_tool_names_empty(self):
        server = BaseMCPServer("test_server", "1.0.0", "Test", enable_rbac=False)
        assert server.tool_names == []

    def test_tool_names_multiple(self):
        server = BaseMCPServer("test_server", "1.0.0", "Test", enable_rbac=False)
        server.register_tool("t1", "Tool 1", {"type": "object"}, lambda: {})
        server.register_tool("t2", "Tool 2", {"type": "object"}, lambda: {})
        assert len(server.tool_names) == 2
        assert "t1" in server.tool_names
        assert "t2" in server.tool_names

    def test_handle_initialize(self):
        server = BaseMCPServer("test_server", "1.0.0", "Test", enable_rbac=False)
        resp = server.handle_request({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
        assert resp["id"] == 1
        assert "result" in resp
        assert resp["result"]["serverInfo"]["name"] == "test_server"
        assert resp["result"]["protocolVersion"] == "2024-11-05"

    def test_handle_ping(self):
        server = BaseMCPServer("test_server", "1.0.0", "Test", enable_rbac=False)
        resp = server.handle_request({"jsonrpc": "2.0", "id": 2, "method": "ping"})
        assert resp["result"] == {"pong": True}

    def test_handle_tools_list(self):
        server = BaseMCPServer("test_server", "1.0.0", "Test", enable_rbac=False)
        server.register_tool("t1", "Tool 1", {"type": "object"}, lambda: {})
        resp = server.handle_request({"jsonrpc": "2.0", "id": 3, "method": "tools/list"})
        assert "result" in resp
        assert len(resp["result"]["tools"]) == 1
        assert resp["result"]["tools"][0]["name"] == "t1"

    def test_handle_tools_call_success(self):
        server = BaseMCPServer("test_server", "1.0.0", "Test", enable_rbac=False)

        def echo(msg: str) -> dict:
            return {"echo": msg}

        server.register_tool(
            "test_server.echo",
            "Echo",
            {"type": "object", "properties": {"msg": {"type": "string"}}},
            echo,
        )
        resp = server.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {"name": "test_server.echo", "arguments": {"msg": "hello"}},
            }
        )
        assert "result" in resp
        content = resp["result"]["content"]
        parsed = json.loads(content[0]["text"])
        assert parsed["echo"] == "hello"

    def test_handle_tools_call_not_found(self):
        server = BaseMCPServer("test_server", "1.0.0", "Test", enable_rbac=False)
        resp = server.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {"name": "nonexistent"},
            }
        )
        assert "error" in resp
        assert resp["error"]["code"] == ERR_TOOL_NOT_FOUND

    def test_handle_tools_call_invalid_params(self):
        server = BaseMCPServer("test_server", "1.0.0", "Test", enable_rbac=False)

        def strict_handler(required_arg: str) -> dict:
            return {"result": required_arg}

        server.register_tool(
            "test_server.strict",
            "Strict",
            {"type": "object", "properties": {"required_arg": {"type": "string"}}},
            strict_handler,
        )
        resp = server.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 6,
                "method": "tools/call",
                "params": {"name": "test_server.strict", "arguments": {"wrong_arg": "value"}},
            }
        )
        assert "error" in resp
        assert resp["error"]["code"] == ERR_INVALID_PARAMS

    def test_handle_tools_call_safety_high(self):
        server = BaseMCPServer("test_server", "1.0.0", "Test", enable_rbac=False)
        server.register_tool(
            "test_server.dangerous",
            "Dangerous",
            {"type": "object"},
            lambda: {},
            safety_level="H",
        )
        resp = server.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 7,
                "method": "tools/call",
                "params": {"name": "test_server.dangerous"},
            }
        )
        assert "error" in resp
        assert resp["error"]["code"] == ERR_RBAC_DENIED

    def test_handle_tools_call_safety_medium(self):
        server = BaseMCPServer("test_server", "1.0.0", "Test", enable_rbac=False)
        server.register_tool(
            "test_server.confirm",
            "Confirm",
            {"type": "object"},
            lambda: {},
            safety_level="M",
        )
        resp = server.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 8,
                "method": "tools/call",
                "params": {"name": "test_server.confirm"},
            }
        )
        assert "result" in resp
        content = resp["result"]["content"]
        parsed = json.loads(content[0]["text"])
        assert parsed["confirmation_required"] is True

    def test_handle_tools_call_mcp_error(self):
        server = BaseMCPServer("test_server", "1.0.0", "Test", enable_rbac=False)

        def failing_handler() -> None:
            raise MCPError(code=ERR_GATE_FAILED, message="Gate check failed")

        server.register_tool("test_server.fail", "Fail", {"type": "object"}, failing_handler)
        resp = server.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 9,
                "method": "tools/call",
                "params": {"name": "test_server.fail"},
            }
        )
        assert "error" in resp
        assert resp["error"]["code"] == ERR_GATE_FAILED

    def test_handle_tools_call_generic_exception(self):
        server = BaseMCPServer("test_server", "1.0.0", "Test", enable_rbac=False)

        def crash_handler() -> None:
            raise RuntimeError("unexpected crash")

        server.register_tool("test_server.crash", "Crash", {"type": "object"}, crash_handler)
        resp = server.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 10,
                "method": "tools/call",
                "params": {"name": "test_server.crash"},
            }
        )
        assert "error" in resp
        assert resp["error"]["code"] == ERR_TOOL_EXECUTION

    def test_handle_unknown_method(self):
        server = BaseMCPServer("test_server", "1.0.0", "Test", enable_rbac=False)
        resp = server.handle_request({"jsonrpc": "2.0", "id": 11, "method": "unknown/method"})
        assert "error" in resp
        assert resp["error"]["code"] == ERR_METHOD_NOT_FOUND

    def test_run_with_stringio(self):
        server = BaseMCPServer("test_server", "1.0.0", "Test", enable_rbac=False)
        inp = StringIO('{"jsonrpc":"2.0","id":1,"method":"ping"}\n')
        out = StringIO()
        server.run(input_stream=inp, output_stream=out)
        out.seek(0)
        response = json.loads(out.read().strip())
        assert response["result"] == {"pong": True}

    def test_run_with_invalid_json(self):
        server = BaseMCPServer("test_server", "1.0.0", "Test", enable_rbac=False)
        inp = StringIO("not json\n")
        out = StringIO()
        server.run(input_stream=inp, output_stream=out)
        out.seek(0)
        response = json.loads(out.read().strip())
        assert "error" in response
        assert response["error"]["code"] == ERR_PARSE_ERROR

    def test_run_with_non_object_json(self):
        server = BaseMCPServer("test_server", "1.0.0", "Test", enable_rbac=False)
        inp = StringIO("[1,2,3]\n")
        out = StringIO()
        server.run(input_stream=inp, output_stream=out)
        out.seek(0)
        response = json.loads(out.read().strip())
        assert "error" in response
        assert response["error"]["code"] == ERR_INVALID_REQUEST

    def test_ok_response_format(self):
        server = BaseMCPServer("test_server", "1.0.0", "Test", enable_rbac=False)
        resp = server._ok(42, {"data": "value"})
        assert resp["jsonrpc"] == "2.0"
        assert resp["id"] == 42
        assert resp["result"] == {"data": "value"}

    def test_err_response_format(self):
        server = BaseMCPServer("test_server", "1.0.0", "Test", enable_rbac=False)
        resp = server._err(42, -32001, "not found", {"detail": "x"})
        assert resp["jsonrpc"] == "2.0"
        assert resp["id"] == 42
        assert resp["error"]["code"] == -32001
        assert resp["error"]["data"] == {"detail": "x"}

    def test_err_response_no_data(self):
        server = BaseMCPServer("test_server", "1.0.0", "Test", enable_rbac=False)
        resp = server._err(42, -32001, "not found")
        assert "data" not in resp["error"]

    def test_disable_rbac(self):
        server = BaseMCPServer("test_server", "1.0.0", "Test", enable_rbac=False)
        server.disable_rbac()
        assert server._rbac_guard is None

    def test_register_tool_decorator(self):
        class MyServer(BaseMCPServer):
            def __init__(self):
                super().__init__("my_server", "1.0.0", "Test", enable_rbac=False)

            @BaseMCPServer.register_tool_decorator(
                name="my_server.hello",
                description="Say hello",
                input_schema={"type": "object", "properties": {}},
            )
            def hello(self):
                return {"message": "hello"}

        server = MyServer()
        server._install_decorated_tools()
        assert "my_server.hello" in server.tool_names

    def test_content_length_read(self):
        body = '{"jsonrpc":"2.0","id":1,"method":"ping"}'
        cl_header = f"Content-Length: {len(body)}\r\n\r\n"
        inp = StringIO(cl_header + body)
        result, used_cl = BaseMCPServer._read_message(inp)
        assert used_cl is True
        assert result == body

    def test_legacy_line_read(self):
        line = '{"jsonrpc":"2.0","id":1,"method":"ping"}'
        inp = StringIO(line + "\n")
        result, used_cl = BaseMCPServer._read_message(inp)
        assert used_cl is False
        assert result == line

    def test_read_message_eof(self):
        inp = StringIO("")
        result, used_cl = BaseMCPServer._read_message(inp)
        assert result is None
