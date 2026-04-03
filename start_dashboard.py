"""Wrapper to launch Streamlit dashboard with explicit package path."""
import sys

sys.path.insert(0, r"C:\Users\Mykhailo\AppData\Roaming\Python\Python314\site-packages")

from streamlit.web.cli import main

sys.argv = [
    "streamlit", "run", "dashboard/app.py",
    "--server.headless", "true",
    "--server.port", "8501",
]
main()
