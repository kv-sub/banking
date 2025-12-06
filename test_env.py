import os
from dotenv import load_dotenv

# Explicitly load .env from the current directory
# load_dotenv(dotenv_path=r"C:\Users\kvsub\Dropbox\My PC (LAPTOP-2PNFQFS4)\Documents\HCLTECH - USECASE\Banking\.env")

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
print("OLLAMA_BASE =", os.getenv("OLLAMA_BASE"))
print("OLLAMA_MODEL =", os.getenv("OLLAMA_MODEL"))
