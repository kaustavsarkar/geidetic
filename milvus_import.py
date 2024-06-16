import concurrent.futures
import os
import threading

from pymilvus import model, MilvusClient, FieldSchema, CollectionSchema, DataType
from pymilvus.model.dense import SentenceTransformerEmbeddingFunction
import re
from milvus import default_server
from tqdm import tqdm

sentence_transformer_ef = SentenceTransformerEmbeddingFunction(
    # model_name='all-mpnet-base-v2',  # Specify the model name
    model_name='all-MiniLM-L6-v2',  # Specify the model name
    device='cpu',  # Specify the device to use, e.g., 'cpu' or 'cuda:0'
    batch_size=32,
    normalize_embeddings=True,
)


def doc_embeddings(pages):
    return sentence_transformer_ef.encode_documents(pages)


def query_embeddings(queries):
    return sentence_transformer_ef.encode_queries(queries)


mcli = MilvusClient()
collection_name = 'ain_source'
txt_output_dir = 'txt_data'
txt_files = os.listdir(txt_output_dir)
txt_files.sort()
milvus_lock = threading.Lock()


def insert_from_file(txt_path, fno, total):
    data = prepare_for_insert(txt_path)
    with milvus_lock:
        res = mcli.insert(collection_name=collection_name, data=data)
    print(f'({fno}/{total}) Inserted {res["insert_count"]} entries for {txt_path}')


def prepare_for_insert(txt_path):
    with open(txt_path, 'rt') as f:
        text = f.read()
    pages = text.split('##EOP##')
    fn: str = os.path.splitext(txt_path)[0]
    clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', fn.replace(' ', '_'))
    data = []
    doc_embs = doc_embeddings(pages)
    for i, page in enumerate(pages):
        data.append({'id': i, 'text': page, 'vector': doc_embs[i], 'name': clean_name})
    return data


def main():
    if mcli.has_collection(collection_name):
        mcli.drop_collection(collection_name=collection_name)

    test_txt = 'some test text for embedding adfafadfadfadfads'
    test_emb = doc_embeddings([test_txt])
    print(sentence_transformer_ef.dim)
    index_params = MilvusClient.prepare_index_params()
    index_params.add_index(
        field_name="vector",
        metric_type="IP",
        index_type="IVF_FLAT",
        index_name="vector_index",
        params={"nlist": 128},
    )
    mcli.create_collection(
        collection_name,
        dimension=sentence_transformer_ef.dim,
        auto_id=False,
        shards_num=2,
        index_params=index_params,
        metric_type='IP',
    )

    # all_data = []
    # for i, txt_file in tqdm(enumerate(txt_files)):
    #     path = os.path.join(txt_output_dir, txt_file)
    #     all_data.extend(prepare_for_insert(path))
    #     if i > 0 and i % 100 == 0:
    #         mcli.insert(collection_name=collection_name, data=all_data)
    #         all_data = []

    futures = []
    cnt = len(txt_files)
    for i, txt_file in enumerate(txt_files):
        path = os.path.join(txt_output_dir, txt_file)
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures.append(
                executor.submit(insert_from_file, path, i, cnt)
            )
    concurrent.futures.wait(futures)


if __name__ == '__main__':
    main()
