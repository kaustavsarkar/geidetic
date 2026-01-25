
import json
import os
from typing import List, Dict, Any, Union, Optional
from models.model import (
    Amendment, ScheduleEntry, TableSection, OathForm, SchedulePart, Schedule,
    ExplanationOrProviso, SubClause, Clause, Article, Chapter, Part
)

# ---------------------------
# Converters
# ---------------------------

def dict_to_amendment(data: Dict[str, Any]) -> Amendment:
    return Amendment(
        marker=data.get("marker", ""),
        anchor=data.get("anchor", "ASTERISK"), # Default or handle error
        operation=data.get("operation", "NOT_AN_AMENDMENT"),
        description=data.get("description", ""),
        date_enacted=data.get("date_enacted"),
        span_text=data.get("span_text"),
        applied_to_state=data.get("applied_to_state"),
        source_page=data.get("source_page")
    )

def dict_to_amendments(data_list: List[Dict[str, Any]]) -> List[Amendment]:
    return [dict_to_amendment(x) for x in data_list]

def dict_to_explanation_proviso(data: Dict[str, Any]) -> ExplanationOrProviso:
    return ExplanationOrProviso(
        type=data.get("type", "EXPLANATION"),
        canonical_id=data.get("canonical_id", ""),
        label=data.get("label", ""),
        text=data.get("text", ""),
        source_page=data.get("source_page", 0),
        ordinal=data.get("ordinal"),
        amendments=dict_to_amendments(data.get("amendments", []))
    )

def dict_to_subclause(data: Dict[str, Any]) -> SubClause:
    return SubClause(
        marker=data.get("marker", ""),
        canonical_id=data.get("canonical_id", ""),
        text=data.get("text", ""),
        source_page=data.get("source_page", 0),
        amendments=dict_to_amendments(data.get("amendments", [])),
        sub_clauses=[dict_to_subclause(x) for x in data.get("sub_clauses", [])],
        is_omitted=data.get("is_omitted", False)
    )

def dict_to_clause(data: Dict[str, Any]) -> Clause:
    return Clause(
        number=data.get("number", ""),
        canonical_id=data.get("canonical_id", ""),
        source_page=data.get("source_page", 0),
        text=data.get("text"),
        sub_clauses=[dict_to_subclause(x) for x in data.get("sub_clauses", [])],
        explanations_provisos=[dict_to_explanation_proviso(x) for x in data.get("explanations_provisos", [])],
        amendments=dict_to_amendments(data.get("amendments", [])),
        is_omitted=data.get("is_omitted", False)
    )

def dict_to_article(data: Dict[str, Any]) -> Article:
    # Handle the typo in model.py 'explanations_provison' vs 'explanations_provisos'
    # The JSON usually has 'explanations_provison' or 'explanations_provisos'
    explanations = data.get("explanations_provison", [])
    if not explanations:
         explanations = data.get("explanations_provisos", [])

    return Article(
        number=data.get("number", ""),
        canonical_id=data.get("canonical_id", ""),
        heading=data.get("heading", ""),
        source_page=data.get("source_page", 0),
        text=data.get("text"),
        clauses=[dict_to_clause(x) for x in data.get("clauses", [])],
        explanations_provison=[dict_to_explanation_proviso(x) for x in explanations],
        amendments=dict_to_amendments(data.get("amendments", [])),
        is_omitted=data.get("is_omitted", False),
        effective_from=data.get("effective_from"),
        effective_to=data.get("effective_to")
    )

def dict_to_chapter(data: Dict[str, Any]) -> Chapter:
    return Chapter(
        name=data.get("name", ""),
        heading=data.get("heading", ""),
        articles=[dict_to_article(x) for x in data.get("articles", [])]
    )

def dict_to_part(data: Dict[str, Any]) -> Part:
    return Part(
        name=data.get("name", ""),
        heading=data.get("heading", ""),
        chapters=[dict_to_chapter(x) for x in data.get("chapters", [])],
        articles=[dict_to_article(x) for x in data.get("articles", [])],
        amendments=dict_to_amendments(data.get("amendments", []))
    )

# ---------------------------
# Schedule Converters
# ---------------------------

