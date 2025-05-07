#!/usr/bin/env python3
"""Helper script to run examples with proper module resolution."""

import os
import sys
import importlib.util
import importlib.machinery

# Add the current directory to the path so 'src' is importable
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def run_example(example_name):
    """Run the specified example script."""
    example_path = f"examples/{example_name}.py"
    
    if not os.path.exists(example_path):
        print(f"Error: Example '{example_name}' not found at {example_path}")
        return
    
    # Load the example module
    loader = importlib.machinery.SourceFileLoader(example_name, example_path)
    spec = importlib.util.spec_from_loader(example_name, loader)
    module = importlib.util.module_from_spec(spec)
    
    # Execute the module
    loader.exec_module(module)
    
    # Run the main function if it exists
    if hasattr(module, 'main'):
        module.main()
    else:
        print(f"Warning: Example '{example_name}' does not have a main() function")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run_example.py <example_name>")
        print("Available examples:")
        for example in os.listdir("examples"):
            if example.endswith(".py"):
                print(f"  {example[:-3]}")
        sys.exit(1)
    
    example_name = sys.argv[1]
    run_example(example_name)