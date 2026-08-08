import json

from google import genai

from app.core.config import settings
from app.services.ai.prompts import VULNERABILITY_PROMPT


# -----------------------------
# Gemini Client
# -----------------------------
client = genai.Client(
    api_key=settings.GEMINI_API_KEY,
)


class AIExplainService:

    @staticmethod
    def execute(alert: dict):

        # -----------------------------
        # Build Prompt
        # -----------------------------
        prompt = VULNERABILITY_PROMPT.format(
            name=alert.get("alert", ""),
            risk=alert.get("risk", ""),
            description=alert.get("description", ""),
            solution=alert.get("solution", ""),
            reference=alert.get("reference", ""),
        )

        # -----------------------------
        # Call Gemini
        # -----------------------------
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
            },
        )

        # -----------------------------
        # Get Response
        # -----------------------------
        content = response.text

        if not content:
            raise ValueError(
                "Gemini returned an empty response."
            )

        # -----------------------------
        # Parse JSON
        # -----------------------------
        try:

            result = json.loads(content)

        except json.JSONDecodeError as e:

            raise ValueError(
                "Gemini returned invalid JSON."
            ) from e

        # -----------------------------
        # Return Expected Fields
        # -----------------------------
        return {
            "ai_explanation": result.get(
                "ai_explanation",
                "",
            ),

            "business_impact": result.get(
                "business_impact",
                "",
            ),

            "technical_impact": result.get(
                "technical_impact",
                "",
            ),

            "remediation_steps": result.get(
                "remediation_steps",
                "",
            ),

            "secure_coding_tip": result.get(
                "secure_coding_tip",
                "",
            ),

            "priority": result.get(
                "priority",
                "",
            ),

            "estimated_fix_time": result.get(
                "estimated_fix_time",
                "",
            ),
        }