"""
Constitution data processors module.

This module contains all the processing functions for converting Constitution
dataclasses (Parts, Schedules, Articles, etc.) into database rows suitable for
ingestion into LanceDB.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Optional, Any

from db_manager import EMBED_DIM, LegalEmbedding
from model_manager import get_embedding_model
from models.model import Part, Article, Clause, SubClause


# Configuration
EMBED_MODEL_NAME = "BAAI/bge-small-en-v1.5"


# ---------------------------
# Utility Functions
# ---------------------------

def embed_text(text: str) -> list[float]:
    """Generate embedding for text using the embedding model."""
    model = get_embedding_model(EMBED_MODEL_NAME)
    vec = model.encode(text, normalize_embeddings=True)
    # Ensure float32 type for LanceDB compatibility
    return [float(x) for x in vec.tolist()]


def now_iso():
    """Get current timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()


def build_row(
    text,
    doc_type,
    canonical_id,
    part=None,
    chapter=None,
    article=None,
    clause=None,
    sub_clause=None,
    schedule_name=None,
    schedule_part=None,
    entry_number=None,
    metadata=None,
    source_page=None,
    source_file=None,
    effective_from=None,
    effective_to=None,
    act_name=None,
    act_year=None,
    case_name=None,
    court=None,
    citation=None,
    paragraph_no=None,
    jurisdiction="India"
):
    """
    Build a database row dictionary with all required fields.
    
    Args:
        text: The main text content
        doc_type: Type of document (e.g., CONSTITUTION_ARTICLE, SCHEDULE_ENTRY)
        canonical_id: Unique identifier for this piece of content
        ... (other fields are optional metadata)
    
    Returns:
        dict: A complete row ready for database insertion
    """
    if text is None:
        print("Text is None. Skipping embedding", text, canonical_id)
        embedding = [0.0] * EMBED_DIM
    else:
        embedding = embed_text(text)
        
    return LegalEmbedding(
        id=str(uuid.uuid4()),
        embedding=embedding,
        text=text,
        doc_type=doc_type,
        canonical_id=canonical_id,
        part=part,
        chapter=chapter,
        article=article,
        clause=clause,
        sub_clause=sub_clause,
        schedule_name=schedule_name,
        schedule_part=schedule_part,
        entry_number=entry_number,
        metadata=metadata,
        act_name=act_name,
        act_year=act_year,
        case_name=case_name,
        court=court,
        citation=citation,
        paragraph_no=paragraph_no,
        effective_from=effective_from,
        effective_to=effective_to,
        amendment_marker=None,
        amendment_operation=None,
        source_file=source_file,
        source_page=source_page,
        jurisdiction=jurisdiction,
        ingested_at=now_iso()
    )   


# ---------------------------
# Constitution Article Processing
# ---------------------------

def process_constitution_article(article: Article,
                                 part_name: str, chapter_name: Optional[str], source_file: str):
    """
    Process a Constitution Article into database rows.
    
    Args:
        article: Article dataclass instance
        part_name: Name of the Part this article belongs to
        chapter_name: Name of the Chapter (if any)
        source_file: Source file name
    
    Returns:
        list: List of database rows
    """
    rows = []

    base_meta: dict[str, Any] = {
        "part": part_name,
        "chapter": chapter_name,
        "article": article.number,
        "act_name": None,
        "act_year": None,
        "jurisdiction": "India"
    }

    # -------- Article Lead Text --------

    if article.text:
        rows.append(build_row(
            text=article.text,
            doc_type="CONSTITUTION_ARTICLE",
            canonical_id=article.canonical_id,
            clause=None,
            sub_clause=None,
            source_page=article.source_page,
            effective_from=article.effective_from,
            effective_to=article.effective_to,
            source_file=source_file,
            **base_meta
        ))

    # -------- Clauses --------

    for clause in article.clauses:

        if clause.text:
            rows.append(build_row(
                text=clause.text,
                doc_type="CONSTITUTION_CLAUSE",
                canonical_id=clause.canonical_id,
                clause=clause.number,
                sub_clause=None,
                source_page=clause.source_page,
                effective_from=article.effective_from,
                effective_to=article.effective_to,
                source_file=source_file,
                **base_meta
            ))

        # Sub-clauses
        for sub in clause.sub_clauses:
            rows.extend(process_subclause(sub, clause, article, base_meta, source_file))

    return rows


def process_subclause(sub: SubClause, clause: Clause, 
                      article: Article, base_meta: dict[str, Any], source_file: str):
    """
    Process a sub-clause (recursive for nested sub-clauses).
    
    Args:
        sub: SubClause dictionary
        clause: Parent Clause dictionary
        article: Parent Article dictionary
        base_meta: Base metadata dictionary
        source_file: Source file name
    
    Returns:
        list: List of database rows
    """
    rows = []

    rows.append(build_row(
        text=sub.text,
        doc_type="CONSTITUTION_SUBCLAUSE",
        canonical_id=sub.canonical_id,
        clause=clause.number,
        sub_clause=sub.marker,
        source_page=sub.source_page,
        effective_from=article.effective_from,
        effective_to=article.effective_to,
        source_file=source_file,
        **base_meta
    ))

    for child in sub.sub_clauses:
        rows.extend(process_subclause(child, clause, article, base_meta, source_file))

    return rows


# ---------------------------
# Schedule Processing Functions
# ---------------------------

