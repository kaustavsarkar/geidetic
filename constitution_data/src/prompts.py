from sections import Article, Section

def sys_prompt() -> str:
    return (
        "You are a careful legal assistant. You must ONLY use the provided article text and amendments. "
        "If the answer is not present, say 'insufficient context'."
    )

def make_prompt(task: str, a: Section) -> str:
    """
    Build task-specific prompts.

    Sections handled explicitly:
    - Introduction (pedagogical / historical)
    - Contents (structural, NOT legal)
    - Preamble (interpretive / philosophical)
    - Articles (legal / normative)
    """

    base = (
        f"[SYSTEM]\n{sys_prompt()}\n\n"
        f"[SECTION]\n{a.part} — {a.number}: {a.heading}\n\n"
        f"{a.text}\n"
    )

    if a.amendments:
        base += "\n[AMENDMENTS]\n" + "\n".join(a.amendments)

    # ================= INTRODUCTION =================
    if a.number == "Introduction":
        instructions = {
        "summary": (
            "Summarize the purpose of this Introduction, focusing on the edition details, "
            "amendment coverage, and how the official Constitution text has been updated."
        ),

        "faq": (
            "Generate 5 practical questions a legal researcher might ask about this "
            "Introduction (e.g., amendment coverage, appendices, authority of the text), "
            "with clear answers."
        ),

        "json": (
            "Extract a JSON with the following fields:\n"
            "- publication_year\n"
            "- edition_description\n"
            "- amendments_covered\n"
            "- issuing_authority\n"
            "- appendices_included\n"
            "- editorial_conventions"
        ),

        "extract_rewrite": (
            "Rewrite this Introduction in clear, professional language explaining how "
            "to use this edition of the Constitution for legal research."
        ),

        "amendments": (
            "Explain whether this Introduction itself is amended, and clarify how "
            "constitutional amendments are reflected in this edition."
        ),
    }

    # ================= CONTENTS =================
    elif a.number == "Contents":
        instructions = {
            "summary": "Explain what this Table of Contents reveals about the structure of the Constitution.",
            "faq": "Create 3 questions explaining how the Constitution is organised.",
            "json": (
                "Extract a JSON showing major Parts and the range of Articles they cover."
            ),
            "extract_rewrite": (
                "Rewrite this Contents section as a high-level roadmap of the Constitution."
            ),
            "amendments": (
                "State whether the Table of Contents itself is subject to amendments."
            ),
        }

    # ================= PREAMBLE =================
    elif a.number == "Preamble":
        instructions = {
            "summary": (
                "Summarize the core constitutional values expressed in the Preamble."
            ),
            "faq": (
                "Create 3 questions explaining how courts use the Preamble in constitutional interpretation."
            ),
            "json": (
                "Extract a JSON with values: sovereignty, socialism, secularism, democracy, "
                "republic, justice, liberty, equality, fraternity."
            ),
            "extract_rewrite": (
                "Rewrite the Preamble in modern, simple language without changing its meaning."
            ),
            "amendments": (
                "Describe how and when the Preamble was amended."
            ),
        }
    elif a.part == "Schedule":
        instructions = {
        "summary": (
            "Summarize the scope and contents of this Schedule factually, "
            "without interpretation."
        ),
        "faq": (
            "Create 3 factual questions explaining what this Schedule provides "
            "and where it applies."
        ),
        "json": (
            "Extract a JSON with fields: schedule_name, part, subject_matter, "
            "key_entries, related_articles."
        ),
        "extract_rewrite": (
            "Rewrite this Schedule section in clear, structured language "
            "suitable for reference."
        ),
        "amendments": (
            "Identify any amendment information mentioned in this Schedule. "
            "If none is present, state so explicitly."
        ),
    }

    # ================= ARTICLES (DEFAULT) =================
    elif a.number.startswith("Article"):
        instructions = {
            "summary": "Summarize this Article in 3–5 precise legal bullets.",
            "faq": "Create 3 legal FAQ-style questions and answers based on this Article.",
            "json": (
                "Extract a structured JSON with scope, rights_or_powers, limitations, "
                "exceptions, related_articles, amendments."
            ),
            "extract_rewrite": (
                "Rewrite this Article in plain English while preserving its legal meaning."
            ),
            "amendments": (
                "Summarize the amendment history of this Article chronologically."
            ),
        }

    if task not in instructions:
        raise ValueError(f"Unsupported task '{task}' for section '{a.number}'")

    return (
        base
        + f"\n\n[INSTRUCTION]\n{instructions[task]}\n\n[RESPONSE]"
    )
