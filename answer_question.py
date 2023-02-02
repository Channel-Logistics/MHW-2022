import openai
from openai.embeddings_utils import get_embedding

def create_context(question, index, mappings, max_len=3750, size="curie"):
    """
    Find most relevant context for a question via Pinecone search
    """
    q_embed = get_embedding(question, engine=f'text-search-{size}-query-001')
    res = index.query(q_embed, top_k=5, include_metadata=True)
    cur_len = 0
    contexts = []

    #TODO Convert vector embedding back to text
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

def answer_question(
    index,
    question,
    instruction="Answer the question based on the context below, and if the question can't be answered based on the context, say \"I don't know\"\n\nContext:\n{0}\n\n---\n\nQuestion: {1}\nAnswer:",
    fine_tuned_qa_model="text-davinci-002",
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