def process_oath_form(oath_form, schedule_name, schedule_part, source_file):
    """
    Process an OathForm (Third Schedule) into database rows.
    
    Args:
        oath_form: OathForm dataclass instance
        schedule_name: Name of the schedule
        schedule_part: Part within schedule (if any)
        source_file: Source file name
    
    Returns:
        list: List of database rows
    """
    from models.model import OathForm
    
    rows = []
    
    # Main oath form content
    canonical_id = f"{schedule_name.replace(' ', '_')}_{oath_form.form_id.replace(' ', '_')}"
    
    rows.append(build_row(
        text=f"{oath_form.title}\n\n{oath_form.content}",
        doc_type="SCHEDULE_OATH_FORM",
        canonical_id=canonical_id,
        schedule_name=schedule_name,
        schedule_part=schedule_part,
        entry_number=oath_form.form_id,
        metadata=json.dumps({"title": oath_form.title}),
        source_file=source_file
    ))
    
    return rows


def process_table_section(table_section, schedule_name, schedule_part, source_file):
    """
    Process a TableSection (Fourth Schedule, etc.) into database rows.
    
    Args:
        table_section: TableSection dataclass instance
        schedule_name: Name of the schedule
        schedule_part: Part within schedule (if any)
        source_file: Source file name
    
    Returns:
        list: List of database rows
    """
    from models.model import TableSection
    
    rows = []
    
    # Convert table to markdown-style text
    text_parts = [table_section.heading, ""]
    text_parts.append(" | ".join(table_section.columns))
    text_parts.append(" | ".join(["---"] * len(table_section.columns)))
    
    for row_dict in table_section.rows:
        row_values = [str(row_dict.get(col, "")) for col in table_section.columns]
        text_parts.append(" | ".join(row_values))
    
    table_text = "\n".join(text_parts)
    
    canonical_id = f"{schedule_name.replace(' ', '_')}_TABLE_{table_section.heading.replace(' ', '_')}"
    
    rows.append(build_row(
        text=table_text,
        doc_type="SCHEDULE_TABLE",
        canonical_id=canonical_id,
        schedule_name=schedule_name,
        schedule_part=schedule_part,
        metadata=json.dumps({
            "columns": table_section.columns,
            "rows": table_section.rows
        }),
        source_file=source_file
    ))
    
    return rows


def process_schedule_entry(entry, schedule_name, schedule_part, source_file, parent_number=None):
    """
    Process a ScheduleEntry into database rows (recursive for sub-entries).
    
    Args:
        entry: ScheduleEntry dataclass instance
        schedule_name: Name of the schedule
        schedule_part: Part within schedule (if any)
        source_file: Source file name
        parent_number: Parent entry number for nested entries
    
    Returns:
        list: List of database rows
    """
    from models.model import ScheduleEntry
    
    rows = []
    
    # Create canonical ID
    entry_path = f"{parent_number}.{entry.number}" if parent_number else entry.number
    canonical_id = f"{schedule_name.replace(' ', '_')}_ENTRY_{entry_path.replace('.', '_')}"
    
    # Serialize metadata if present
    metadata_json = json.dumps(entry.metadata) if entry.metadata else None
    
    rows.append(build_row(
        text=entry.base_text,
        doc_type="SCHEDULE_ENTRY",
        canonical_id=canonical_id,
        schedule_name=schedule_name,
        schedule_part=schedule_part,
        entry_number=entry.number,
        metadata=metadata_json,
        source_page=entry.source_page,
        source_file=source_file
    ))
    
    # Process sub-entries recursively
    for sub_entry in entry.sub_entries:
        rows.extend(process_schedule_entry(
            sub_entry, 
            schedule_name, 
            schedule_part, 
            source_file, 
            parent_number=entry_path
        ))
    
    return rows


def process_schedule(schedule, source_file):
    """
    Process a Schedule object into database rows.
    
    Args:
        schedule: Schedule dataclass instance
        source_file: Source file name
    
    Returns:
        list: List of database rows
    """
    from models.model import Schedule, OathForm, TableSection, ScheduleEntry
    
    rows = []
    schedule_name = schedule.name
    
    # Process parts within the schedule
    for part in schedule.parts:
        part_name = part.part_name
        
        for content_block in part.content_blocks:
            if isinstance(content_block, TableSection):
                rows.extend(process_table_section(content_block, schedule_name, part_name, source_file))
            elif isinstance(content_block, ScheduleEntry):
                rows.extend(process_schedule_entry(content_block, schedule_name, part_name, source_file))
    
    # Process flat entries
    for entry in schedule.flat_entries:
        if isinstance(entry, OathForm):
            rows.extend(process_oath_form(entry, schedule_name, None, source_file))
        elif isinstance(entry, ScheduleEntry):
            rows.extend(process_schedule_entry(entry, schedule_name, None, source_file))
    
    return rows


def process_part(part: Part , source_file: str) -> list:
    """
    Process a Part object into database rows.
    
    Args:
        part: Part dataclass instance
        source_file: Source file name
    
    Returns:
        list: List of database rows
    """
    from models.model import Part
    
    rows = []
    part_name = part.name
    
    # Process articles directly under part
    for article in part.articles:
        rows.extend(process_constitution_article(article, part_name, None, source_file))
    
    # Process chapters
    for chapter in part.chapters:
        chapter_name = chapter.name
        for article in chapter.articles:
            rows.extend(process_constitution_article(article, part_name, chapter_name, source_file))
    
    return rows
