"""LLM client abstraction.

V1 ships a `MockLLMClient` so the demo runs without any API keys, plus an
`AnthropicClient` (pulled forward from the V3 roadmap) used by the evaluation
harness. OpenAI and other providers remain on the V3 roadmap.
"""
from __future__ import annotations

import json
import os
import re
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseLLMClient(ABC):
    """All LLM provider clients implement this interface."""

    name: str = "base"

    @abstractmethod
    def extract(self, prompt: str) -> str:  # pragma: no cover - interface
        """Return the model's raw textual response to `prompt`."""


_WORK_KEYWORDS_EN = (
    "engineer",
    "developer",
    "scientist",
    "manager",
    "intern",
    "analyst",
    "consultant",
    "director",
    "researcher",
    "designer",
    "officer",
    "lead",
    "google",
    "facebook",
    "meta",
    "amazon",
    "microsoft",
    "bytedance",
    "tiktok",
    "alibaba",
    "tencent",
    "tesla",
    "apple",
    "nvidia",
    "openai",
    "anthropic",
)
_WORK_KEYWORDS_ZH = (
    "工程师",
    "经理",
    "实习",
    "公司",
    "字节跳动",
    "腾讯",
    "阿里巴巴",
    "百度",
    "美团",
    "京东",
    "数据科学家",
    "工作",
    "任职",
    "负责",
    "团队",
)
_DEGREE_PATTERNS = [
    (re.compile(r"\bph\.?d\b|博士", re.IGNORECASE), "PhD"),
    (re.compile(r"\bmaster|\bm\.?s\b|\bm\.?sc\b|\bm\.?eng\b|硕士|研究生", re.IGNORECASE), "Master"),
    (re.compile(r"\bbachelor|\bb\.?s\b|\bb\.?a\b|\bbsc\b|\bbeng\b|本科|学士", re.IGNORECASE), "Bachelor"),
]
_YEAR_RANGE = re.compile(
    r"(?P<from>(?:19|20)\d{2}(?:[./年\-]\s?\d{1,2}\s?月?)?)\s*"
    r"(?:[-~–—至到]|to|until|—|present-?)\s*"
    r"(?P<to>(?:19|20)\d{2}(?:[./年\-]\s?\d{1,2}\s?月?)?|present|now|至今|今)",
    re.IGNORECASE,
)
_SINGLE_YEAR = re.compile(r"(?P<year>(?:19|20)\d{2})")


def _normalize_date(s: str) -> str:
    s = s.strip().lower()
    if s in {"present", "now", "至今", "今"}:
        return "present"
    # Convert "2018年9月" → "2018-09"; "2018/9" → "2018-09"; "2018.9" → "2018-09"
    m = re.match(r"^\s*(\d{4})\s*[./年-]?\s*(\d{1,2})?", s)
    if m:
        year = m.group(1)
        month = m.group(2)
        if month:
            return f"{year}-{int(month):02d}"
        return year
    return s


def _extract_dates(text: str) -> tuple[Optional[str], Optional[str]]:
    m = _YEAR_RANGE.search(text)
    if m:
        return _normalize_date(m.group("from")), _normalize_date(m.group("to"))
    years = _SINGLE_YEAR.findall(text)
    if len(years) >= 2:
        return years[0], years[1]
    if len(years) == 1:
        return years[0], None
    return None, None


def _extract_school(text: str) -> Optional[str]:
    # Chinese university suffixes
    m = re.search(r"([一-龥A-Za-z]{1,20}大学)", text)
    if m:
        return m.group(1)
    m = re.search(r"([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){0,3}\s+University)", text)
    if m:
        return m.group(1)
    m = re.search(r"(University\s+of\s+[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)?)", text)
    if m:
        return m.group(1)
    m = re.search(r"\b(MIT|Stanford|Harvard|Caltech|Yale|ETH Zurich|Princeton|Berkeley|UCLA|UCSD|CMU|NYU)\b", text)
    if m:
        return m.group(1)
    return None


