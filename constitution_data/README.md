## Create instruction-tuning (SFT) data from the Constitution text using Llama 3.2 1B Instruct.

Enhancements:
- Extracts Contents and Preamble sections from the PDF before Articles.
- Articles, Preamble, Contents, Amendments, and Timelines all included.
- Supports multiple PDF files (introduction, preamble, part_articles, schedules).

Outputs:
- sft_constitution.jsonl : all SFT records
- sft_constitution.train.jsonl / sft_constitution.eval.jsonl : split sets
- amendments.jsonl : only amendment SFT samples
- amendments_timeline.jsonl : timeline records (chronological amendments)

Usage:
```shell
poetry run python main.py \
  --input introduction.pdf preamble.pdf part_articles.pdf schedules.pdf \
  --model meta-llama/Llama-3.2-1B-Instruct \
  --out sft_constitution.jsonl \
  --amend_out amendments.jsonl \
  --amend_timeline_out amendments_timeline.jsonl \
  --max_articles 150 \
  --tasks summary faq json extract_rewrite amendments \
  --debug true \
  --seed 42
  ```

  ```shell
poetry run python main.py \
  --input_section schedules \
  --input data/schedules.pdf \
  --model local_models/Phi-3-mini-4k-instruct-q4.gguf \
  --out sft_constitution.jsonl \
  --amend_out amendments.jsonl \
  --amend_timeline_out amendments_timeline.jsonl \
  --max_articles 150 \
  --tasks summary faq json extract_rewrite amendments \
  --seed 42
  --debug True
  ```

Or use a directory:
```shell
python main.py \
  --input_dir ./data/ \
  --model microsoft/Phi-3-mini-4k-instruct \
  --out sft_constitution.jsonl
  ```