"""Run Giskard LLM Scan — used in CI/CD pipeline."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import giskard
import pandas as pd

from src.model import model_predict


def main():
    # Configure Giskard LLM backend
    giskard.llm.set_llm_model("gpt-4o")
    giskard.llm.set_embedding_model("text-embedding-3-small")

    # Wrap model for Giskard
    giskard_model = giskard.Model(
        model=model_predict,
        model_type="text_generation",
        name="TechCorp Customer Support Assistant",
        description=(
            "AI assistant for product support, billing inquiries, and "
            "technical troubleshooting. Must not reveal internal policies."
        ),
        feature_names=["question"],
    )

    # Run automated vulnerability scan
    print("Running Giskard LLM Scan...")
    scan_results = giskard.scan(giskard_model)

    # Save report
    os.makedirs("outputs", exist_ok=True)
    scan_results.to_html("outputs/scan_report.html")
    print(f"Scan report saved to outputs/scan_report.html")

    # Print summary
    print(f"\n{'='*60}")
    print(f"SCAN RESULTS: {len(scan_results.issues)} issues detected")
    print(f"{'='*60}")
    for issue in scan_results.issues:
        print(f"  [{issue.level.upper()}] {issue.group}: {issue.description}")

    # Fail CI if major issues found
    major_issues = [i for i in scan_results.issues if i.level == "major"]
    if major_issues:
        print(f"\nFAILED: {len(major_issues)} major vulnerabilities found")
        sys.exit(1)

    print("\nPASSED: No major vulnerabilities detected")
    return scan_results


if __name__ == "__main__":
    main()
