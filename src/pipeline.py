"""End-to-end guarded LLM pipeline."""

from src.model import call_llm_with_context
from src.retrieval import retrieve_documents, load_knowledge_base
from src.guards import screen_input, screen_output
from src.metrics import SecurityMetrics


class GuardedLLMPipeline:
    """LLM pipeline with Guards protection informed by Scan results."""

    def __init__(self, kb_path: str = "data/techcorp_knowledge_base.csv"):
        self.kb_df = load_knowledge_base(kb_path)
        self.metrics = SecurityMetrics()

    def process(self, user_message: str) -> dict:
        """Process a user message through the full guarded pipeline.

        Returns dict with 'response', 'blocked', 'block_reason', 'stage'.
        """
        # ─── STEP 1: Input Guard (blocks jailbreaks found by Scan) ───
        try:
            input_screen = screen_input(user_message)
            self.metrics.log_event(input_screen, "input")
            if input_screen.get("blocked"):
                return {
                    "response": "I'm sorry, I can't help with that request.",
                    "blocked": True,
                    "block_reason": "input_guard",
                    "stage": "input_screening",
                    "guard_result": input_screen,
                }
        except Exception as e:
            # If Guards API is unavailable, log and continue (fail-open or fail-closed)
            print(f"Warning: Input guard failed: {e}")

        # ─── STEP 2: RAG Retrieval ───
        context = retrieve_documents(user_message, self.kb_df)

        # ─── STEP 3: LLM Generation ───
        response = call_llm_with_context(user_message, context)

        # ─── STEP 4: Output Guard (blocks hallucinations found by RAGET) ───
        try:
            output_screen = screen_output(user_message, response, context)
            self.metrics.log_event(output_screen, "output")
            if output_screen.get("blocked"):
                return {
                    "response": (
                        "I'm not confident in my answer. "
                        "Please check our documentation or contact support."
                    ),
                    "blocked": True,
                    "block_reason": "output_guard",
                    "stage": "output_screening",
                    "guard_result": output_screen,
                }
        except Exception as e:
            print(f"Warning: Output guard failed: {e}")

        return {
            "response": response,
            "blocked": False,
            "block_reason": None,
            "stage": "complete",
        }
