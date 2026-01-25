from dataclasses import dataclass, field
from typing import Optional, Union, Literal

AmendmentScope = Literal["BRACKET", "ASTERISK", "OMISSION", "STATE_SPECIFIC"]
AmendmentAnchor = Literal["SUPERSCRIPT", "ASTERISK", "INLINE_NOTE"]
AmendmentOperation = Literal[
    "INSERTION",
    "SUBSTITUTION",
    "REPEAL",
    "OMISSION",
    "COMMENCEMENT",
    "NOT_AN_AMENDMENT"
]

@dataclass
class Amendment:
    """Represents legal changes, including state-specific modifications found in Sch 6 [1, 2]."""
    marker: str
    anchor: AmendmentAnchor
    operation: AmendmentOperation
    description: str
    date_enacted: Optional[str] = None
    span_text: Optional[str] = None
    applied_to_state: Optional[str] = None  # Crucial for Schedule 6 variations [3, 4]
    source_page: Optional[int] = None  # The page number in the source document

@dataclass
class ScheduleEntry:
    """A generic entry for numbered lists (Sch 7, 8, 9, 11, 12) [5-8]."""
    number: str
    base_text: str  
    metadata: Optional[dict] = None # For 'Territories' in Sch 1 or 'Seats' in Sch 4 [9, 10]
    amendments: list[Amendment] = field(default_factory=list)
    sub_entries: list["ScheduleEntry"] = field(default_factory=list) # For sub-paragraphs [11]
    source_page: Optional[int] = None  # The page number in the source document

@dataclass
class TableSection:
    """Handles the tables found in Schedule 4 and Schedule 6 [10, 12]."""
    heading: str
    columns: list[str]
    rows: list[dict[str, Union[str, int]]] 
    amendments: list[Amendment] = field(default_factory=list)

@dataclass
class OathForm:
    """Specialized structure for the Third Schedule forms [13, 14]."""
    form_id: str  # Roman numerals I-VIII
    title: str    # e.g., 'Minister for the Union'
    content: str  # The template text with placeholders
    amendments: list[Amendment] = field(default_factory=list)

@dataclass
class SchedulePart:
    """Represents major divisions like Part A, B, C (Sch 1, 2, 5, 6) [15-17]."""
    part_name: str
    heading: str
    content_blocks: list[Union[ScheduleEntry, TableSection]]
    amendments: list[Amendment] = field(default_factory=list)

@dataclass
class Schedule:
    """The root container for any of the 12 Schedules."""
    name: str = "" # e.g., 'FIFTH SCHEDULE'
    articles: list[str] = field(default_factory=list) # Referenced Articles, e.g., ['244(1)'] [15]
    parts: list[SchedulePart] = field(default_factory=list)
    # For schedules that are just a flat list of entries or forms
    flat_entries: list[Union[ScheduleEntry, OathForm]] = field(default_factory=list)
    global_amendments: list[Amendment] = field(default_factory=list)


@dataclass
class ExplanationOrProviso:
    """Represents 'Explanations' or 'Provisos' found at Article or Clause levels."""
    type: Literal["EXPLANATION", "PROVISO"]
    canonical_id: str  # e.g. "ART_19_CLAUSE_1_EXPLANATION_I"
    label: str # e.g., "Explanation I" or "Provided further"
    text: str
    source_page: int  # Added for citation
    ordinal: Optional[int] = None  # 1 = first proviso, 2 = second proviso
    amendments: list[Amendment] = field(default_factory=list)


@dataclass
class SubClause:
    """Represents sub-paragraphs, e.g., (a), (b), or deeper (i), (ii)."""
    marker: str 
    canonical_id: str  # e.g. "ART_19_CLAUSE_1_A"
    text: str # If sub_clauses is non-empty, text is the clause lead-in only.
    source_page: int  # Added for citation
    amendments: list[Amendment] = field(default_factory=list)
    sub_clauses: list['SubClause'] = field(default_factory=list) # Added for recursion
    is_omitted: bool = False # Added for things like Art 19(1)(f)


@dataclass
class Clause:
    """Represents numbered sections within an article, e.g., (1), (2)."""
    number: str 
    canonical_id: str  # e.g. "ART_19_CLAUSE_1"
    source_page: int  # Added for citation
    text: Optional[str] = None 
    sub_clauses: list[SubClause] = field(default_factory=list)
    explanations_provisos: list[ExplanationOrProviso] = field(default_factory=list)
    amendments: list[Amendment] = field(default_factory=list)
    is_omitted: bool = False # Handle omitted clauses


@dataclass
class Article:
    """The fundamental unit of the Constitution."""
    number: str 
    canonical_id: str  # e.g. "ART_19"
    heading: str 
    source_page: int  # Added for citation
    text: Optional[str] = None 
    clauses: list[Clause] = field(default_factory=list)
    explanations_provison: list[ExplanationOrProviso] = field(default_factory=list)
    amendments: list[Amendment] = field(default_factory=list)
    is_omitted: bool = False
    effective_from: Optional[str] = None
    effective_to: Optional[str] = None


@dataclass
class Chapter:
    """Groups of articles within a Part, found in larger Parts like Part V."""
    name: str # e.g., "CHAPTER I"
    heading: str # e.g., "THE EXECUTIVE"
    articles: list[Article] = field(default_factory=list)


@dataclass
class Part:
    """The primary division of the Constitution, e.g., PART III."""
    name: str # e.g., "PART III"
    heading: str # e.g., "FUNDAMENTAL RIGHTS"
    chapters: list[Chapter] = field(default_factory=list)
    # Some Parts contain Articles directly without Chapters
    articles: list[Article] = field(default_factory=list)
    amendments: list[Amendment] = field(default_factory=list)

@dataclass
class VectorResult:
    """Holds the result of an embedding operation."""
    rank: int
    text: str
    doc_type: str
    canonical_id: str
    article: Optional[str] = None
    clause: Optional[str] = None
    sub_clause: Optional[str] = None
    similarity_score: Optional[float] = None
    court: Optional[str] = None
    citation: Optional[str] = None
    source_page: Optional[int] = None
    source_file: Optional[str] = None
    schedule: Optional[str] = None
    entry: Optional[str] = None
    amendment: Optional[str] = None