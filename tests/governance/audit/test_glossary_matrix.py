# [A_test] module_id: SRC-TST-1059 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_glossary_matrix
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_audit.glossary_matrix import (
    GLOSSARY,
    GLOSSARY_COUNT,
    GlossaryEntry,
    list_terms,
    lookup,
)


class TestGlossaryEntry:
    def test_create_entry(self):
        entry = GlossaryEntry(term="Alpha", definition="test", domain="quant")
        assert entry.term == "Alpha"
        assert entry.definition == "test"
        assert entry.domain == "quant"
        assert entry.acronym == ""

    def test_entry_with_acronym(self):
        entry = GlossaryEntry(term="Alpha", definition="test", domain="quant", acronym="α")
        assert entry.acronym == "α"


class TestLookup:
    def test_existing_term(self):
        result = lookup("Alpha")
        assert result is not None
        assert result.term == "Alpha"
        assert result.domain == "量化"

    def test_nonexistent_term(self):
        result = lookup("NONEXISTENT")
        assert result is None

    def test_empty_string(self):
        result = lookup("")
        assert result is None

    def test_case_sensitive(self):
        result = lookup("alpha")
        assert result is None

    def test_dma_lookup(self):
        result = lookup("DMA")
        assert result is not None
        assert "Direct Market Access" in result.definition


class TestListTerms:
    def test_returns_sorted_list(self):
        terms = list_terms()
        assert terms == sorted(terms)

    def test_includes_known_terms(self):
        terms = list_terms()
        assert "Alpha" in terms
        assert "DMA" in terms
        assert "HFT" in terms

    def test_count_matches(self):
        terms = list_terms()
        assert len(terms) == GLOSSARY_COUNT


class TestGlossaryData:
    def test_all_entries_are_glossary_entry(self):
        for key, entry in GLOSSARY.items():
            assert isinstance(entry, GlossaryEntry)
            assert entry.term == key

    def test_glossary_count_positive(self):
        assert GLOSSARY_COUNT > 0
