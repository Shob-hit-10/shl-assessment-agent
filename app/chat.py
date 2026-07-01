import json
from app.retriever import Retriever
from app.llm import GeminiLLM


class ChatController:
    def __init__(self, retriever: Retriever):
        self.retriever = retriever
        self.llm = GeminiLLM()

    def get_test_type(self, assessment):
        keys = assessment.get("keys", [])

        if "Ability & Aptitude" in keys:
            return "A"
        if "Personality & Behavior" in keys:
            return "P"
        if "Knowledge & Skills" in keys or "Simulations" in keys:
            return "K"

        return "K"

    def get_all_user_text(self, messages):
        return "\n".join(
            f"{m.role}: {m.content}"
            for m in messages
        )

    def analyze_conversation(self, messages):
        conversation = self.get_all_user_text(messages)

        prompt = f"""
You are analyzing a conversation for an SHL assessment recommendation agent.

Return ONLY valid JSON with this schema:
{{
  "intent": "clarify" | "recommend" | "compare" | "refuse",
  "query": "search query for retrieval",
  "reply": "short assistant reply if clarification/refusal is needed",
  "assessment_names": ["names to compare if intent is compare"],
  "end_of_conversation": false
}}

Rules:
- If user asks for general hiring advice, legal advice, salary, resume help, interview questions, or anything outside SHL assessments: intent="refuse".
- If the user query is vague like "I need an assessment" with no role/job level/skills: intent="clarify".
- If user asks difference/compare/between two assessments: intent="compare".
- Otherwise intent="recommend".
- Use the full conversation history. If user refines constraints, include previous facts plus latest changes in query.
- For clarification, ask only ONE useful question.
- For refusal, say you only help with SHL assessment selection and comparison.

Conversation:
{conversation}
"""
        try:
            return self.llm.generate_json(prompt)
        except Exception:
            text = conversation.lower()
            if "assessment" in text and len(text.split()) < 8:
                return {
                    "intent": "clarify",
                    "query": "",
                    "reply": "Could you tell me the role or job level you are hiring for?",
                    "assessment_names": [],
                    "end_of_conversation": False
                }
            return {
                "intent": "recommend",
                "query": conversation,
                "reply": "",
                "assessment_names": [],
                "end_of_conversation": False
            }

    def find_by_name(self, name):
        name_lower = name.lower()
        all_items = self.retriever.assessments

        exact = [
            a for a in all_items
            if a.get("name", "").lower() == name_lower
        ]
        if exact:
            return exact[0]

        partial = [
            a for a in all_items
            if name_lower in a.get("name", "").lower()
            or a.get("name", "").lower() in name_lower
        ]
        if partial:
            return partial[0]

        results = self.retriever.search(name, top_k=1)
        return results[0] if results else None

    def handle_compare(self, analysis):
        names = analysis.get("assessment_names", [])
        items = []

        for name in names:
            item = self.find_by_name(name)
            if item:
                items.append(item)

        if len(items) < 2:
            return {
                "reply": "I can compare SHL assessments, but I need two assessment names from the catalog.",
                "recommendations": [],
                "end_of_conversation": False
            }

        a, b = items[0], items[1]

        reply = f"""
    Here is a catalog-grounded comparison:

    {a.get("name", "")}:
    - Type: {self.get_test_type(a)}
    - Category: {", ".join(a.get("keys", []))}
    - Duration: {a.get("duration", "Not specified")}
    - Job levels: {", ".join(a.get("job_levels", []))}
    - Description: {a.get("description", "")}

    {b.get("name", "")}:
    - Type: {self.get_test_type(b)}
    - Category: {", ".join(b.get("keys", []))}
    - Duration: {b.get("duration", "Not specified")}
    - Job levels: {", ".join(b.get("job_levels", []))}
    - Description: {b.get("description", "")}
    """.strip()

        return {
            "reply": reply,
            "recommendations": [],
            "end_of_conversation": False
        }

    def handle_recommend(self, analysis):
        query = analysis.get("query", "")
        results = self.retriever.search(query, top_k=10)

        full_query = query.lower()

        if "personality" in full_query or "behavior" in full_query or "behaviour" in full_query:
            personality_results = self.retriever.search(
                "OPQ32r personality behavior workplace",
                top_k=3
            )
            results = personality_results + results

        if "cognitive" in full_query or "ability" in full_query or "aptitude" in full_query:
            ability_results = self.retriever.search(
                "SHL Verify Interactive G+ cognitive ability aptitude reasoning",
                top_k=3
            )
            results = ability_results + results

        recommendations = []
        seen = set()

        for r in results:
            name = r.get("name", "")
            url = r.get("link", "")

            if not name or not url or name in seen:
                continue

            recommendations.append({
                "name": name,
                "url": url,
                "test_type": self.get_test_type(r)
            })

            seen.add(name)

            if len(recommendations) == 10:
                break

        names = ", ".join([r["name"] for r in recommendations[:5]])

        return {
            "reply": f"Based on your requirements, I found these SHL assessments. Top matches include: {names}.",
            "recommendations": recommendations,
            "end_of_conversation": False
        }

    def handle_chat(self, messages):
        last_user_message = ""
        for m in reversed(messages):
            if m.role == "user":
                last_user_message = m.content
                break

        last_lower = last_user_message.lower()

        if "difference between" in last_lower:
            part = last_user_message.lower().split("difference between", 1)[1]
            if " and " in part:
                a, b = part.split(" and ", 1)
                return self.handle_compare({
                    "assessment_names": [
                        a.strip(" ?."),
                        b.strip(" ?.")
                    ]
                })

        if "compare" in last_lower:
            return self.handle_compare({
                "assessment_names": []
            })

        analysis = self.analyze_conversation(messages)
        intent = analysis.get("intent", "recommend")

        if intent == "refuse":
            return {
                "reply": analysis.get(
                    "reply",
                    "I can only help with SHL assessment selection and comparison."
                ),
                "recommendations": [],
                "end_of_conversation": True
            }

        if intent == "clarify":
            return {
                "reply": analysis.get(
                    "reply",
                    "Could you tell me the role or job level you are hiring for?"
                ),
                "recommendations": [],
                "end_of_conversation": False
            }

        if intent == "compare":
            return self.handle_compare(analysis)

        return self.handle_recommend(analysis)