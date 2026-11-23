import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "logs"), exist_ok=True)