def _extract_degree(text: str) -> Optional[str]:
    for pattern, label in _DEGREE_PATTERNS:
        if pattern.search(text):
            return label
    return None


def _looks_like_work(text: str) -> bool:
    lower = text.lower()
    if any(k in lower for k in _WORK_KEYWORDS_EN):
        # Avoid false positives where the person studied engineering but it
        # was actually education. If a degree keyword is also present, treat
        # it as education unless an explicit company / job-title signal wins.
        if _extract_degree(text) is None:
            return True
    if any(k in text for k in _WORK_KEYWORDS_ZH):
        if _extract_degree(text) is None:
            return True
    return False


def _try_parse_json_in_text(text: str) -> Optional[Dict[str, Any]]:
    """If the input itself contains a JSON object, parse it directly."""
    m = re.search(r"\{[^{}]*\}", text)
    if not m:
        return None
    try:
        data = json.loads(m.group(0))
    except (json.JSONDecodeError, ValueError):
        return None
    if isinstance(data, dict):
        return data
    return None


_MAJOR_HINTS_ZH = [
    "计算机科学与技术",
    "计算机科学",
    "软件工程",
    "电子工程",
    "电气工程",
    "机械工程",
    "国际经济与贸易",
    "数学",
    "物理",
    "化学",
    "生物",
    "统计",
    "金融",
    "经济",
    "管理",
]
_MAJOR_HINTS_EN = [
    "Computer Science",
    "Software Engineering",
    "Electrical Engineering",
    "Mechanical Engineering",
    "Computer Vision",
    "Data Science",
    "Statistics",
    "Mathematics",
    "Physics",
    "Chemistry",
    "Biology",
    "Finance",
    "Economics",
    "Management",
    "Search Infra",
    "Recommendation Systems",
]


def _extract_major_or_role(text: str) -> Optional[str]:
    for hint in _MAJOR_HINTS_ZH:
        if hint in text:
            return hint
    for hint in _MAJOR_HINTS_EN:
        if hint.lower() in text.lower():
            return hint
    # Generic role-like phrase
    m = re.search(r"\b(Senior\s+[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){0,2})", text)
    if m:
        return m.group(1)
    return None


def _heuristic_education_extraction(input_text: str) -> Dict[str, Any]:
    # If the row already contains a JSON dict, trust that as a partial source.
    embedded = _try_parse_json_in_text(input_text)
    if embedded:
        out = {
            "from": embedded.get("from"),
            "to": embedded.get("to"),
            "school": embedded.get("school"),
            "major": embedded.get("major"),
            "scholar": embedded.get("degree") or embedded.get("scholar"),
            "is_work_experience": False,
        }
        return out

    frm, to = _extract_dates(input_text)
    school = _extract_school(input_text)
    degree = _extract_degree(input_text)
    major_or_role = _extract_major_or_role(input_text)
    is_work = _looks_like_work(input_text)

    return {
        "from": frm,
        "to": to,
        "school": school,
        "major": major_or_role,
        "scholar": degree,
        "is_work_experience": is_work,
    }


def _extract_input_text_from_prompt(prompt: str) -> str:
    """Pull the row's input text out of the structured prompt."""
    marker = "Input text:"
    if marker not in prompt:
        return prompt
    after = prompt.split(marker, 1)[1]
    # Stop at the trailing JSON-only directive.
    after = after.split("Respond with ONE JSON object", 1)[0]
    return after.strip()


class MockLLMClient(BaseLLMClient):
    """A heuristic-based LLM stand-in. Deterministic, no network calls.

    For the V1 Education Experience Cleaner template, it inspects the input text
    embedded in the prompt and returns a JSON object with the expected fields.
    The output is realistic enough that the full demo flow produces meaningful
    extracted data on the bundled sample CSV.
    """

    name = "mock"

    def extract(self, prompt: str) -> str:
        input_text = _extract_input_text_from_prompt(prompt)
        archive_reason = _archive_check(input_text)
        if archive_reason is not None:
            return json.dumps({"_unprocessable": True, "reason": archive_reason}, ensure_ascii=False)
        # Detect Education Experience Cleaner via the prompt's field schema.
        if (
            "is_work_experience" in prompt
            and "school" in prompt
            and "scholar" in prompt
        ):
            payload = _heuristic_education_extraction(input_text)
            return json.dumps(payload, ensure_ascii=False)
        # Fallback for unknown schemas: echo an empty JSON object.
        return "{}"


