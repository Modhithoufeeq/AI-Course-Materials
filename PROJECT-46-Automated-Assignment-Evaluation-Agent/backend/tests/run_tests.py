import os
import sys

# Ensure backend root is in PYTHONPATH
sys.path.insert(0, os.path.abspath("."))
os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"

import pytest

if __name__ == "__main__":
    exit_code = pytest.main([
        "-v",
        "backend/tests"
    ])
    sys.exit(exit_code)
