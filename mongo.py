import pymongo
from loguru import logger
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import sys
from datetime import datetime

DATABASE_NAME = "psw_manager"
CREDENTIALS_COLLECTION = "credentials"
VAULTS_COLLECTION = "vaults"
SALTS_COLLECTION = "salts"

class MongoMethods:

    def __init__(self) -> False:
        self.conn : pymongo.MongoClient = False
        self.psw_manager_database = False
        self.credentials_collection = False
        self.vaults_collection = False
        self.salts_collection = False

    def create_connection(self) -> pymongo.MongoClient:
        """
        Create a connection to local mongo.
        """
        try:
            logger.info("Trying to connect mongo at localhost:27017!")
            conn = pymongo.MongoClient("localhost", 27017)
            # Force connection -> error if not working
            conn.server_info()
            self.conn = conn
            logger.info("Mongo connection initialized!")
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f'MongoDB seems to be down? \n {e}')
            sys.exit()
        return conn
    
    def initialize_mongo(self):
        """
        Check mongo database and its collections. 
        Create psw_manager database if doesn't exist.
        Create collections if don't exist.
        """
        self.psw_manager_database = self.conn[DATABASE_NAME]
        self.credentials_collection = self.psw_manager_database[CREDENTIALS_COLLECTION]
        self.vaults_collection = self.psw_manager_database[VAULTS_COLLECTION]
        self.salts_collection = self.psw_manager_database[SALTS_COLLECTION]

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