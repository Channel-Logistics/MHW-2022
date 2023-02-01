
import openai
from openai.embeddings_utils import get_embedding

import pandas as pd
import numpy as np
import pyarrow
import pinecone

from transformers import GPT2TokenizerFast

from sys import getsizeof
from tqdm.auto import tqdm
import json
import time



tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
df = pd.read_csv('./drug-side-effects.csv')
df = df[["drug_name","medical_condition", "side_effects"]]
df = df.dropna()
df = df.assign(questions=lambda x: "what is the side effect of taking drug " + x.drug_name + "for the " + x.medical_condition + " medical condition.")
questions = df.pop('questions')
df.insert(2, 'questions', questions)
df.rename(columns = {'side_effects':'context'}, inplace = True)
df['text'] = "Topic: " + df.drug_name + " - " + df.medical_condition + "; Question: " + df.medical_condition + " - " + df.questions + "; Answer: " + df.context
df['n_tokens'] = df.text.apply(lambda x: len(tokenizer.encode(x)))

df.head()

df.n_tokens.hist(bins=100, log=True)

df = df[df.n_tokens < 2000]

openai.api_key = '<>'
model = 'curie'
count = 0
embed_array = []
for index, row in df.iterrows():
    count += 1
    embed_array.append(get_embedding(row['text'], engine=f'text-search-{model}-doc-001'))
    if count == 50:
        time.sleep(62)
        count = 0 
    
df.insert(6, "embeddings", embed_array, True)       
df.to_parquet('/Users/rajthith/openai/curie_embeddings.parquet')
df.head()



df1 = pd.read_parquet('./curie_embeddings.parquet')
df1.head()


too_big = []

for text in df['text'].tolist():
    if getsizeof(text) > 5000:
        too_big.append((text, getsizeof(text)))

print(f"{len(too_big)} / {len(df)} records are too big")


df['id'] = [str(i) for i in range(len(df))]
df.head()

pinecone.init(
    api_key='<>', 
    environment='us-west1-gcp'
)

index_name = 'chatgpt-demo'

if not index_name in pinecone.list_indexes():
    pinecone.create_index(
        index_name, dimension=len(df['embeddings'].tolist()[0]),
        metric='cosine'
    )

index = pinecone.Index(index_name)


batch_size = 32

for i in tqdm(range(0, len(df), batch_size)):
    i_end = min(i+batch_size, len(df))
    df_slice = df.iloc[i:i_end]
    to_upsert = [
        (
            row['id'],
            row['embeddings'],
            {
                'drug_name': row['drug_name'],
                'medical_condition': row['medical_condition'],
                'n_tokens': row['n_tokens']
            }
        ) for _, row in df_slice.iterrows()
    ]
    index.upsert(vectors=to_upsert)

    mappings = {row['id']: row['text'] for _, row in df[['id', 'text']].iterrows()}


    with open('./mapping.json', 'w') as fp:
        json.dump(mappings, fp)


    def load_index():
        pinecone.init(
            api_key='<>',  # app.pinecone.io
            environment='us-west1-gcp'
        )

        index_name = 'chatgpt-demo'

        if not index_name in pinecone.list_indexes():
            raise KeyError(f"Index '{index_name}' does not exist.")

        return pinecone.Index(index_name)


if __name__=='__main__':
    pass

index = load_index()

def create_context(question, index, max_len=3750, size="curie"):
    """
    Find most relevant context for a question via Pinecone search
    """
    q_embed = get_embedding(question, engine=f'text-search-{size}-query-001')
    res = index.query(q_embed, top_k=5, include_metadata=True)
    

    cur_len = 0
    contexts = []

    for row in res['matches']:
        text = mappings[row['id']]
        cur_len += row['metadata']['n_tokens'] + 4
        if cur_len < max_len:
            contexts.append(text)
        else:
            cur_len -= row['metadata']['n_tokens'] + 4
            if max_len - cur_len < 200:
                break
    return "\n\n###\n\n".join(contexts)

create_context("what is the side effect of taking drug doxycycline for Acne medical condition", index)

def answer_question(
    index=index,
    fine_tuned_qa_model="text-davinci-002",
    question="Do i get any side effect if I take ibuprofen?",
    instruction="Answer the question based on the context below, and if the question can't be answered based on the context, say \"I don't know\"\n\nContext:\n{0}\n\n---\n\nQuestion: {1}\nAnswer:",
    max_len=3550,
    size="curie",
    debug=False,
    max_tokens=400,
    stop_sequence=None,
):
    """
    Answer a question based on the most similar context from the dataframe texts
    """
    context = create_context(
        question,
        index,
        max_len=max_len,
        size=size,
    )
    if debug:
        print("Context:\n" + context)
        print("\n\n")
    try:
        # fine-tuned models requires model parameter, whereas other models require engine parameter
        model_param = (
            {"model": fine_tuned_qa_model}
            if ":" in fine_tuned_qa_model
            and fine_tuned_qa_model.split(":")[1].startswith("ft")
            else {"engine": fine_tuned_qa_model}
        )
        #print(instruction.format(context, question))
        response = openai.Completion.create(
            prompt=instruction.format(context, question),
            temperature=0,
            max_tokens=max_tokens,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=stop_sequence,
            **model_param,
        )
        return response["choices"][0]["text"].strip()
    except Exception as e:
        print(e)
        return ""

instructions = {
    "conservative Q&A": "Answer the question based on the context below, and if the question can't be answered based on the context, say \"I don't know\"\n\nContext:\n{0}\n\n---\n\nQuestion: {1}\nAnswer:",
    "paragraph about a question":"Write a paragraph, addressing the question, and use the text below to obtain relevant information\"\n\nContext:\n{0}\n\n---\n\nQuestion: {1}\nParagraph long Answer:",
    "bullet point": "Write a bullet point list of possible answers, addressing the question, and use the text below to obtain relevant information\"\n\nContext:\n{0}\n\n---\n\nQuestion: {1}\nBullet point Answer:",
    "summarize problems given a topic": "Write a summary of the problems addressed by the questions below\"\n\n{0}\n\n---\n\n",
    "just instruction": "{1} given the common questions and answers below \n\n{0}\n\n---\n\n",
    "summarize": "Write an elaborate, paragraph long summary about \"{1}\" given the questions and answers from a public forum on this topic\n\n{0}\n\n---\n\nSummary:",
}

