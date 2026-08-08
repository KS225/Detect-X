VULNERABILITY_PROMPT = """
You are a senior cybersecurity expert.

Analyze the following OWASP ZAP vulnerability.

Return ONLY valid JSON.

{{
    "ai_explanation": "",
    "business_impact": "",
    "technical_impact": "",
    "remediation_steps": "",
    "secure_coding_tip": "",
    "priority": "",
    "estimated_fix_time": ""
}}

Vulnerability

Name:
{name}

Risk:
{risk}

Description:
{description}

Solution:
{solution}

Reference:
{reference}
"""