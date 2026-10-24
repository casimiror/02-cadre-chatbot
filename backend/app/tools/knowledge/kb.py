import re
from dataclasses import dataclass
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).resolve().parents[2] / "knowledge"
_WORD = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True)
class Section:
    source: str
    title: str
    body: str

    def render(self) -> str:
        return f"[{self.source} › {self.title}]\n{self.body.strip()}"


def _tokens(text: str) -> set[str]:
    return {w for w in _WORD.findall(text.lower()) if len(w) > 2}


class KnowledgeBase:
    """Markdown files split by `## ` headings, ranked by keyword overlap.

    Deliberately simple and debuggable; swap for pgvector if the KB grows (see plan.md).
    """

    def __init__(self, directory: Path = KNOWLEDGE_DIR) -> None:
        self.sections = [s for path in sorted(directory.glob("*.md")) for s in self._split(path)]

    @staticmethod
    def _split(path: Path) -> list[Section]:
        parts = re.split(r"^## ", path.read_text(), flags=re.MULTILINE)
        sections = []
        for part in parts[1:]:
            title, _, body = part.partition("\n")
            sections.append(Section(source=path.stem, title=title.strip(), body=body))
        return sections

    def search(self, query: str, k: int = 3) -> list[Section]:
        q = _tokens(query)
        scored = [(len(q & _tokens(s.title + " " + s.body)), s) for s in self.sections]
        return [s for score, s in sorted(scored, key=lambda x: -x[0]) if score > 0][:k]
