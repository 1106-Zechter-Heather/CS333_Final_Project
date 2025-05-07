"""Configure pytest for this project."""
import os
import sys

# Add the project root directory to the Python path
# This ensures that the 'src' module can be imported in tests
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))