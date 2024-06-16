from langchain_huggingface import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFacePipeline
from langchain_core.prompts import PromptTemplate
from langchain_milvus import Milvus
from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from typing import List

model_name = 'all-MiniLM-L6-v2'
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': True}
hfe = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)
hfm = HuggingFacePipeline.from_model_id(
    model_id='microsoft/Phi-3-mini-128k-instruct',
    task='text-generation',
    # model_kwargs={'temperature':0},
    pipeline_kwargs={'max_new_tokens': 2000},
)

PROMPT_TEMPLATE = """
Human: You are an AI assistant, and provides answers to questions by using fact based and statistical information when possible.
Use the following pieces of information to provide a concise answer to the question enclosed in <question> tags.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
<context>
{context}
</context>

<question>
{question}
</question>

The response should be specific and use statistics or numbers when possible.

Assistant:"""

rag_prompt = PromptTemplate(
    template=PROMPT_TEMPLATE, input_variables=["context", "question"]
)
vector_store = Milvus(
    embedding_function=hfe,
    connection_args={'uri': 'http://localhost:19530'},
    auto_id=False,
    drop_old=False,
)
retriever = vector_store.as_retriever()


def format_docs(docs: List[Document]):
    return "\n\n".join(doc.page_content for doc in docs)


rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | rag_prompt
        | hfm
        | StrOutputParser()
)


query = 'have there been any cases involving Indian forest officers?'


if __name__ == '__main__':
    res = rag_chain.invoke(query)
    print(res)
