import pymongo
from loguru import logger
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, ConfigurationError, OperationFailure
import sys
import os
import dotenv

dotenv.load_dotenv()
mongo_url = os.getenv("MONGO_URL")
mongo_port = int(os.getenv("MONGO_PORT"))
mongo_username = os.getenv("MONGO_USERNAME")
mongo_psw = os.getenv("MONGO_PSW")

DATABASE_NAME = "psw_manager"
CREDENTIALS_COLLECTION = "credentials"
VAULTS_COLLECTION = "vaults"
SALTS_COLLECTION = "salts"

class MongoMethods:

    def __init__(self):
        self.conn : pymongo.MongoClient = None
        self.psw_manager_database = None
        self.credentials_collection = None
        self.vaults_collection = None
        self.salts_collection = None

    def create_connection(self) -> pymongo.MongoClient:
        """
        Create a connection to local mongo.
        """
        try:
            if mongo_username and mongo_psw:
                logger.info(
                    f"Trying to connect mongo at {mongo_url}:{mongo_port} using provided credentials!"
                    )
                conn = pymongo.MongoClient(mongo_url, 
                                           mongo_port,
                                           username=mongo_username,
                                           password=mongo_psw)
            else:
                logger.info(
                    f"Trying to connect mongo at {mongo_url}:{mongo_port} without credentials!"
                    )
                conn = pymongo.MongoClient(mongo_url, mongo_port)
            self.conn = conn
            self.initialize_databases()
            logger.info("Mongo connection initialized!")
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f'MongoDB seems to be down? \n {e}')
            sys.exit()
        except ConfigurationError as e:
            logger.error(f"Wrong mongo credentials? \n {e}")
            sys.exit()
        except OperationFailure as e:
            logger.error(f"Wrong mongo credentials? \n {e}")
            sys.exit()
        return conn
    
    def initialize_databases(self):
        """
        Check mongo database and its collections. 
        Create psw_manager database if doesn't exist.
        Create collections if don't exist.
        """
        self.psw_manager_database = self.conn[DATABASE_NAME]
        self.credentials_collection = self.psw_manager_database[CREDENTIALS_COLLECTION]
        self.vaults_collection = self.psw_manager_database[VAULTS_COLLECTION]
        self.salts_collection = self.psw_manager_database[SALTS_COLLECTION]

        # Check that connection works
        self.psw_manager_database.list_collections()

    def get_credentials(self, username: str):
        try:
            return self.credentials_collection.find_one(
                {"username": username}), ""
        except ServerSelectionTimeoutError as e:
            logger.error(f'MongoDB seems to be down? \n {e}')
            return False, "Something went wrong. Is mongo up?"
        
    def add_credentials(self, username: str, hashed_psw: bytes) -> bool:
        try:
            return self.credentials_collection.insert_one(
                {"username": username, "psw": hashed_psw}), ""
        except ServerSelectionTimeoutError as e:
            logger.error(f'MongoDB seems to be down? \n {e}')
            return False, "Something went wrong. Is mongo up?"
        
    def add_vault(self, username: str, vault: bytes):
        try:
            return self.vaults_collection.insert_one(
                {"username": username, "vault": vault}), ""
        except ServerSelectionTimeoutError as e:
            logger.error(f'MongoDB seems to be down? \n {e}')
            return False, "Something went wrong. Is mongo up?"

    def get_vault(self, username: str):
        try:
            return self.vaults_collection.find_one(
                {"username": username}), ""
        except ServerSelectionTimeoutError as e:
            logger.error(f'MongoDB seems to be down? \n {e}')
            return False, "Something went wrong. Is mongo up?"

    def update_vault(self, username: str, vault: bytes):
        try:
            return self.vaults_collection.update_one(
                {"username": username}, {"$set": {"vault": vault}}), ""
        except ServerSelectionTimeoutError as e:
            logger.error(f'MongoDB seems to be down? \n {e}')
            return False, "Something went wrong. Is mongo up?"

    def get_salt(self, hash: str): 
        try:
            return self.salts_collection.find_one({"hash": hash}), ""
        except ServerSelectionTimeoutError as e:
            logger.error(f'MongoDB seems to be down? \n {e}')
            return False, "Something went wrong. Is mongo up?"
    
    def add_salt(self, hash: str, salt: bytes):
        try:
            return self.salts_collection.insert_one(
                {"hash": hash, "salt": salt}), ""
        except ServerSelectionTimeoutError as e:
            logger.error(f'MongoDB seems to be down? \n {e}')
            return False, "Something went wrong. Is mongo up?"
        
mongo = MongoMethods()