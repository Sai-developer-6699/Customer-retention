import json
import re
from langchain_core.messages import HumanMessage

class ComplianceAuditorAgent:
    """
    Subagent that reviews copy for tone, truthfulness, and regulatory compliance.
    Implements security parameters: PII/Secret leak filters, prompt injection defense,
    pricing safety bounds, and hardcoded fatigue overrides.
    """
    def __init__(self, llm):
        self.llm = llm

    def run(self, customer, outreach_draft):
        action = outreach_draft.get("selected_action", "DO_NOTHING")
        draft_copy = outreach_draft.get("draft_copy", "")
        
        # ─────────────────────────────────────────────
        # SECURITY PARAMETER: PROMPT INJECTION SHIELD
        # ─────────────────────────────────────────────
        injection_signals = [
            "ignore previous", "ignore all", "system prompt", 
            "instead do", "you are now a", "overwrite memory"
        ]
        has_injection = any(signal in draft_copy.lower() for signal in injection_signals)
        if has_injection:
            return {
                "approved": False,
                "finalized_action": "DO_NOTHING",
                "finalized_copy": "Outreach blocked: Security filter triggered (Prompt Injection Detected).",
                "audit_notes": "BLOCKED: Prompt injection attack signatures matched."
            }

        # ─────────────────────────────────────────────
        # SECURITY PARAMETER: PII & SECRET EXPOSURE CHECK
        # ─────────────────────────────────────────────
        pii_patterns = [
            r"[\w\.-]+@[\w\.-]+\.\w+",           # Email regex
            r"\b[A-Za-z0-9+/]{32,}\b",            # Potential hashes/keys
            r"fake_key",                          # Mock API keys
            r"sk-[a-zA-Z0-9]{20,}",               # OpenAI API key pattern
            r"AIzaSy[a-zA-Z0-9-_]{33}"            # Google API key pattern
        ]
        
        for pattern in pii_patterns:
            if re.search(pattern, draft_copy):
                return {
                    "approved": False,
                    "finalized_action": "DO_NOTHING",
                    "finalized_copy": "Outreach blocked: Security filter triggered (Sensitive data / PII Leak risk).",
                    "audit_notes": "BLOCKED: Detected potential PII or active credentials in draft copy."
                }

        # ─────────────────────────────────────────────
        # HARD GUARDRAIL: SMS FATIGUE OVERRIDE
        # ─────────────────────────────────────────────
        sms_count = customer.get("sms_count", 0)
        if "SMS" in action and sms_count >= 2:
            # Downgrade to Email to protect channel reputation
            new_action = "SEND_EMAIL_DISCOUNT" if "DISCOUNT" in action else "SEND_EMAIL_TUTORIAL"
            audit_notes = f"SMS Fatigue limit hit ({sms_count} sent). Overriding action from {action} to {new_action}."
            action = new_action
        else:
            audit_notes = "Outreach channel complies with fatigue constraints."

        # ─────────────────────────────────────────────
        # HARD GUARDRAIL: PRICING LIES AUDITING
        # ─────────────────────────────────────────────
        prohibited_phrases = ["free forever", "90% off", "80% off", "100% discount", "no charge ever"]
        has_unapproved_offer = any(phrase in draft_copy.lower() for phrase in prohibited_phrases)
        if has_unapproved_offer:
            # Rewrite to conform to authorized 30% retention limit
            draft_copy = re.sub(
                r"(free forever|90% off|80% off|100% discount|no charge ever)", 
                "30% off", 
                draft_copy, 
                flags=re.IGNORECASE
            )
            audit_notes += " Corrected unapproved discount rate to authorized 30% discount margin."

        # ─────────────────────────────────────────────
        # REGULATORY AUDITING: SMS OPT-OUT
        # ─────────────────────────────────────────────
        if "SMS" in action and "STOP" not in draft_copy.upper():
            draft_copy += " Reply STOP to opt out."
            audit_notes += " Injected mandatory SMS unsubscribe opt-out compliance suffix."

        # Run final LLM audit for tone, ensuring professional language
        prompt = f"""
You are the Compliance Auditor Agent.
Audit this processed message to ensure a friendly, corporate, supportive tone.
- Customer Name: {customer['name']}
- Outreach Channel: {action}
- Message Draft: "{draft_copy}"

If the message sounds aggressive or is formatting-broken, fix it. Output the finalized compliant copy.

Output format (STRICT JSON ONLY):
{{
  "approved": true,
  "finalized_action": "{action}",
  "finalized_copy": "Compliant message copy",
  "audit_notes": "Notes about tone safety checks."
}}
"""
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            content = response.content.replace("```json", "").replace("```", "").strip()
            result = json.loads(content)
            # Concat our hardcoded notes
            result["audit_notes"] = f"{audit_notes} | {result.get('audit_notes', 'Tone approved.')}"
            return result
        except Exception as e:
            return {
                "approved": True,
                "finalized_action": action,
                "finalized_copy": draft_copy,
                "audit_notes": f"{audit_notes} | Fallback tone audit applied (Exception: {e})"
            }
