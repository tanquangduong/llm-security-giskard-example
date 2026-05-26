# End-to-End LLM Security with Giskard: From Scan to Guards

A complete, runnable example demonstrating a **continuous security loop** for LLM applications using the Giskard ecosystem — from pre-deployment vulnerability discovery to runtime protection.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/VectoringAI/ai-engineering/blob/main/llm/end_to_end_llm_security_with_giskard.ipynb)

## Overview

This project implements the four-phase security loop:

```
┌─────────┐    ┌──────────┐    ┌──────────┐    ┌────────┐
│  SCAN   │───▶│ PROTECT  │───▶│ MONITOR  │───▶│ITERATE │──┐
│Giskard  │    │ Guards   │    │ Metrics  │    │Re-scan │  │
│Scan+RAG │    │ API      │    │ Tracking │    │+ Tests │  │
└─────────┘    └──────────┘    └──────────┘    └────────┘  │
     ▲                                                      │
     └──────────────────────────────────────────────────────┘
```

| Phase | Tool | Purpose |
|-------|------|---------|
| **Scan** | Giskard LLM Scan | Probe model for prompt injection, jailbreaks, toxicity |
| **Evaluate** | Giskard RAGET | Generate test questions for RAG and measure faithfulness |
| **Protect** | Giskard Guards API | Screen inputs/outputs at runtime with policies |
| **Iterate** | Test Suites + Logs | Convert findings into CI/CD tests |

---

## Project Structure

```
.
├── end_to_end_llm_security_with_giskard.ipynb  # 📓 Google Colab notebook (start here!)
├── requirements.txt                             # Python dependencies
├── data/
│   └── techcorp_knowledge_base.csv             # Sample knowledge base (15 docs)
├── src/
│   ├── __init__.py
│   ├── model.py          # LLM wrapper (OpenAI GPT-4o-mini)
│   ├── retrieval.py      # Simple RAG retrieval
│   ├── guards.py         # Giskard Guards API integration
│   ├── pipeline.py       # End-to-end guarded pipeline
│   └── metrics.py        # Security metrics tracking
├── scripts/
│   ├── run_scan.py       # CI/CD: Run Giskard vulnerability scan
│   ├── run_raget.py      # CI/CD: Run RAGET RAG evaluation
│   └── run_test_suite.py # CI/CD: Run adversarial test suite
└── .github/
    └── workflows/
        └── llm-security.yml  # GitHub Actions CI/CD workflow
```

---

## Quick Start (Google Colab)

The fastest way to run this end-to-end:

### Step 1: Open in Colab

Click the badge above or open `end_to_end_llm_security_with_giskard.ipynb` in Google Colab.

### Step 2: Set API Keys

In Colab, go to **🔑 Secrets** (key icon in left sidebar) and add:

