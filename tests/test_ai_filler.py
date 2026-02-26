import pytest
from phasecompiler.ai_filler import (
    _strip_code_fences,
    _build_prior_phases_summary,
)


class TestStripCodeFences:
    """Test markdown code fence removal."""

    def test_strip_json_code_fence(self):
        """Test removing JSON code fence."""
        text = '```json\n{"key": "value"}\n```'
        result = _strip_code_fences(text)
        assert result == '{"key": "value"}'

    def test_strip_generic_code_fence(self):
        """Test removing generic code fence."""
        text = "```\nsome code\n```"
        result = _strip_code_fences(text)
        assert result == "some code"

    def test_plain_text_no_fences(self):
        """Test plain text without fences."""
        text = '{"key": "value"}'
        result = _strip_code_fences(text)
        assert result == '{"key": "value"}'

    def test_whitespace_handling(self):
        """Test whitespace is trimmed properly."""
        text = "  ```\ncode\n```  "
        result = _strip_code_fences(text)
        assert result == "code"

    def test_multiline_content(self):
        """Test multiline content in code fence."""
        text = "```\nline1\nline2\nline3\n```"
        result = _strip_code_fences(text)
        assert result == "line1\nline2\nline3"


class TestPriorPhasesSummary:
    """Test prior phases summary generation."""

    def test_empty_phases(self):
        """Test summary with no completed phases."""
        result = _build_prior_phases_summary([])
        assert result == "None yet."

    def test_single_phase(self):
        """Test summary with one phase."""
        phases = [{"id": 1, "deliverable": "Backend API"}]
        result = _build_prior_phases_summary(phases)
        assert "Phase 1: Backend API" in result

    def test_multiple_phases(self):
        """Test summary with multiple phases."""
        phases = [
            {"id": 1, "deliverable": "Backend API"},
            {"id": 2, "deliverable": "Frontend UI"},
            {"id": 3, "deliverable": "Database"},
        ]
        result = _build_prior_phases_summary(phases)
        assert "Phase 1: Backend API" in result
        assert "Phase 2: Frontend UI" in result
        assert "Phase 3: Database" in result

    def test_format_consistency(self):
        """Test format is consistent."""
        phases = [
            {"id": 1, "deliverable": "Setup"},
            {"id": 2, "deliverable": "Build"},
        ]
        result = _build_prior_phases_summary(phases)
        lines = result.strip().split("\n")
        assert len(lines) == 2
        for line in lines:
            assert "Phase" in line
            assert ":" in line
