"""
Launch the EMA Strategy Backtester dashboard.
Double-click this file or run: python run.py
"""
import subprocess
import sys
import os

if __name__ == "__main__":
    dashboard = os.path.join(os.path.dirname(__file__), "dashboard", "app.py")
    subprocess.run([sys.executable, "-m", "streamlit", "run", dashboard])