def dict_to_oath_form(data: Dict[str, Any]) -> OathForm:
    return OathForm(
        form_id=data.get("form_id", ""),
        title=data.get("title", ""),
        content=data.get("content", ""),
        amendments=dict_to_amendments(data.get("amendments", []))
    )

def dict_to_schedule_entry(data: Dict[str, Any]) -> ScheduleEntry:
    return ScheduleEntry(
        number=data.get("number", ""),
        base_text=data.get("base_text", ""),
        metadata=data.get("metadata"),
        amendments=dict_to_amendments(data.get("amendments", [])),
        sub_entries=[dict_to_schedule_entry(x) for x in data.get("sub_entries", [])],
        source_page=data.get("source_page")
    )

def dict_to_table_section(data: Dict[str, Any]) -> TableSection:
    return TableSection(
        heading=data.get("heading", ""),
        columns=data.get("columns", []),
        rows=data.get("rows", []),
        amendments=dict_to_amendments(data.get("amendments", []))
    )

def dict_to_schedule_part(data: Dict[str, Any]) -> SchedulePart:
    content_blocks = []
    for block in data.get("content_blocks", []):
         # Distinguish between TableSection and ScheduleEntry
         if "columns" in block and "rows" in block:
             content_blocks.append(dict_to_table_section(block))
         else:
             content_blocks.append(dict_to_schedule_entry(block))

    return SchedulePart(
        part_name=data.get("part_name", ""),
        heading=data.get("heading", ""),
        content_blocks=content_blocks,
        amendments=dict_to_amendments(data.get("amendments", []))
    )

def dict_to_schedule(data: Dict[str, Any]) -> Schedule:
    flat_entries = []
    for entry in data.get("flat_entries", []):
        # Distinguish between OathForm and ScheduleEntry
        # OathForm has 'form_id', ScheduleEntry has 'number'
        if "form_id" in entry:
            flat_entries.append(dict_to_oath_form(entry))
        else:
             flat_entries.append(dict_to_schedule_entry(entry))

    return Schedule(
        name=data.get("name", ""),
        articles=data.get("articles", []),
        parts=[dict_to_schedule_part(x) for x in data.get("parts", [])],
        flat_entries=flat_entries,
        global_amendments=dict_to_amendments(data.get("global_amendments", []))
    )

# ---------------------------
# Loaders
# ---------------------------

def load_parts(data_dir: str) -> List[Part]:
    parts_dir = os.path.join(data_dir, "parts")
    parts: list[Part] = []
    
    if not os.path.exists(parts_dir):
        print(f"Warning: Directory {parts_dir} does not exist.")
        return []

    # Sort files to ensure order if necessary, though Part numbers deal with that
    # Filenames like part_1.json, part_10.json might sort oddly as strings, 
    # but for now simple processing is fine.
    filenames = sorted([f for f in os.listdir(parts_dir) if f.endswith(".json")])
    
    for filename in filenames:
        filepath = os.path.join(parts_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                parts.append(dict_to_part(data))
        except Exception as e:
            print(f"Error loading part from {filename}: {e}")

    return parts

def load_schedules(data_dir: str) -> List[Schedule]:
    schedules_dir = os.path.join(data_dir, "schedules")
    schedules = []

    if not os.path.exists(schedules_dir):
        print(f"Warning: Directory {schedules_dir} does not exist.")
        return []
    
    filenames = sorted([f for f in os.listdir(schedules_dir) if f.endswith(".json")])
    
    for filename in filenames:
        # Skip internal data files or non-schedule jsons if any (e.g. sft_*.json)
        # Based on file listing, we have "sft_constitution.introduction.json" etc.
        # We only want schedule files.
        # Simple heuristic: Check if it has "schedule" in the name or the loaded json has "name" starting with schedule?
        # Better: check the name field in the json or filename. 
        # Schedule filenames: "first_schedule.json", "second_schedule.json", etc.
        if "schedule" not in filename or filename.startswith("sft_"):
            continue
            
        filepath = os.path.join(schedules_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                schedules.append(dict_to_schedule(data))
        except Exception as e:
            print(f"Error loading schedule from {filename}: {e}")
            
    return schedules
