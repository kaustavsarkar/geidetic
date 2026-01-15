#!/usr/bin/env python3

import argparse
import json
import os
import random
import re
from dataclasses import dataclass
from typing import List, Dict, Any, Sequence, Tuple
from parsers.ex_schedules import parse_schedules
from parsers.schedules import extract_schedules
from sections import Article, FrontMatter, Schedule, Section
from parsers.front_matter import extract_front_matter
from parsers.articles import split_articles
from prompts import make_prompt

from tqdm import tqdm

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from model_manager import load_model_with_cache
from pdf_loader import load_text, load_multiple_texts, get_pdf_files_from_directory

# Regex patterns
ARTICLE_REGEX = re.compile(r"(?m)^(\[?\d+[A-Z]?\]?\.?)\s+(.*)")
AMEND_INLINE = re.compile(r"\[(.*?)\]")
AMEND_FOOTNOTE = re.compile(r"\(As amended.*?\)", re.IGNORECASE)
PART_REGEX = re.compile(r"(?im)\bPart\s+([IVXLCDM]+)\b\s*(?:\(([^)]*)\))?")
AMEND_DATE = re.compile(r"(\d{4})")
PREAMBLE_REGEX = re.compile(r"WE,\s+THE PEOPLE OF INDIA.*?THIS CONSTITUTION\.", re.DOTALL | re.IGNORECASE)
INTRO_HEADER_REGEX = re.compile(r"THE CONSTITUTION OF INDIA", re.IGNORECASE)

