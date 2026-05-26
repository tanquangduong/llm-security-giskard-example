"""Run Giskard RAGET evaluation for RAG pipeline."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import giskard
import pandas as pd
from giskard.rag import KnowledgeBase, generate_testset, evaluate

from src.model import call_llm_with_context
from src.retrieval import retrieve_documents, load_knowledge_base


def rag_answer_fn(question: str, history=None) -> str:
    """RAG pipeline — retrieves context and generates answer."""
    kb_df = load_knowledge_base()
    context = retrieve_documents(question, kb_df)
    return call_llm_with_context(question, context)


def main():
    # Configure Giskard LLM backend
    giskard.llm.set_llm_model("gpt-4o")
    giskard.llm.set_embedding_model("text-embedding-3-small")

    # Load knowledge base
    documents_df = load_knowledge_base()
    print(f"Loaded {len(documents_df)} documents from knowledge base")

    # Create Giskard KnowledgeBase
    knowledge_base = KnowledgeBase.from_pandas(
        documents_df, columns=["content", "title"]
    )

    # Generate test questions
    print("Generating RAGET test questions...")
    testset = generate_testset(
        knowledge_base,
        num_questions=30,
        language="en",
        agent_description=(
            "TechCorp customer support chatbot that answers "
            "product and billing questions based on internal documentation"
        ),
    )

    # Save testset
    os.makedirs("outputs", exist_ok=True)
    testset.save("outputs/techcorp_rag_testset.jsonl")
    print(f"Test set saved to outputs/techcorp_rag_testset.jsonl")

    # Evaluate
    print("Running RAGET evaluation...")
    report = evaluate(
        rag_answer_fn,
        testset=testset,
        knowledge_base=knowledge_base,
    )

    # Print results
    print(f"\n{'='*60}")
    print("RAG EVALUATION RESULTS")
    print(f"{'='*60}")
    if hasattr(report, "component_scores"):
        print("Component Scores:")
        for component, score in report.component_scores.items():
            print(f"  {component}: {score}")

    if hasattr(report, "correctness_by_question_type"):
        print("\nCorrectness by Question Type:")
        for qtype, score in report.correctness_by_question_type().items():
            print(f"  {qtype}: {score:.1%}")

    return report


if __name__ == "__main__":
    main()
