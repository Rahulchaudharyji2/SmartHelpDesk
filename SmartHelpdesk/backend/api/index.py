import os, sys

# Add nested path to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # root
NESTED = os.path.join(BASE_DIR, "backened")
if NESTED not in sys.path:
    sys.path.append(NESTED)

from app.main import app  # because we appended path pointing at backened/app
