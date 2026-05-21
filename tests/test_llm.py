import pytest

from agents.llm import _extract_json, load_system_prompt


def test_extract_plain_object():
    assert _extract_json('{"a": 1}') == {"a": 1}


def test_extract_array_with_prefix():
    text = '여기 결과: [{"id":"x"}, {"id":"y"}] 입니다.'
    assert _extract_json(text) == [{"id": "x"}, {"id": "y"}]


def test_extract_fenced_json():
    text = "설명...\n```json\n{\"k\": [1,2,3]}\n```\n끝"
    assert _extract_json(text) == {"k": [1, 2, 3]}


def test_extract_handles_nested_braces_in_string():
    text = '{"a": "value with } brace"}'
    assert _extract_json(text) == {"a": "value with } brace"}


def test_extract_raises_when_no_json():
    with pytest.raises(ValueError):
        _extract_json("no json here at all")


def test_load_system_prompt_strips_frontmatter():
    body = load_system_prompt("researcher")
    assert "당신은 연구조사 보조원" in body
    assert "---" not in body.split("\n", 1)[0]  # 본문은 frontmatter 이후
