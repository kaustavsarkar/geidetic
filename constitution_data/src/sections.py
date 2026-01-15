from dataclasses import dataclass
from typing import List

@dataclass
class Section:
    number: str
    heading: str
    text: str
    amendments: List[str]
    part: str = ""

@dataclass
class Article(Section):
    """Represents a standard Article section in the constitution text."""
    pass

@dataclass
class FrontMatter(Section):
    """Represents front-matter sections such as Contents or Preamble."""
    part: str = "Front Matter"

@dataclass
class Schedule(Section):
    """Represents a Schedule section in the constitution text."""
    part: str = "Schedule"
    
@dataclass
class SchedulePart:
    """Represents a part within a Schedule section."""
    name: str
    content: str