| Secret Name | Required | Where to Get |
|-------------|----------|--------------|
| `OPENAI_API_KEY` | ✅ Yes | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) |
| `GISKARD_GUARDS_API_KEY` | Optional | [guards.giskard.cloud](https://guards.giskard.cloud) |

> **Note:** Without the Guards API key, the notebook uses simulated guardrail responses (still demonstrates the full workflow).

### Step 3: Run All Cells

Click **Runtime → Run all**. The notebook will:
1. Install dependencies (~1 min)
2. Run Giskard Scan on the model (~5-15 min)
3. Run RAGET evaluation (~3-5 min)
4. Test Guards protection
5. Show security metrics

---

## Local Setup

### Prerequisites

- Python 3.10+
- An OpenAI API key (for GPT-4o / GPT-4o-mini)
- (Optional) A Giskard Guards API key

### Step 1: Clone the Repository

```bash
git clone https://github.com/VectoringAI/llm-security-giskard-example.git
cd llm-security-giskard-example
```

### Step 2: Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Environment Variables

```bash
export OPENAI_API_KEY="sk-your-key-here"
export GISKARD_GUARDS_API_KEY="your-guards-key"  # Optional
```

Or create a `.env` file (don't commit this!):

```env
OPENAI_API_KEY=sk-your-key-here
GISKARD_GUARDS_API_KEY=your-guards-key
```

### Step 5: Run Individual Scripts

```bash
# Run the vulnerability scan
python scripts/run_scan.py

# Run RAG evaluation
python scripts/run_raget.py

# Run the adversarial test suite
python scripts/run_test_suite.py
```

### Step 6: Run the Notebook Locally

```bash
pip install jupyter
jupyter notebook end_to_end_llm_security_with_giskard.ipynb
```

---

## Detailed Walkthrough

### Phase 1: Giskard Scan — Vulnerability Discovery

The scan probes your model with adversarial inputs across categories:
- **Prompt Injection** — Can the model be hijacked?
- **Information Disclosure** — Does it leak system prompts?
- **Harmful Content** — Can it be tricked into generating harmful output?
- **Stereotypes & Bias** — Does it produce biased content?

```bash
python scripts/run_scan.py
```

Output: `outputs/scan_report.html` — a visual report of all detected vulnerabilities.

### Phase 1b: RAGET — RAG Evaluation

Tests your RAG pipeline with 6 question types:
- Simple, Complex, Distracting, Situational, Double, Conversational

```bash
python scripts/run_raget.py
```

Output: Component scores for Generator, Retriever, and Knowledge Base.

### Phase 2: Guards — Runtime Protection

Maps each vulnerability to a runtime detector:

| Vulnerability Found | Guard Detector | Action |
|--------------------|----------------|--------|
| Prompt injection | Known Attacks | Block |
| Info disclosure | Known Attacks + Guidelines | Block |
| Hallucination | Groundedness | Block |
| Off-topic drift | Task Adherence | Monitor |

### Phase 3: Monitor

The `SecurityMetrics` class tracks all screening events:
- Total screenings
- Block rate
- Input vs output blocks

### Phase 4: Iterate

Production blocks become new test cases → re-scan → tighten policies → repeat.

---

## CI/CD Integration

The included GitHub Actions workflow (`.github/workflows/llm-security.yml`) runs automatically on:
- Pull requests that modify `src/`, `data/`, or `scripts/`
- Pushes to `main`

### Setup for Your Repo

1. Go to **Settings → Secrets and variables → Actions**
2. Add `OPENAI_API_KEY` as a repository secret
3. Push code — the workflow runs automatically

---

## API Key Requirements

| Key | Cost | Used For |
|-----|------|----------|
| OpenAI API Key | ~$0.50-2.00 per full scan | LLM calls (model under test + Giskard's evaluator) |
| Giskard Guards API Key | Free tier available | Runtime guardrail screening |

### Getting API Keys

1. **OpenAI**: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. **Giskard Guards**: [guards.giskard.cloud](https://guards.giskard.cloud) — sign up and create a policy

### Configuring Giskard Guards Policies

After signing up at [guards.giskard.cloud](https://guards.giskard.cloud):

1. Create an **Input Policy** named `techcorp-input`:
   - Enable: Known Attacks detector (action: Block)
   - Enable: Obfuscation Detection (action: Block)

2. Create an **Output Policy** named `techcorp-output`:
   - Enable: Groundedness detector (action: Block)
   - Enable: PII Detection (action: Block)

3. Copy your API key from the dashboard

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'giskard'` | Run `pip install -r requirements.txt` |
| `openai.AuthenticationError` | Check your `OPENAI_API_KEY` is valid |
| Scan takes too long | Reduce model complexity or use `gpt-4o-mini` |
| Guards returns 401 | Check your `GISKARD_GUARDS_API_KEY` |
| Guards returns 404 | Verify your policy handles match (`techcorp-input`, `techcorp-output`) |
| RAGET fails on `generate_testset` | Ensure knowledge base CSV has `content` and `title` columns |

---

## Estimated Costs

Running the full notebook end-to-end:
- **Giskard Scan**: ~$0.50-1.50 (many LLM evaluation calls)
- **RAGET**: ~$0.30-0.80 (test generation + evaluation)
- **Guards API**: Free tier (limited requests) or paid
- **Total**: ~$1-3 for a complete run

---

## References

- [Giskard Guards Documentation](https://guards.giskard.cloud/docs/introduction)
- [Giskard Guards Detectors](https://guards.giskard.cloud/docs/policies/detectors)
- [Giskard Open Source LLM Scan](https://legacy-docs.giskard.ai/en/stable/open_source/scan/scan_llm/index.html)
- [Giskard RAGET Evaluation](https://legacy-docs.giskard.ai/en/stable/open_source/testset_generation/rag_evaluation/index.html)
- [Giskard GitHub](https://github.com/Giskard-AI/giskard)
- [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)

---

## License

MIT
