import json
from langchain_core.messages import HumanMessage

class DynamicPricingAgent:
    """
    Subagent that evaluates customer segment margins and determines optimal, margin-safe price campaigns.
    """
    def __init__(self, llm):
        self.llm = llm

    def run(self, customer, adoption_insights):
        prompt = f"""
You are the Dynamic Pricing Agent for a subscription SaaS.
Analyze this customer's financial profile and the adoption insights from the analyst agent:
- Name: {customer['name']}
- Segment: {customer.get('segment')}
- Current Engagement Score: {customer['engagement_score']}
- Discount Sensitivity Score: {customer['sensitivity']['discount']}
- Content/Onboarding Sensitivity: {customer['sensitivity']['content']}
- Current Risk/Adoption insights: {json.dumps(adoption_insights)}

Your goal is to recommend whether to offer:
1. A discount coupon (SMS/Email) - only if they are highly price-sensitive (Discount Sensitivity > 0.6) AND have NOT hit max discounts (discount_count < 2).
2. A tutorial onboarding intervention (SMS/Email) - if they are content-sensitive (Content Sensitivity > 0.5) OR have low product adoption/limit walls.
3. Pay-as-you-go or a custom API bundle - if they are high-value and hitting limits.
4. No pricing intervention (DO_NOTHING).

Determine the margin impact and write a concise recommendation.

Output format (STRICT JSON ONLY):
{{
  "recommendation_strategy": "DISCOUNT or TUTORIAL or CUSTOM_BUNDLE or DO_NOTHING",
  "reasoning": "Brief explanation of price elasticity / margin-safety safety check."
}}
"""
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            content = response.content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except Exception as e:
            return {
                "recommendation_strategy": "TUTORIAL",
                "reasoning": f"LLM pricing calculations failed: {e}. Defaulting to tutorial."
            }
