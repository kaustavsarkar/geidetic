import json

from pymilvus import model, MilvusClient, FieldSchema, CollectionSchema, DataType
from pymilvus.model.dense import SentenceTransformerEmbeddingFunction
import re
from milvus import default_server
from tqdm import tqdm
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

sentence_transformer_ef = SentenceTransformerEmbeddingFunction(
    # model_name='all-mpnet-base-v2',  # Specify the model name
    model_name='all-MiniLM-L6-v2',  # Specify the model name
    device='cpu',  # Specify the device to use, e.g., 'cpu' or 'cuda:0'
    batch_size=32,
    normalize_embeddings=True,
)
collection_name = 'ain_source'


def query_embeddings(queries):
    return sentence_transformer_ef.encode_queries(queries)


torch.random.manual_seed(0)

llm = AutoModelForCausalLM.from_pretrained(
    "microsoft/Phi-3-mini-128k-instruct",
    torch_dtype="auto",
    trust_remote_code=True,
)
tokenizer = AutoTokenizer.from_pretrained("microsoft/Phi-3-mini-128k-instruct")

PROMPT = """
You are an AI assistant, and provides answers to questions by using fact based and statistical information when possible.
Use the following pieces of information to provide a concise answer to the question enclosed in <question> tags.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
<context>
{context}
</context>

<question>
{question}
</question>

The response should be specific and use statistics or numbers when possible.
You MUST provide references/citations at the end of your response, these can be found in the context given above.
"""

pipe = pipeline(
    "text-generation",
    model=llm,
    tokenizer=tokenizer,
)

generation_args = {
    "max_new_tokens": 2000,
    "return_full_text": False,
    "temperature": 0.0001,
    "do_sample": True,
}


def main():
    query = 'have there been any cases involving Indian forest officers? have there been any SCC citations?'

    mcli = MilvusClient()
    res = mcli.search(
        collection_name=collection_name,
        data=[
            query_embeddings([query])[0]
        ],
        limit=3,
        search_params={'metric_type': 'IP'},
        output_fields=['text', 'name'],
    )
    # print(f'res: {res}')

    raw_context = [
        (r["entity"]["text"], r['entity']['name'], r["distance"]) for r in res[0]
    ]
    # print(json.dumps(raw_context, indent=4))

    context = []
    for ctx in raw_context:
        txt = ctx[0]
        ref = f'reference/source: {ctx[1]}'
        entry = '\n'.join([txt, ref])
        context.append(entry)

    content = PROMPT.format(context='\n'.join(context), question=query)
    messages = [
        {"role": "user",
         "content": content},
    ]
    # print(json.dumps(content))
    output = pipe(messages, **generation_args)
    print(output[0]['generated_text'])


if __name__ == '__main__':
    main()
