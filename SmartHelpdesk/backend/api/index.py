import os, sys

# Add nested path to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # root
NESTED = os.path.join(BASE_DIR,  "SmartHelpDesk", "SmartHelpdesk.","backend")
if NESTED not in sys.path:
    sys.path.append(NESTED)

from app.main import app  # because we appended path pointing at backened/app


# Expose your FastAPI app to Vercel's Python runtime

# Try both import paths depending on your chosen project root.
# If your Vercel Project Root is set to "SmartHelpdesk/backend", the first import works.
# If your Project Root is the repo root, the second import works.

try:
    from app.main import app as fastapi_app  # when root is SmartHelpdesk/backend
except ImportError:
    from SmartHelpdesk.backend.app.main import app as fastapi_app  # when root is repo root

# Vercel looks for a top-level ASGI callable named "app"
app = fastapi_app
