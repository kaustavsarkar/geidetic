I am providing the text content for a Schedule from the Constitution of India.
Parse this content into a JSON object that strictly adheres to the Python dataclass structure provided below.
Do not infer, summarize, paraphrase, or modernize constitutional text. Preserve all constitutional text verbatim.

### 1. Class Structure

```python
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
    marker: str
    anchor: AmendmentAnchor
    operation: AmendmentOperation
    description: str
    date_enacted: Optional[str] = None
    span_text: Optional[str] = None
    applied_to_state: Optional[str] = None
    source_page: Optional[int] = None

@dataclass
class ScheduleEntry:
    number: str
    base_text: str
    metadata: Optional[dict] = None
    amendments: list[Amendment] = field(default_factory=list)
    sub_entries: list["ScheduleEntry"] = field(default_factory=list)
    source_page: Optional[int] = None

@dataclass
class TableSection:
    heading: str
    columns: list[str]
    rows: list[dict[str, Union[str, int]]]
    amendments: list[Amendment] = field(default_factory=list)

@dataclass
class OathForm:
    form_id: str
    title: str
    content: str
    amendments: list[Amendment] = field(default_factory=list)

@dataclass
class SchedulePart:
    part_name: str
    heading: str
    content_blocks: list[Union[ScheduleEntry, TableSection]]
    amendments: list[Amendment] = field(default_factory=list)

@dataclass
class Schedule:
    name: str = ""
    articles: list[str] = field(default_factory=list)
    parts: list[SchedulePart] = field(default_factory=list)
    flat_entries: list[Union[ScheduleEntry, OathForm]] = field(default_factory=list)
    global_amendments: list[Amendment] = field(default_factory=list)
```

### 2. Strict Parsing Rules
#### A. Header and Title
- Extract the Schedule name (e.g., "THIRD SCHEDULE").
- Extract all referenced Articles into Schedule.articles.
- Detect superscripts, asterisks, or bracketed markers in the Schedule title.
    - Create corresponding Amendment objects.
    - Store them in Schedule.global_amendments.
    - Set source_page to the page where the marker appears.

#### B. Structural Detection
- If the Schedule is divided into Parts (PART A, PART B, etc.), populate Schedule.parts.
- If the Schedule is a continuous list (no Parts), populate Schedule.flat_entries.
- Preserve the original document order at all levels.

#### C. Part Headings
- Represent each Part using SchedulePart.
- Capture any amendment markers appearing in:
  - Part name
  - Part heading text
- Capture any amendment markers appearing in Part headings as SchedulePart.amendments.

#### D. Entries
- Every numbered paragraph, item, clause, or sub-clause must be represented as a ScheduleEntry.
- Preserve numbering exactly as printed (Roman numerals, letters, hyphens, etc.).
- Populate source_page using the page where the entry text appears.

**Deleted / Omitted Entries**
If an entry has been deleted, omitted, or repealed:
- Retain its original position.
- Set:
    - number = "-1" (or original number if explicitly shown)
    - base_text = "Deleted/Omitted"
- Attach the Amendment responsible for the deletion.

#### E. Footnote and Marker Mapping
For each footnote or marker:
- Map the marker (e.g., 1, *, **) to its footnote.
- Populate Amendment fields strictly as follows:

| Field          | Rule                                         |
| -------------- | -------------------------------------------- |
| `marker`       | Exact symbol or number                       |
| `anchor`       | SUPERSCRIPT / ASTERISK / INLINE_NOTE         |
| `operation`    | Based **only** on explicit keywords          |
| `description`  | Verbatim footnote text                       |
| `date_enacted` | Extract exactly (e.g., `"w.e.f. 1-11-1956"`) |
| `span_text`    | Exact affected constitutional text           |
| `source_page`  | Page where the footnote appears              |

**Operation Mapping (Exact)**
- "Ins." → INSERTION
- "Subs." → SUBSTITUTION
- "Omitted" → OMISSION
- "Repealed" → REPEAL
- "w.e.f." with no modification → COMMENCEMENT

If none apply:
- Use NOT_AN_AMENDMENT
- Explain why in description.

#### F. Editorial Notes
- Footnotes or notes that do not modify constitutional text must be recorded with:
    - operation = "NOT_AN_AMENDMENT".

#### G. State-Specific Amendments
- If an amendment applies only to a specific State, populate applied_to_state.

#### H. Tables
- If the content is tabular (Schedules 4 or 6), use TableSection.
- Preserve column names and row values exactly.

#### I. Oath Forms (Third Schedule)
- Use OathForm instead of ScheduleEntry.
- Preserve placeholders, formatting, and wording exactly.

#### J. Ordering Guarantees
- Preserve document order for Parts and entries.
- Maintain amendment order as they appear in the text.
- Do not reorder for readability or grouping.

#### K. Output Rules
- Output only the raw JSON object.
- No markdown.
- No explanations.
- No trailing text.

