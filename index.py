import pinecone

def load_index(index):
    pinecone.init(
        api_key='554cd5ba-ec05-459a-afac-d07511e7ae53',
        environment='us-east1-gcp'
    )
    if not index in pinecone.list_indexes():
        raise KeyError(f"Index '{index}' does not exist.")
    return pinecone.Index(index)


def create_mappings(df):
    return {row['id']: row['text'] for _, row in df[['id', 'text']].iterrows()}

