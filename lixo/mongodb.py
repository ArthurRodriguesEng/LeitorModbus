from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

class MongoDB():

    def __init__(self):

        uri = "mongodb+srv://SCADA_STEMIS:SCADA_STEMIS@cluster-tracker.nkl4scp.mongodb.net/?retryWrites=true&w=majority"
        # Create a new client and connect to the server
        self._client = MongoClient(uri, server_api=ServerApi('1'))
        # Send a ping to confirm a successful connection
        try:
            self._client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)

    def inserir(self,database,collection, data):

        # seleciona o banco de dados e a coleção
        db = self._client[database]
        collection = db[collection]

        collection.insert_one(data)
        # print(f"Inserted data with id: {result.inserted_id}")

