import json
from langchain_core.messages import HumanMessage

class OutreachCopywriterAgent:
    """
    Subagent that drafts context-specific email, SMS, push, or in-app copies.
    """
    def __init__(self, llm):
        self.llm = llm

    def run(self, customer, pricing_insights, allowed_actions):
        prompt = f"""
You are the Outreach Copywriter Agent.
Draft highly personalized retention copy based on this customer's details and the pricing strategy recommendation:
- Name: {customer['name']}
- Segment: {customer.get('segment')}
- Lifecycle Stage: {customer['lifecycle_stage']}
- Pricing Recommendation: {pricing_insights['recommendation_strategy']}
- Allowed Outreach Channels: {allowed_actions}

Your copy must speak directly to their persona (e.g. Student Sam loves coupons/exams context, Clara needs deep tech integration/API references).
Choose the best action channel from the allowed outreach channels list.

Output format (STRICT JSON ONLY):
{{
  "selected_action": "ONE_OF_ALLOWED_CHANNELS",
  "draft_copy": "The full exact copy of the message (Subject + Body for email, short text for SMS/Push/In-App). Avoid generic wording."
}}
"""
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            content = response.content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except Exception as e:
            fallback_action = allowed_actions[0] if allowed_actions else "DO_NOTHING"
            return {
                "selected_action": fallback_action,
                "draft_copy": f"Hello {customer['name']}, please let us know how we can improve your workspace experience!"
            }
