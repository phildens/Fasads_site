import os
from dotenv import load_dotenv
load_dotenv()
envir= os.getenv("STATIC_PATH")

print(envir)