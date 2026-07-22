import json
from langchain_core.messages import HumanMessage

class AdoptionAnalystAgent:
    """
    Subagent that scans user logs, adoption events, and detects 'wobble moments'.
    """
    def __init__(self, llm):
        self.llm = llm

    def analyze_telemetry(self, customer):
        """Simulates scanning raw product telemetry data"""
        history = customer.get("history", [])
        time_since = customer.get("time_since_last_event", 0)
        score = customer.get("engagement_score", 100)
        
        # Determine signals
        wobble = False
        signal = "Normal activity"
        
        if time_since >= 4:
            wobble = True
            signal = "Severe inactivity detected"
        elif "Limit Warning Hit" in history:
            wobble = True
            signal = "Usage limit wall hit (needs scale-up/upsell)"
        elif score < 50:
            wobble = True
            signal = "Engagement score decaying rapidly"

        return {
            "wobble_moment_detected": wobble,
            "primary_signal": signal,
            "days_inactive": time_since,
            "engagement_score": score
        }

    def run(self, customer):
        telemetry = self.analyze_telemetry(customer)
        
        prompt = f"""
You are the Adoption Analyst Agent for customer retention.
Review the following user adoption telemetry details:
- Name: {customer['name']}
- Segment: {customer.get('segment')}
- Days Inactive: {telemetry['days_inactive']}
- Engagement Score: {telemetry['engagement_score']}
- Primary Signal: {telemetry['primary_signal']}
- Wobble Moment Detected: {telemetry['wobble_moment_detected']}

Analyze the customer's current product adoption and risk state. Provide a concise vibe check analysis.

Output format (STRICT JSON ONLY):
{{
  "risk_assessment": "High/Medium/Low risk level description",
  "adoption_friction_points": "Identify any usage friction points or limit issues."
}}
"""
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            content = response.content.replace("```json", "").replace("```", "").strip()
            res = json.loads(content)
            res.update(telemetry)
            return res
        except Exception as e:
            return {
                "risk_assessment": f"Failed to run LLM: {e}",
                "adoption_friction_points": "Unknown",
                **telemetry
            }
