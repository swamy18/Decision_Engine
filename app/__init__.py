# Decision Engine

A robust, audit-first framework designed to bridge the gap between **unstructured AI outputs** and **strict business logic**. This system turns noisy, probabilistic LLM generations into verified, deterministic **Decision Objects**.

## 🧐 The Problem
In modern AI integration, developers face a critical "trust gap":
- **LLMs are Probabilistic**: They hallucinate, omit data, or format outputs inconsistently.
- **Business Logic is Deterministic**: Financial and operational decisions require 100% adherence to rules (e.g., "Confidence must be > 90%", "Dates must be in the future").
- **Auditability is Hard**: When a mistake happens, it's often unclear *why* the model made that decision.

## 🛡 The Solution
The Decision Engine wraps the AI in a safety layer using a 4-step pipeline:
1.  **Ingest**: Create an immutable record of the raw input.
2.  **Translate**: Use an LLM to extract structured data (with fault tolerance).
3.  **Verify**: Apply code-based rules to validate the extracted data.
4.  **Decide**: Generate a final `DecisionObject` with a confidence score and audit trail.

## 🚀 Key Features

### 1. Deterministic Verification
Every model output passes through a logic layer (`VerificationResult`). If the model says "Success" but the data contains errors, the system catches the contradiction.
- **Contradiction Detection**: Flags logical inconsistencies.
- **Confidence Penalties**: Automatically downgrades confidence levels if validation fails.

### 2. Full Auditability
Nothing is lost. The final artifact is a `DecisionObject` that connects the dots:
- `RawInput` (What came in)
- `TranslationResult` (What the AI saw)
- `VerificationResult` (what the rules said)
- `AuditTrail` (Timeline of actions)

### 3. Safety by Default
Low confidence? Missing critical fields? The system automatically triggers an `EscalationPolicy`.
- **High Severity**: Requires immediate human review.
- **Fail-Safe**: It is impossible for a "bad" decision to slip through as "verified".

## 🏗 Architecture & Workflow

The system follows a strict linear pipeline (orchestrated in `app/workflow.py`):

```mermaid
graph LR
    A[Raw Input] --> B[Ingest]
    B --> C[Translate (LLM)]
    C --> D[Verify (Rules)]
    D --> E[Decision Object]
```

### Data Models (`app/domain/models.py`)
- **`RawInput`**: Immutable source of truth with hash.
- **`TranslationResult`**: The "noisy" extraction from the AI provider.
- **`VerificationResult`**: The output of the determinisic rule engine.
- **`DecisionObject`**: The final, safe artifact ready for downstream use.

## 🛠 Tech Stack
- **Framework**: FastAPI
- **Validation**: Pydantic V2 (Strict typing & validation)
- **Server**: Uvicorn
- **Testing**: Pytest

## 📂 Project Structure
```bash
├── app/
│   ├── api/          # API Routes
│   ├── core/         # Configuration
│   ├── domain/       # Pydantic Models (The Core Truth)
│   ├── services/     # Business Logic (Ingest, Translate, Verify)
│   └── workflow.py   # Main Pipeline Orchestrator
├── tests/            # Pytest suites
└── requirements.txt  # Dependencies
```

## ⚡️ Quick Start

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Run the Server
```bash
uvicorn app.main:app --reload
```

### 3. Test the API
Send a POST request to process a document:
```bash
curl -X POST "http://localhost:8000/api/v1/process" \
     -H "Content-Type: application/json" \
     -d '{
           "content": "Subject: Invoice 123. Total: $500. Status: Pending.",
           "metadata": {"source": "email_gateway"}
         }'
```

## 🚨 Failure Modes / Error Handling
- **ModelIntegrationError**: The LLM failed to produce valid JSON.
- **CONTRADICTION**: The LLM output logic conflicts with business rules (Confidence halved).
- **MISSING_DATA**: Critical fields are empty (Triggers Escalation).