def normalize_whitespace(s: str) -> str:
    s = re.sub(r"\u00a0", " ", s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\s*\n\s*", "\n", s)
    return s.strip()


# Removed old load_model function as it's now handled by model_manager
def generate(model, tok, prompt: str, device: str, max_new_tokens=384, temperature=0.2, top_p=0.9) -> str:
    """
    Generate text from either a llama_cpp.Llama instance (when tok is None) or a
    Hugging Face transformers model/tokenizer pair.
    """
    # llama.cpp path: tokenizer is managed internally, model exposes create_completion
    if tok is None and hasattr(model, "create_completion"):
        # llama_cpp expects max_tokens (new tokens to generate)
        resp = model.create_completion(
            prompt=prompt,
            max_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
        )
        # response text is in resp['choices'][0]['text']
        text = resp.get("choices", [{}])[0].get("text", "")
        parts = text.split("[RESPONSE]")
        return parts[-1].strip() if parts else text.strip()

    # Transformers path
    inputs = tok(prompt, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=temperature,
            top_p=top_p,
            eos_token_id=tok.eos_token_id,
        )
    text = tok.decode(out[0], skip_special_tokens=True)
    resp = text.split("[RESPONSE]")
    return resp[-1].strip() if resp else text.strip()

def parse_amendments_timeline(amendments: List[str]) -> List[Dict[str, Any]]:
    timeline = []
    for a in amendments:
        year_match = AMEND_DATE.search(a)
        year = int(year_match.group(1)) if year_match else None
        timeline.append({
            "text": a.strip(),
            "year": year
        })
    timeline.sort(key=lambda x: (x["year"] or 9999))
    return timeline

def build_records(articles: Sequence[Section], tasks: List[str], model_id: str, local_dir: str, device: str,
                  max_articles: int, seed: int, progress: bool=True) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    random.seed(seed)
    if max_articles:
        articles = articles[:max_articles]

    tok, model = load_model_with_cache(model_id, local_dir, device)

    # introduction_records: list[Dict[str, Any]] = []
    # preamble_records: list[Dict[str, Any]] = []
    records: list[Dict[str, Any]] = []
    amendment_records: list[Dict[str, Any]] = []
    timeline_records: list[Dict[str, Any]] = []
    schedules: list[Dict[str, Any]] = []

    it = tqdm(articles, desc="Generating", disable=not progress)
    for art in it:
        for task in tasks:
            prompt = make_prompt(task, art)
            output = generate(model, tok, prompt, device=device)

            rec = {
                "instruction": task,
                "input": f"Part: {art.part or 'Unknown'}\nArticle {art.number}: {art.heading}\n\n{art.text}\nAmendments: {art.amendments}",
                "output": output,
                "meta": {
                    "task": task,
                    "article_number": art.number,
                    "heading": art.heading,
                    "part": art.part,
                    "amendments": art.amendments,
                    "model": model_id,
                },
            }
            # if art.number == "Introduction":
            #     introduction_records.append(rec)
            # if art.number == "Preamble":
            #     preamble_records.append(rec)
            records.append(rec)

            if task == "amendments" and art.amendments:
                amendment_records.append(rec)
                timeline_records.append({
                    "article_number": art.number,
                    "heading": art.heading,
                    "part": art.part,
                    "timeline": parse_amendments_timeline(art.amendments)
                })

    return records, amendment_records, timeline_records

def write_jsonl(path: str, records: List[Dict[str, Any]]):
    path = os.path.join("training_data", path)
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

def split_train_eval(records: List[Dict[str, Any]], eval_ratio: float = 0.1, seed: int = 42):
    random.Random(seed).shuffle(records)
    n_eval = int(len(records) * eval_ratio)
    return records[n_eval:], records[:n_eval]

def main():
    os.environ["HF_TOKEN"] = ""
    ap = argparse.ArgumentParser(description="Generate SFT data from Constitution PDFs")
    
    # Input arguments - either multiple files or a directory
    input_group = ap.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--input", nargs="+", help="One or more PDF/TXT files to process")
    input_group.add_argument("--input_dir", help="Directory containing PDF files")
    ap.add_argument("--input_section", default="introduction", choices=["introduction", "preamble", "articles", "schedules"])
    ap.add_argument("--model", default="meta-llama/Llama-3.2-1B-Instruct")
    ap.add_argument("--device", default="cpu", choices=["cpu", "cuda"]) 
    ap.add_argument("--local_model_dir", default="./local_models", help="Directory to save/load models locally")
    ap.add_argument("--out", default="sft_constitution.jsonl")
    ap.add_argument("--out_train", default="sft_constitution.train.jsonl")
    ap.add_argument("--out_eval", default="sft_constitution.eval.jsonl")
    ap.add_argument("--amend_out", default="amendments.jsonl")
    ap.add_argument("--amend_timeline_out", default="amendments_timeline.jsonl")
    ap.add_argument("--tasks", nargs="+", default=["summary", "faq", "json", "extract_rewrite", "amendments"])
    ap.add_argument("--max_articles", type=int, default=0)
    ap.add_argument("--eval_ratio", type=float, default=0.1)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--debug", action="store_true", help="Print debug information")
    args = ap.parse_args()

    # Determine input files
    if args.input:
        input_files = args.input
    else:
        print("No input files specified. Searching directory...", args.input_dir)
        input_files = get_pdf_files_from_directory(args.input_dir)
    
    if not input_files:
        raise SystemExit("No input files found.")
    
    print(f"Processing {len(input_files)} file(s)...")
    
    # Load and combine all texts
    raw = load_multiple_texts(input_files)
    
    if args.debug:
        print(f"\n=== First 1000 characters of combined text ===")
        print(raw[:1000])
        print("\n" + "="*50 + "\n")
    
    # Extract front matter and articles
    front: Sequence[Section] = list()
    articles: Sequence[Section] = list()
    schedules: Sequence[Section] = list()
    print(f"Input section: {args.input_section == 'introduction'}")
    if args.input_section == "introduction" or args.input_section == "preamble":
        print("Extracting front matter...", raw[:100])
        front = extract_front_matter(raw)
        print(f"Extracted {len(front)} front matter sections.")
    if args.input_section == "articles":
        articles = split_articles(raw)
    if args.input_section == "schedules":
        schedules = parse_schedules(raw)
        print(f"Extracted {len(schedules)} schedule sections.")
        
    return

    print(f"Debug mode: {args.debug}")

    if args.debug:
        print(f"\n=== Front matter sections: {len(front)} ===")
        for f in front:
            print(f"  - {f.number}: {f.heading}")
        print(f"\n=== First 10 articles ===")
        for a in articles[:10]:
            print(f"  - Article {a.number}: {a.heading} (Part {a.part})")
        print("\n" + "="*50 + "\n")
    
    all_articles: List[Section] = list(front) + list(articles) + list(schedules)
    if not all_articles:
        raise SystemExit("No articles or front matter detected. Check input formatting and regex.")

    print(f"Detected {len(all_articles)} sections (front matter + articles).")
    records, amendment_records, timeline_records = build_records(
        articles=all_articles,
        tasks=args.tasks,
        model_id=args.model,
        local_dir=args.local_model_dir,
        device=args.device,
        max_articles=args.max_articles,
        seed=args.seed,
    )

    write_jsonl(args.out, records)
    train, eval_ = split_train_eval(records, eval_ratio=args.eval_ratio, seed=args.seed)
    write_jsonl(args.out_train, train)
    write_jsonl(args.out_eval, eval_)
    

    if amendment_records:
        write_jsonl(args.amend_out, amendment_records)
        print(f"Wrote {len(amendment_records)} amendment records → {args.amend_out}")

    if timeline_records:
        write_jsonl(args.amend_timeline_out, timeline_records)
        print(f"Wrote {len(timeline_records)} amendment timeline records → {args.amend_timeline_out}")

    print(f"Wrote {len(records)} records → {args.out}\nTrain: {len(train)} → {args.out_train}\nEval: {len(eval_)} → {args.out_eval}")

if __name__ == "__main__":
    main()