_PUNCT_ONLY = re.compile(r"^[\W_]+$", re.UNICODE)
_GARBAGE_PHRASES = {
    "n/a", "na", "tbd", "tbc", "无", "暂无", "缺失", "缺", "未知",
    "null", "undefined", "none",
    "lorem ipsum", "hello world", "你好世界", "今天天气真好",
    "see resume", "see attached", "见附件",
    "no info", "no record", "data_loss", "data loss", "redacted",
    "[redacted]", "<no record>",
}
_GARBAGE_PREFIXES = (
    "[error]", "[fatal]", "[debug]", "[info]", "[warn]",
)


def _archive_check(text: str) -> Optional[str]:
    """Cheap heuristic for the MockLLMClient: spot obviously unprocessable rows.

    The real model makes a smarter judgement on its own based on the prompt
    rule. This is only used so the offline demo can still demonstrate the
    archive flow.
    """
    stripped = text.strip()
    if not stripped:
        return "empty input"
    lower = stripped.lower()
    if lower in _GARBAGE_PHRASES:
        return f"placeholder phrase: {stripped!r}"
    if any(lower.startswith(p) for p in _GARBAGE_PREFIXES):
        return "looks like a log line, not a record"
    if len(stripped) <= 2 and not re.search(r"\d", stripped):
        return "input too short to be a record"
    if _PUNCT_ONLY.match(stripped) and not re.search(r"[一-鿿A-Za-z0-9]", stripped):
        return "input is punctuation only"
    if stripped.isdigit() and len(stripped) < 4:
        return "input is just a small number"
    # Single character repeated many times: "****", "————", "##########"
    if len(stripped) >= 3 and len(set(stripped)) == 1:
        return "input is a repeated single character"
    # No letters or CJK characters at all → unlikely to be a record
    if not re.search(r"[A-Za-z一-鿿]", stripped):
        return "input has no letters or CJK characters"
    return None


class AnthropicClient(BaseLLMClient):
    """Real LLM client backed by Anthropic's Messages API.

    Pulled forward from the V3 roadmap so the evaluation harness can compare
    Mock heuristics against a production-quality model. The `BaseLLMClient`
    interface is intentionally untouched.
    """

    name = "anthropic"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-6",
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> None:
        # Defer the import so a missing `anthropic` package only breaks users
        # who actually opt into this provider.
        try:
            from anthropic import Anthropic
        except ImportError as e:
            raise RuntimeError(
                "The `anthropic` package is required to use AnthropicClient. "
                "Install with: pip install anthropic"
            ) from e

        resolved_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not resolved_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY is not set. Provide it via .env or environment."
            )
        self._client = Anthropic(api_key=resolved_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def extract(self, prompt: str) -> str:
        msg = self._client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        parts: list[str] = []
        for block in msg.content:
            if getattr(block, "type", None) == "text":
                parts.append(block.text)
        return "".join(parts)


def get_llm_client(provider: str, **kwargs: Any) -> BaseLLMClient:
    """Resolve a provider name to an LLM client instance.

    V1 supports `mock` and `anthropic`. OpenAI and others are planned for V3.
    """
    provider_key = (provider or "mock").lower()
    if provider_key == "mock":
        return MockLLMClient()
    if provider_key == "anthropic":
        return AnthropicClient(**kwargs)
    raise NotImplementedError(
        f"LLM provider '{provider}' is not implemented yet. "
        f"`mock` and `anthropic` are supported; OpenAI is on the V3 roadmap."
    )
