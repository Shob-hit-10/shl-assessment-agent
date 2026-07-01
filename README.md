# SHL Assessment Recommendation Agent

A conversational AI agent that recommends SHL assessments based on hiring requirements. The system uses a Retrieval-Augmented Generation (RAG) approach over the SHL Product Catalog and exposes a FastAPI service for interactive conversations.

---

## Overview

This project was developed as part of the SHL AI Hiring Assessment.

The agent is capable of:

- Asking clarifying questions for vague hiring requests.
- Recommending relevant SHL assessments.
- Refining recommendations when user requirements change.
- Comparing SHL assessments using catalog evidence.
- Returning only assessments available in the SHL Product Catalog.

The implementation combines:

- FastAPI
- Retrieval-Augmented Generation (RAG)
- TF-IDF based retrieval
- Google Gemini 1.5 Flash
- SHL Product Catalog

---

# Features

### Clarification

The agent asks follow-up questions whenever the user's request is too vague.

Example:

> User:
>
> I need an assessment.

Agent:

> Could you tell me the role or job level you are hiring for?

---

### Assessment Recommendation

Once sufficient information is available, the agent returns between **1 and 10** SHL assessments.

Each recommendation contains:

- Assessment name
- Official SHL catalog URL
- Assessment type

---

### Recommendation Refinement

The conversation is stateless but uses the provided conversation history to update recommendations.

Example:

User:

> I'm hiring a Java developer.

Later:

> Also include personality assessments.

The shortlist is updated accordingly.

---

### Assessment Comparison

The agent compares assessments using only information available in the SHL Product Catalog.

Example:

> Compare OPQ32r and SHL Verify Interactive G+.

---

# Architecture

```
                User
                  │
                  ▼
            FastAPI (/chat)
                  │
                  ▼
      Conversation Analysis
        (Google Gemini)
                  │
                  ▼
         TF-IDF Retriever
                  │
                  ▼
      SHL Product Catalog
                  │
                  ▼
      Response Generation
                  │
                  ▼
              JSON Response
```

---

# Project Structure

```
app/
│
├── chat.py
├── llm.py
├── main.py
├── models.py
├── parser.py
├── prompts.py
└── retriever.py

data/
└── shl_catalog.json

requirements.txt
README.md
```

---

# Installation

Clone the repository

```bash
git clone https://github.com/Shob-hit-10/shl-assessment-agent.git

cd shl-assessment-agent
```

Create virtual environment

```bash
python -m venv venv
```

Activate

Windows

```bash
venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create a `.env` file

```text
GEMINI_API_KEY=YOUR_API_KEY
```

Run the application

```bash
uvicorn app.main:app --reload
```

---

# API Endpoints

## Health

```
GET /health
```

Response

```json
{
    "status":"ok"
}
```

---

## Chat

```
POST /chat
```

Request

```json
{
    "messages":[
        {
            "role":"user",
            "content":"I'm hiring a Java developer"
        }
    ]
}
```

---

Response

```json
{
  "reply":"Based on your requirements...",
  "recommendations":[
      {
          "name":"Java 8 (New)",
          "url":"...",
          "test_type":"K"
      }
  ],
  "end_of_conversation":false
}
```

---

# Retrieval Method

The system uses a Retrieval-Augmented Generation (RAG) pipeline.

1. SHL Product Catalog is parsed into structured assessment objects.
2. Assessment metadata is indexed using TF-IDF vectorization.
3. User queries are matched against indexed assessment descriptions.
4. The highest-ranked assessments are returned.
5. Google Gemini is used only for conversation understanding (clarification, refinement and intent detection).

All recommendations remain grounded in the SHL Product Catalog.

---

# Evaluation Methodology

The system was evaluated across four dimensions.

## 1. Retrieval Quality

Representative hiring queries were tested to verify that relevant SHL assessments appear within the retrieved results.

Examples:

| Query | Expected Result |
|--------|-----------------|
| Hiring Java Developer | Java assessments |
| Personality Assessment | OPQ assessments |
| Graduate Hiring | Graduate-level assessments |

---

## 2. Recommendation Relevance

The following criteria were verified:

- Recommendations match hiring intent.
- Only SHL catalog assessments are returned.
- Between 1 and 10 assessments are recommended.
- Every recommendation contains a valid SHL catalog URL.

---

## 3. Groundedness

All recommendations and comparisons are generated exclusively from the SHL Product Catalog.

Validation included:

- Assessment names
- URLs
- Descriptions
- Categories
- Job levels

No external assessment information is introduced.

---

## 4. Conversational Behaviour

The agent was tested for all required behaviours.

| Behaviour | Status |
|-----------|--------|
| Clarification | ✅ |
| Recommendation | ✅ |
| Refinement | ✅ |
| Comparison | ✅ |
| SHL-only Recommendations | ✅ |

---

# Example Test Cases

## Clarification

Input

```
I need an assessment.
```

Output

```
Could you tell me the role or job level you are hiring for?
```

---

## Recommendation

Input

```
I'm hiring a Java developer.
```

Output

```
Returns Java-related SHL assessments.
```

---

## Refinement

Input

```
Also include personality assessments.
```

Output

```
Recommendation list updated with OPQ assessments.
```

---

## Comparison

Input

```
Compare OPQ32r and SHL Verify Interactive G+.
```

Output

```
Returns a catalog-grounded comparison.
```

---

# Technologies Used

- Python 3.10
- FastAPI
- Google Gemini 1.5 Flash
- TF-IDF Retrieval
- Scikit-learn
- Pydantic
- Uvicorn

---

# Live Deployment

Render

```
https://shl-assessment-agent-ez7v.onrender.com
```

Swagger Documentation

```
https://shl-assessment-agent-ez7v.onrender.com/docs
```

---

# GitHub Repository

https://github.com/Shob-hit-10/shl-assessment-agent

---

# Author

**Shobhit Koli**

Developed for the SHL AI Hiring Assessment.