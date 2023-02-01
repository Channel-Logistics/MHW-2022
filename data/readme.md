# Data info
## From a subset of AIS transciever data, embedding vectors are generated from ChatGPT embedding model="text-embedding-ada-002".  


***embedding.zip*** contains the following AIS data columns merged as a string.
df[["lat", "long", "sog", "cog", "timestamp", "mmsi"]]


***question-embeddings.zip*** contains the ChatGPT generated embeddings for the following questions.   

- 'df['question1'] = (
    "What is the average speed and direction of the oil tankers in the Blacksea where the speed is"+
    df.sog.astype(str)+ "in knots and the" +df.cog.astype(str)+"is the direction of travel in degrees")'.  
 
- 'df['question2'] = ("Which vessels, where vessel is " + df.mmsi.astype(str)+ " are in the area of the Blacksea where the area of the Blacksea is "+ df.Blacksea.astype(str)+ " and the vessel location is "+ df.lat.astype(str)+ df.long.astype(str)+ " on 05/14/2022,where the date is "+df.timestamp.astype(str)+"?")'''
 
