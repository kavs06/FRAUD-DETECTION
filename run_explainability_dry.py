"""Helper to run explainability.py in dry-run mode (DUMMY_KEY).

This script sets the environment variable inside the process to avoid shell quoting
issues and invokes the `main()` function from `explainability.py` with sample
arguments for quick local testing.
"""

import os
import sys

# Ensure we run with a safe dummy key to trigger the built-in dry-run behavior
os.environ["GOOGLE_API_KEY"] = "DUMMY_KEY"

from explainability import main

if __name__ == "__main__":
    # Provide sample args similar to CLI usage
    test_args = [
        "--provider-id",
        "PRV10019",
        "--prediction",
        "Fraud",
        "--probability",
        "0.948",
        "--top-features",
        "num_inpatient_claims,total_reimbursement,duplicate_claims",
        "--max-tokens",
        "600",
        "--dry-run",
    ]
    sys.exit(main(test_args))
