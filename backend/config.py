import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
basedir = os.path.abspath(os.path.dirname(__file__))
QDRANT_PATH = os.path.join(basedir, "../vector-db/qdrant_data")
