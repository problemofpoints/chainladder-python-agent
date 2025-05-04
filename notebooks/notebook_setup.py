"""Helper module to set up paths for Jupyter notebooks in the chainladder-python-agent project.

This module adds the project root to the Python path, making local imports work correctly.
"""
import os
import sys

def setup_notebook_path():
    """Add the project root to the Python path.
    
    This ensures that imports of local modules like 'chainladder_agent' work correctly
    regardless of where the notebook is located in the project structure.
    """
    # Get the absolute path to this file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Get the project root (parent directory of the notebooks directory)
    project_root = os.path.abspath(os.path.join(current_dir, '..'))
    
    # Add project root to the path if it's not already there
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        print(f"Added {project_root} to Python path")
    else:
        print(f"{project_root} already in Python path")
    
    return project_root

# When imported, automatically set up the path
project_root = setup_notebook_path()
