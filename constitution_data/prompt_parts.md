### LLM Parsing Prompt: Constitution of India (Part/Article Logic)
**Role**: You are a Specialized Legal Knowledge Engineer. Your objective is to parse the provided text of the Constitution of India into a JSON format that strictly adheres to the provided Python Dataclass schema.
- Do not infer or create Clauses, SubClauses, Explanations, or Provisos unless they are explicitly present in the text.
- If an Article contains unnumbered prose only, populate Article.text and leave clauses empty.


#### Target Schema (Reference)
Your JSON output must map perfectly to these classes:

```python
# Literal definitions for validation
AmendmentScope = ["BRACKET", "ASTERISK", "OMISSION", "STATE_SPECIFIC"]
AmendmentAnchor = ["SUPERSCRIPT", "ASTERISK", "INLINE_NOTE"]
AmendmentOperation = ["INSERTION", "SUBSTITUTION", "REPEAL", "OMISSION", "COMMENCEMENT", "NOT_AN_AMENDMENT"]

@dataclass
class Amendment:
    marker: str
    anchor: AmendmentAnchor
    operation: AmendmentOperation
    description: str
    date_enacted: Optional[str] = None
    span_text: Optional[str] = None
    applied_to_state: Optional[str] = None 
    source_page: Optional[int] = None 

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
```
#### Critical Extraction Rules
- **Part Extraction**
  - Create exactly one Part object.
  - Part.name must match the printed label (e.g., "PART III").
  - Part.heading must match the printed heading verbatim.
  - If the Part contains Chapters, populate Part.chapters.
  - If the Part has Articles directly, populate Part.articles.
  - Preserve original document order.

- **Chapter Extraction**
  - Create a Chapter only if explicitly printed (e.g., "CHAPTER I").
  - Do not infer chapters.
  - Populate Chapter.name and Chapter.heading verbatim.

- **Article Extraction**
  - Every Article printed in the text must produce exactly one Article.
  - Populate:
    - number exactly as printed (e.g., "19", "19A").
    - heading from the marginal heading.
    - canonical_id as ART_<number>.
    - source_page from the page where the Article text begins.
  - If the Article has no numbered clauses, populate Article.text and leave clauses empty.
  - If an Article is marked as omitted (e.g., "2A. [Sikkim to be associated...] Omitted...")
    - Set is_omitted = true
    - Do not fabricate text.

- Clause Extraction
  - Create a Clause only if a numbered clause exists (e.g., (1)).
  - Populate:
    - number exactly as printed.
    - canonical_id as 'ART_<article>_CLAUSE_<number>'.
    - text only if the clause contains lead-in prose.
  - If the clause is explicitly omitted, set is_omitted = true.

- **The Marginal Heading Rule:**
  - The heading field for an Article must capture the descriptive title (e.g., "Admission or establishment of new States.").

- **Recursive Sub-Clauses:**
  - Create SubClause objects only for explicitly labeled markers:
    - (a), (b), (i), (ii), etc.
  - Nest recursively only if nesting is explicitly shown.
  - text must contain only the text belonging to that marker.
  - Populate canonical_id deterministically.

#### PROVISOS & EXPLANATIONS (NON-NEGOTIABLE RULES)
- **Identification**
  - Use EXPLANATION only if the word “Explanation” appears.
  - Use PROVISO only if the text begins with:
    - “Provided that”
    - “Provided further that”
    - “Provided also that”
- **Attachment Rule (MANDATORY)**
  - A proviso or explanation attaches to the nearest immediately preceding unit:
    - Clause
    - Otherwise Article
  - Never attach to SubClauses.
- **Ordinal Rule**
  - Assign ordinal = 1 for first proviso, 2 for second proviso, etc.
  - There is no maximum limit on provisos.

#### AMENDMENT EXTRACTION (ZERO INFERENCE)

- **Marker Detection**
  - Detect only:
    - Superscripts (¹, ²)
    - Asterisks (*, **)
    - Inline bracketed notes
- **Mapping Rules**
  - Every marker must map to a footnote on the same page.
  - If no clear mapping exists:
    - Set operation = NOT_AN_AMENDMENT
    - Explain ambiguity in description
- **Operation Mapping (EXACT MATCH ONLY)**
  
| Footnote Keyword | Operation    |
| ---------------- | ------------ |
| "Ins."           | INSERTION    |
| "Subs."          | SUBSTITUTION |
| "Omitted"        | OMISSION     |
| "Repealed"       | REPEAL       |
| "w.e.f." alone   | COMMENCEMENT |

- **Scope Rules**
  - BRACKET → amendment text appears in square brackets
  - ASTERISK → referenced via * or **
  - OMISSION → text explicitly omitted
  - STATE_SPECIFIC → applies only to named State

- **Temporal Rules**
  - Populate effective_from or date_enacted only if explicitly stated
  - Populate effective_to only when repeal/substitution explicitly states a date
  - Never infer dates from amendment numbers

#### SOURCE PAGE RULE (MANDATORY)

- Detect page boundaries from visible markers (page numbers, separators).
- Assign source_page to the page where the text begins.
- If page number cannot be determined:
- Set source_page = null
- Do not guess

#### FORBIDDEN ACTIONS (HARD FAIL)
- You must NOT:
  - Infer structure
  - Reword text
  - Combine clauses
  - Split sentences
  - Guess amendments
  - Guess dates
  - Create missing hierarchy
  - Normalize language

