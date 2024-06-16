## RAG POC for AIN Q&A

This is a POC, please do not expect polish.

### Prereqs

- docker
- docker-compose
- Python packages:
  - `pip install pymupdf langdetect`
  - `pip install milvus pymilvus "pymilvus[model]"`
  - `pip install sentence_transformers`
  - `pip install git+https://github.com/huggingface/transformers`
  - `pip install tf-keras torch tqdm`

### Running the POC

1. Extract text data from PDF files if not already done (NOTE: ADJUST THE DIRECTORY PATHS IN THE SCRIPT BEFORE RUNNING)

```shell
$ python txt_extractor.py
```

2. Start the Milvus stack (from the directory where `docker-compose.yaml` is present)

```shell
$ docker-compose up
```

3. Import extracted text into the Milvus server

```shell
$ python milvus_import.py
```

4. Edit `sample_poc_rag.py` to set your `query` and run it.

```shell
$ python sample_poc_rag.py
```
