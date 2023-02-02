import os
import pandas as pd
import openai
from openai.embeddings_utils import get_embedding
import numpy as np
import pyarrow
import pinecone
from transformers import GPT2TokenizerFast
from sys import getsizeof
from tqdm.auto import tqdm
import json
import time
import geopandas as gpd
import shapely
from typing import List
from index import load_index

def get_ada_embedding(text, model="text-embedding-ada-002"):
    text = text.replace("\n", " ")
    return openai.Embedding.create(input = [text], model=model)['data'][0]['embedding']

def build_embeddings(df):
    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
    df['n_tokens'] = df.text.apply(lambda x: len(tokenizer.encode(x)))

    model = 'curie'
    count = 0
    embed_array = []
    for index, row in df.iterrows():
        count += 1
        embed_array.append(get_embedding(row['text'], engine=f'text-search-{model}-doc-001'))
        if count == 50:
            time.sleep(62)
            count = 0
        
    df["embeddings"] = embed_array
    df.to_parquet('data/curie_embeddings.parquet')
    return df

def insert_embeddings(df, index):
    batch_size = 32
    for i in tqdm(range(0, len(df), batch_size)):
        i_end = min(i+batch_size, len(df))
        df_slice = df.iloc[i:i_end]
        to_upsert = [
            (
                row['id'],
                row['embeddings'].tolist(),
                {
                    'mmsi': row['mmsi'],
                    'date': row['date'],
                    'n_tokens': row['n_tokens']
                }
            ) for _, row in df_slice.iterrows()
        ]
        index.upsert(vectors=to_upsert)

def create_vectors_file(df):
    result = {"vectors": [{"id": row["id"], "metadata": {"mmsi": row["mmsi"], "date": row["date"], "n_tokens": row["n_tokens"]}, "values": row["embeddings"].tolist()} for _, row in df.iterrows()]}
    with open("data/vectors.json", "w") as f:
        f.write(json.dumps(result))

def main():
    df = pd.read_csv('data/ais_500.csv')
    df = df.dropna()
    df["combined"] = ("Latitude: " + df.lat.astype(str) + "; Longitude: " + df.long.astype(str)+"; Timestamp: " + df.timestamp.astype(str) + "; Vessel_id: " + df.mmsi.astype(str))
    df["mmsi"] = df["mmsi"].astype("str")

    black_sea_polygon = """POLYGON((41.501954197883606 41.40647995835556,42.01171875000001 41.81390371835323,41.66015625 42.750239247943995,41.29101723432541 43.200370822542624,40.4296875 43.31558594389247,38.63671928644181 44.64364438534287,37.652344554662704 44.78105523504854,37.3359377682209 45.265607783049376,36.597657054662704 45.5371364925241,36.5273442864418 45.27797881162647,36.246094554662704 45.12935464365077,35.7363286614418 45.19132852770056,35.279297679662704 45.178939096433226,35.1386721432209 44.99277476549506,34.52343776822091 44.88078499850664,34.0839846432209 44.543505260999666,33.69726642966271 44.618626019858084,33.8027349114418 45.01763135081822,33.5917966067791 45.3150740677238,33.92578125000001 46.34389377064005,31.0078127682209 46.94726205437263,29.7773440182209 46.00306696587131,28.880859911441803 45.672411397427425,27.720703259110454 45.6601271152588,28.2656255364418 45.11695173027687,28.177734911441803 43.60903503149538,27.210937365889553 42.814745459405884,26.701172143220905 42.25779683566509,27.474609240889556 41.45919517849495,28.5820309817791 41.04953099922517,30.181641429662708 40.87697221248803,31.6757820546627 40.943394408239214,32.7128903567791 41.59079665045235,34.9628908932209 41.709009264054345,36.6328127682209 41.009749867466695,38.9179690182209 40.810483302450905,40.359376072883606 40.757242936286815,41.501954197883606 41.40647995835556))"""

    df = df.assign(questions=lambda x: "Was the vessel " + x.mmsi + " in the black sea on " + x.date + ".")
    df["context"] = "yes"
    df['text'] = "Topic: " + df.mmsi + " - " + df.date + "; Question: " + df.date + " - " + df.questions + "; Answer: " + df.context

    df = df[["mmsi", "date", "questions", "context", "text"]]
    df['id'] = [str(i) for i in range(len(df))]
    mappings = {row['id']: row['text'] for _, row in df[['id', 'text']].iterrows()}

    df = build_embeddings(df)
    index = load_index("chat-ais")
    insert_embeddings(df, index)

if __name__=='__main__':
    main()