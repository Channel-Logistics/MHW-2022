import pandas as pd
import openai
from openai.embeddings_utils import get_embedding
from prepare_embeddings import build_embeddings, insert_embeddings
from index import load_index, create_mappings
from answer_question import answer_question

def main(question:str):

    instructions = {
        "conservative Q&A": "Answer the question based on the context below, and if the question can't be answered based on the context, say \"I don't know\"\n\nContext:\n{0}\n\n---\n\nQuestion: {1}\nAnswer:",
        "paragraph about a question":"Write a paragraph, addressing the question, and use the text below to obtain relevant information\"\n\nContext:\n{0}\n\n---\n\nQuestion: {1}\nParagraph long Answer:",
        "bullet point": "Write a bullet point list of possible answers, addressing the question, and use the text below to obtain relevant information\"\n\nContext:\n{0}\n\n---\n\nQuestion: {1}\nBullet point Answer:",
        "summarize problems given a topic": "Write a summary of the problems addressed by the questions below\"\n\n{0}\n\n---\n\n",
        "just instruction": "{1} given the common questions and answers below \n\n{0}\n\n---\n\n",
        "summarize": "Write an elaborate, paragraph long summary about \"{1}\" given the questions and answers from a public forum on this topic\n\n{0}\n\n---\n\nSummary:",
    }

    index = load_index("chat_ais")
    response = answer_question(question, index, mappings)
    return response
    

if __name__=='__main__':
    openai.api_key = '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'
    question = input("Ask a question about maritime activity")
    main(question)




# too_big = []
# for text in df['text'].tolist():
#     if getsizeof(text) > 5000:
#         too_big.append((text, getsizeof(text)))
# print(f"{len(too_big)} / {len(df)} records are too big")

# sample['ada_embedding'] = sample.combined.apply(lambda x: get_embedding(x, model='text-embedding-ada-002'))

# @retry(wait=wait_random_exponential(min=1, max=50), stop=stop_after_attempt(6))
# def completion_with_backoff(**kwargs):
#     return openai.Embeddings.create(**kwargs)

# embeddings = completion_with_backoff(openai.Embedding.create(input = df.combined, model=model)['data'][0]['embedding']))

