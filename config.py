import os
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pathlib import Path
from urllib.parse import quote_plus
import dns.resolver

# Configure DNS to use Google's servers
dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = ['8.8.8.8', '8.8.4.4']

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / '.env')

class Config:
    MONGODB_USERNAME = os.getenv("MONGODB_USERNAME")
    MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
    MONGODB_CLUSTER = os.getenv("MONGODB_CLUSTER")
    DB = os.getenv("MONGODB_DB")
    
    if not all([MONGODB_USERNAME, MONGODB_PASSWORD, MONGODB_CLUSTER, DB]):
        raise RuntimeError("MongoDB environment variables are not set")
    
    # URL encode credentials
    username_encoded = quote_plus(MONGODB_USERNAME)
    password_encoded = quote_plus(MONGODB_PASSWORD)
    
    # Use SRV connection string (with Google DNS configured above)
    MONGO_URI = f"mongodb+srv://{username_encoded}:{password_encoded}@{MONGODB_CLUSTER}/?retryWrites=true&w=majority&appName=Cluster0"
    
    SECRET_KEY = os.getenv('SECRET_KEY', 'drivingforceofeducation')
    client = None
    
    @classmethod
    def get_client(cls):
        if cls.client is None:
            print(f"Connecting to: {cls.MONGODB_CLUSTER}")
            cls.client = MongoClient(
                cls.MONGO_URI,
                server_api=ServerApi('1'),
                serverSelectionTimeoutMS=30000,
                socketTimeoutMS=30000,
                connectTimeoutMS=30000
            )
            try:
                cls.client.admin.command('ping')
                print("✓ Successfully connected to MongoDB Atlas!")
            except Exception as e:
                print(f"✗ Connection failed: {e}")
                raise
        return cls.client
