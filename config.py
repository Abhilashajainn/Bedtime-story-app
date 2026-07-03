"""
Shared configuration: loads environment variables, holds the model constants,
and creates the single OpenAI client every other module imports.
"""

import os

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # reads OPENAI_API_KEY out of a local .env file, if present

MODEL = "gpt-3.5-turbo"  # unchanged, per assignment instructions
MAX_REVISIONS = 2         # how many judge-driven rewrite passes we allow
PASS_THRESHOLD = 8        # judge score (1-10) needed to stop revising

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # reads key from env; never hard-code it