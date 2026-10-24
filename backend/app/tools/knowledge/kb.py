import math
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).resolve().parents[2] / "knowledge"
_WORD = re.compile(r"[a-z0-9]+")
# Words that appear in nearly every section and only add noise to the ranking.
_STOPWORDS = {
    "the", "and", "for", "you", "your", "are", "with", "that", "this", "what", "how", "can",
    "from", "our", "into", "not", "who", "when", "which", "they", "their",
}  # fmt: skip
# BM25 parameters (standard defaults) and how much a title match outweighs a body match.
_K1, _B, _TITLE_WEIGHT = 1.5, 0.75, 3


def _stem(word: str) -> str:
    """Fold plurals so "industries" matches "industry" and "agents" matches "agent"."""
    if word.endswith("ies") and len(word) > 4:
        return word[:-3] + "y"
    if word.endswith("s") and not word.endswith("ss") and len(word) > 3:
        return word[:-1]
    return word


def _tokens(text: str) -> list[str]:
    words = _WORD.findall(text.lower())
    return [_stem(w) for w in words if len(w) > 2 and w not in _STOPWORDS]


@dataclass(frozen=True)
class Section:
    source: str
    title: str
    body: str
    terms: Counter[str] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        terms = Counter(_tokens(self.body))
        for word in _tokens(self.title):
            terms[word] += _TITLE_WEIGHT
        object.__setattr__(self, "terms", terms)

    @property
    def length(self) -> int:
        return sum(self.terms.values())

    def render(self) -> str:
        return f"[{self.source} › {self.title}]\n{self.body.strip()}"


class KnowledgeBase:
    """Markdown files split by `## ` headings, ranked with BM25 (title words weigh more).

    Still keyword search: simple and debuggable; swap for pgvector if the KB grows (see plan.md).
    """

    def __init__(self, directory: Path = KNOWLEDGE_DIR) -> None:
        self.sections = [s for path in sorted(directory.glob("*.md")) for s in self._split(path)]
        doc_freq = Counter(word for s in self.sections for word in s.terms)
        n = len(self.sections)
        self._idf = {w: math.log(1 + (n - df + 0.5) / (df + 0.5)) for w, df in doc_freq.items()}
        self._avg_len = sum(s.length for s in self.sections) / n if n else 0.0

    @staticmethod
    def _split(path: Path) -> list[Section]:
        parts = re.split(r"^## ", path.read_text(), flags=re.MULTILINE)
        sections = []
        for part in parts[1:]:
            title, _, body = part.partition("\n")
            sections.append(Section(source=path.stem, title=title.strip(), body=body))
        return sections

    def _score(self, query: set[str], section: Section) -> float:
        norm = _K1 * (1 - _B + _B * section.length / self._avg_len)
        score = 0.0
        for word in query:
            tf = section.terms.get(word, 0)
            if tf:
                score += self._idf[word] * tf * (_K1 + 1) / (tf + norm)
        return score

    def search(self, query: str, k: int = 3) -> list[Section]:
        q = set(_tokens(query))
        scored = [(self._score(q, s), s) for s in self.sections]
        return [s for score, s in sorted(scored, key=lambda x: -x[0]) if score > 0][:k]