If something is unclear, represent it minimally and mark ambiguity explicitly.

#### ABSOLUTE OUTPUT CONTRACT
- Output ONLY a single valid JSON object.
- The JSON MUST conform exactly to the provided Python dataclass schema.
- Do NOT include:
  - Markdown
  - Explanations
  - Comments
  - Extra keys
  - Missing required fields
- If a value cannot be determined from explicit text, use null or an empty list — never guess.

### Few Shot Examples:
#### FEW-SHOT EXAMPLE 1 (Article with Clauses, Sub-Clauses, Provisos, Explanation, and Amendment**)
##### FEW-SHOT INPUT (Example Text)
```
--- PAGE 145 ---

19. Protection of certain rights regarding freedom of speech, etc.—

(1) All citizens shall have the right—
    (a) to freedom of speech and expression;
    (b) to assemble peaceably and without arms;

Provided that nothing in sub-clause (a) shall affect the operation of any existing law.

Explanation I.—Nothing in this clause shall prevent the State from making any law.

(2) Nothing in sub-clause (a) of clause (1) shall affect the operation of any existing law¹.

¹ Subs. by the Constitution (First Amendment) Act, 1951, w.e.f. 18-6-1951.
```

##### FEW-SHOT OUTPUT (Gold-Standard JSON)

```json
{
  "name": "PART III",
  "heading": "FUNDAMENTAL RIGHTS",
  "chapters": [],
  "articles": [
    {
      "number": "19",
      "canonical_id": "ART_19",
      "heading": "Protection of certain rights regarding freedom of speech, etc.—",
      "source_page": 145,
      "text": null,
      "clauses": [
        {
          "number": "1",
          "canonical_id": "ART_19_CLAUSE_1",
          "source_page": 145,
          "text": "All citizens shall have the right—",
          "sub_clauses": [
            {
              "marker": "a",
              "canonical_id": "ART_19_CLAUSE_1_A",
              "text": "to freedom of speech and expression;",
              "source_page": 145,
              "amendments": [],
              "sub_clauses": [],
              "is_omitted": false
            },
            {
              "marker": "b",
              "canonical_id": "ART_19_CLAUSE_1_B",
              "text": "to assemble peaceably and without arms;",
              "source_page": 145,
              "amendments": [],
              "sub_clauses": [],
              "is_omitted": false
            }
          ],
          "explanations_provisos": [
            {
              "type": "PROVISO",
              "canonical_id": "ART_19_CLAUSE_1_PROVISO_1",
              "label": "Provided that",
              "text": "nothing in sub-clause (a) shall affect the operation of any existing law.",
              "source_page": 145,
              "ordinal": 1,
              "amendments": []
            },
            {
              "type": "EXPLANATION",
              "canonical_id": "ART_19_CLAUSE_1_EXPLANATION_I",
              "label": "Explanation I",
              "text": "Nothing in this clause shall prevent the State from making any law.",
              "source_page": 145,
              "ordinal": null,
              "amendments": []
            }
          ],
          "amendments": [],
          "is_omitted": false
        },
        {
          "number": "2",
          "canonical_id": "ART_19_CLAUSE_2",
          "source_page": 145,
          "text": "Nothing in sub-clause (a) of clause (1) shall affect the operation of any existing law",
          "sub_clauses": [],
          "explanations_provisos": [],
          "amendments": [
            {
              "marker": "1",
              "anchor": "SUPERSCRIPT",
              "operation": "SUBSTITUTION",
              "description": "Subs. by the Constitution (First Amendment) Act, 1951, w.e.f. 18-6-1951.",
              "date_enacted": "w.e.f. 18-6-1951",
              "span_text": "Nothing in sub-clause (a) of clause (1) shall affect the operation of any existing law",
              "applied_to_state": null,
              "source_page": 145
            }
          ],
          "is_omitted": false
        }
      ],
      "explanations_provison": [],
      "amendments": [],
      "is_omitted": false,
      "effective_from": null,
      "effective_to": null
    }
  ],
  "amendments": []
}
```


#### FEW-SHOT EXAMPLE 2 - Omitted Article (No Clauses)
##### FEW-SHOT INPUT
```
--- PAGE 152 ---

19(1)(f). [Right to acquire, hold and dispose of property] Omitted by the Constitution (Forty-fourth Amendment) Act, 1978, w.e.f. 20-6-1979.
```
##### FEW-SHOT OUTPUT
```json
{
  "number": "19(1)(f)",
  "canonical_id": "ART_19_1_F",
  "heading": "Right to acquire, hold and dispose of property",
  "source_page": 152,
  "text": null,
  "clauses": [],
  "explanations_provison": [],
  "amendments": [
    {
      "marker": "",
      "anchor": "INLINE_NOTE",
      "operation": "OMISSION",
      "description": "Omitted by the Constitution (Forty-fourth Amendment) Act, 1978, w.e.f. 20-6-1979.",
      "date_enacted": "w.e.f. 20-6-1979",
      "span_text": "Right to acquire, hold and dispose of property",
      "applied_to_state": null,
      "source_page": 152
    }
  ],
  "is_omitted": true,
  "effective_from": null,
  "effective_to": "20-6-1979"
}
```