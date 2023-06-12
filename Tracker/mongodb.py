from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

class MongoDB():

    def __init__(self):
        
        uri = "mongodb+srv://TRACKER_ARTHUR:TRACKER_ARTHUR@cluster0.kk0vgjd.mongodb.net/"
        # Create a new client and connect to the server
        self._client = MongoClient(uri, server_api=ServerApi('1'))
        # Send a ping to confirm a successful connection
        try:
            self._client.admin.command('ping')
            #print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)

    def insert(self,database,collection,data):

        # seleciona o banco de dados e a coleção
        db = self._client[database]
        collection = db[collection]
        collection.insert_one(data)
        #print(f"Inserted data with id: {result.inserted_id}")

