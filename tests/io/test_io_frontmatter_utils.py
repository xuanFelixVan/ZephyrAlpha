# [A_test] module_id: SRC-TST-1153 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §testing

# [MODULE] tests.test_io_frontmatter_utils

# [INVARIANTS] parse_frontmatter严格---边界;extract_body跳过frontmatter;YAML错误返回None

# [MODIFY-GUARD] frontmatter_utils.py变更时同步更新

# [CONSUMERS] CI

# [STABILITY] stable

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 无

# [TESTS] pytest tests/test_io_frontmatter_utils.py -q
# [TTL] task_bound

from zephyr.shared.io.frontmatter_utils import (
    extract_body,
    parse_frontmatter,
    parse_frontmatter_from_file,
    parse_yaml_header,
)


class TestParseFrontmatter:
    def test_valid_frontmatter(self):
        content = "---\ntitle: Hello\nversion: 1.0\n---\nBody text"
        result = parse_frontmatter(content)
        assert result is not None
        assert result["title"] == "Hello"
        assert result["version"] == 1.0

    def test_no_frontmatter(self):
        content = "Just body text"
        result = parse_frontmatter(content)
        assert result is None

    def test_unclosed_frontmatter(self):
        content = "---\ntitle: Hello\nBody text"
        result = parse_frontmatter(content)
        assert result is None

    def test_empty_frontmatter(self):
        content = "---\n---\nBody"
        result = parse_frontmatter(content)
        assert result is None

    def test_invalid_yaml(self):
        content = "---\n: invalid yaml [\n---\nBody"
        result = parse_frontmatter(content)
        assert result is None

    def test_multiline_values(self):
        content = "---\ntitle: Test\ndescription: |\n  Line 1\n  Line 2\n---\nBody"
        result = parse_frontmatter(content)
        assert result is not None
        assert "Line 1" in result["description"]

    def test_string_field(self):
        content = '---\ntitle: "Hello World"\n---\nBody'
        result = parse_frontmatter(content)
        assert result["title"] == "Hello World"


class TestParseFrontmatterFromFile:
    def test_valid_file(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("---\ntitle: File Test\n---\nBody", encoding="utf-8")
        result = parse_frontmatter_from_file(f)
        assert result is not None
        assert result["title"] == "File Test"

    def test_nonexistent_file(self, tmp_path):
        result = parse_frontmatter_from_file(tmp_path / "missing.md")
        assert result is None

    def test_no_frontmatter_file(self, tmp_path):
        f = tmp_path / "plain.md"
        f.write_text("Just text", encoding="utf-8")
        result = parse_frontmatter_from_file(f)
        assert result is None


class TestParseYamlHeader:
    def test_valid_yaml(self):
        content = "key1: value1\nkey2: 42\n"
        result = parse_yaml_header(content)
        assert result is not None
        assert result["key1"] == "value1"
        assert result["key2"] == 42

    def test_invalid_yaml(self):
        content = ": [invalid"
        result = parse_yaml_header(content)
        assert result is None

    def test_non_dict_yaml(self):
        content = "- item1\n- item2\n"
        result = parse_yaml_header(content)
        assert result is None

    def test_empty_yaml(self):
        result = parse_yaml_header("")
        assert result is None


class TestExtractBody:
    def test_with_frontmatter(self):
        content = "---\ntitle: Test\n---\nBody text here"
        result = extract_body(content)
        assert result == "Body text here"

    def test_without_frontmatter(self):
        content = "Just body text"
        result = extract_body(content)
        assert result == content

    def test_unclosed_frontmatter(self):
        content = "---\ntitle: Test\nBody text"
        result = extract_body(content)
        assert result == content

    def test_multiline_body(self):
        content = "---\ntitle: Test\n---\nLine 1\nLine 2\n"
        result = extract_body(content)
        assert "Line 1" in result
        assert "Line 2" in result