### 3. Few Shot Example
#### Example Input (Raw Text)
```
FIRST SCHEDULE
[Articles 1 and 4]

PART I
THE STATES

1. Andhra Pradesh¹ — The territories specified in sub-section (1) of section 3
of the Andhra State Act, 1953.

¹ Subs. by the Andhra Pradesh Reorganisation Act, 2014, w.e.f. 2-6-2014.

Page 253
```

#### Example Output (Gold Standard JSON)
```json
{
  "name": "FIRST SCHEDULE",
  "articles": ["1", "4"],
  "parts": [
    {
      "part_name": "PART I",
      "heading": "THE STATES",
      "content_blocks": [
        {
          "number": "1",
          "base_text": "Andhra Pradesh¹ — The territories specified in sub-section (1) of section 3\nof the Andhra State Act, 1953.",
          "metadata": null,
          "amendments": [
            {
              "marker": "1",
              "anchor": "SUPERSCRIPT",
              "operation": "SUBSTITUTION",
              "description": "Subs. by the Andhra Pradesh Reorganisation Act, 2014, w.e.f. 2-6-2014.",
              "date_enacted": "w.e.f. 2-6-2014",
              "span_text": "Andhra Pradesh¹ — The territories specified in sub-section (1) of section 3\nof the Andhra State Act, 1953.",
              "applied_to_state": null,
              "source_page": 253
            }
          ],
          "sub_entries": [],
          "source_page": 253
        }
      ],
      "amendments": []
    }
  ],
  "flat_entries": [],
  "global_amendments": []
}
```

#### Example Input (Synthetic, Minimal, Representative)

```
THIRD SCHEDULE*
[Articles 75(4), 99, 124(6)]

* Subs. by Constitution (42nd Amendment) Act, 1976.

PART I
FORMS OF OATH OR AFFIRMATION

FORM I
Oath for a Minister

"I, A.B., do swear in the name of God that I will faithfully discharge..."

¹ Subs. by Act 44 of 1978, w.e.f. 3-1-1977.

Page 110

PART II
MISCELLANEOUS

1. Allowances — The allowances shall be as prescribed.

2. Deleted.

² Omitted by Act 7 of 1956.

Page 111

PART III
TABLE OF SEATS

| State | Seats |
| Assam | 7     |
| Goa  | 1     |

³ Ins. by Act 56 of 1987 (Goa only).

Page 112
```
#### Example Output (Gold-Standard JSON)

```json
{
  "name": "THIRD SCHEDULE",
  "articles": ["75(4)", "99", "124(6)"],
  "parts": [
    {
      "part_name": "PART I",
      "heading": "FORMS OF OATH OR AFFIRMATION",
      "content_blocks": [
        {
          "form_id": "I",
          "title": "Oath for a Minister",
          "content": "\"I, A.B., do swear in the name of God that I will faithfully discharge...\"",
          "amendments": [
            {
              "marker": "1",
              "anchor": "SUPERSCRIPT",
              "operation": "SUBSTITUTION",
              "description": "Subs. by Act 44 of 1978, w.e.f. 3-1-1977.",
              "date_enacted": "w.e.f. 3-1-1977",
              "span_text": "\"I, A.B., do swear in the name of God that I will faithfully discharge...\"",
              "applied_to_state": null,
              "source_page": 110
            }
          ]
        }
      ],
      "amendments": []
    },
    {
      "part_name": "PART II",
      "heading": "MISCELLANEOUS",
      "content_blocks": [
        {
          "number": "1",
          "base_text": "Allowances — The allowances shall be as prescribed.",
          "metadata": null,
          "amendments": [],
          "sub_entries": [],
          "source_page": 111
        },
        {
          "number": "-1",
          "base_text": "Deleted/Omitted",
          "metadata": null,
          "amendments": [
            {
              "marker": "2",
              "anchor": "SUPERSCRIPT",
              "operation": "OMISSION",
              "description": "Omitted by Act 7 of 1956.",
              "date_enacted": null,
              "span_text": null,
              "applied_to_state": null,
              "source_page": 111
            }
          ],
          "sub_entries": [],
          "source_page": 111
        }
      ],
      "amendments": []
    },
    {
      "part_name": "PART III",
      "heading": "TABLE OF SEATS",
      "content_blocks": [
        {
          "heading": "TABLE OF SEATS",
          "columns": ["State", "Seats"],
          "rows": [
            { "State": "Assam", "Seats": 7 },
            { "State": "Goa", "Seats": 1 }
          ],
          "amendments": [
            {
              "marker": "3",
              "anchor": "SUPERSCRIPT",
              "operation": "INSERTION",
              "description": "Ins. by Act 56 of 1987 (Goa only).",
              "date_enacted": null,
              "span_text": "Goa | 1",
              "applied_to_state": "Goa",
              "source_page": 112
            }
          ]
        }
      ],
      "amendments": []
    }
  ],
  "flat_entries": [],
  "global_amendments": [
    {
      "marker": "*",
      "anchor": "ASTERISK",
      "operation": "SUBSTITUTION",
      "description": "Subs. by Constitution (42nd Amendment) Act, 1976.",
      "date_enacted": null,
      "span_text": "THIRD SCHEDULE",
      "applied_to_state": null,
      "source_page": 110
    }
  ]
}
```