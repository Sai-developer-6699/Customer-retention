import os
from dotenv import load_dotenv
import json
import random
from langchain_core.messages import HumanMessage
# Load variables from .env
load_dotenv()

# Now the agent can see the key automatically
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.2,
    api_key=os.getenv("OPENAI_API_KEY")
)
# 1. BEHAVIOR ANALYSIS AGENT (Deterministic Logic)
def behavior_analysis_agent(customer):
    """Analyzes raw history to create a 'Vibe Check' for the LLM."""
    last_3_events = customer['history'][-3:]
    score_change = customer['engagement_score']
    
    status = "Healthy"
    if "Inactive" in last_3_events:
        status = "At Risk"
    if "Visited Pricing Page" in last_3_events:
        status = "Upsell Opportunity"
        
    return {
        "customer_id": customer['id'],
        "status": status,
        "summary": f"User is {status} with a score of {score_change}."
    }

# 2. DECISION AGENT (The LLM Brain)
# This uses the 'Observe' and 'Memory' to decide the 'Action'
DECISION_PROMPT = """
You are an Autonomous CLM Orchestrator.
CONTEXT:
Customer: {name} ({persona})
Current Status: {status_summary}
Strategy Memory (Past results): {memory}

TASK:
Based on the status and what we've learned from past interactions, 
choose the NEXT BEST ACTION from: [SEND_DISCOUNT, SEND_TUTORIAL, SCHEDULE_CALL, DO_NOTHING].

Provide your reasoning in the 'thought' field.
OUTPUT JSON FORMAT:
{{
  "thought": "your reasoning here",
  "action": "ACTION_NAME",
  "params": {{}}
}}
"""


ACTIONS = ["SEND_DISCOUNT", "SEND_TUTORIAL", "ASK_INTEREST", "DO_NOTHING"]

def decision_agent(customer, memory):
    """
    Strategic Decision Agent.
    ALWAYS returns:
    {
        "thought": str,
        "action": str
    }
    """

    # ─────────────────────────────
    # HARD RULES (NO LLM)
    # ─────────────────────────────
    if customer["status"] == "Churned":
        return {
            "thought": "Customer already churned. No further investment.",
            "action": "DO_NOTHING"
        }

    MAX_DISCOUNTS = 2

    forbidden = memory.get_forbidden_actions(customer)

    # HARD BUSINESS CONSTRAINT: Discount cap
    if customer["discount_count"] >= MAX_DISCOUNTS:
        forbidden.append("SEND_DISCOUNT")

    # Force exploration if primary strategy failed
    if "SEND_DISCOUNT" in forbidden and customer["segment"] == "Price-Sensitive":
        pass  # ASK_INTEREST becomes the natural next option

    # Force action when inactive
    if customer["time_since_last_event"] >= 2 and "DO_NOTHING" not in forbidden:
        forbidden.append("DO_NOTHING")

    # Business policy example
    if customer.get("segment") == "High-Value":
        forbidden.append("SEND_DISCOUNT")

    allowed_actions = [a for a in ACTIONS if a not in forbidden]

    # Absolute fallback (should rarely happen)
    if not allowed_actions:
        return {
            "thought": "All actions are constrained. Defaulting to safe inaction.",
            "action": "DO_NOTHING"
        }

    # ─────────────────────────────
    # LLM STRATEGIC REASONING
    # ─────────────────────────────
    prompt = f"""
You are an Autonomous Customer Lifecycle Decision Agent.

Your objective is to choose the NEXT BEST ACTION that maximizes customer engagement.

━━━━━━━━━━━━━━━━━━━━━━
CUSTOMER CONTEXT
━━━━━━━━━━━━━━━━━━━━━━
Name: {customer['name']}
Segment: {customer.get('segment', 'N/A')}
Lifecycle Stage: {customer['lifecycle_stage']}
Engagement Score: {customer['engagement_score']}
Time Since Last Event: {customer['time_since_last_event']}
Last Action: {customer['last_action']}
Action History: {customer['action_history']}

━━━━━━━━━━━━━━━━━━━━━━
PAST LEARNINGS
━━━━━━━━━━━━━━━━━━━━━━
{memory.get_success_hints(customer)}

Forbidden Actions (must NOT choose):
{forbidden}

━━━━━━━━━━━━━━━━━━━━━━
DECISION RULES
━━━━━━━━━━━━━━━━━━━━━━
- Inaction causes engagement decay.
- Avoid repeating failed strategies.
- Prefer actions aligned with the customer segment.
- Choose exactly ONE action.

━━━━━━━━━━━━━━━━━━━━━━
AVAILABLE ACTIONS
━━━━━━━━━━━━━━━━━━━━━━
{allowed_actions}

━━━━━━━━━━━━━━━━━━━━━━
OUTPUT FORMAT (STRICT JSON ONLY)
━━━━━━━━━━━━━━━━━━━━━━
{{
  "thought": "Briefly explain WHY this action is chosen.",
  "action": "ONE_ACTION_FROM_AVAILABLE_ACTIONS"
}}
"""

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content.replace("```json", "").replace("```", "").strip()
        result = json.loads(content)

        action = result.get("action")
        thought = result.get("thought", "No explicit reasoning provided.")

        # Validate action
        if action not in allowed_actions:
            return {
                "thought": f"Model suggested invalid action '{action}'. Falling back to first allowed option.",
                "action": allowed_actions[0]
            }

        return {
            "thought": thought,
            "action": action
        }

    except Exception as e:
        print("Decision Agent Error:", e)
        return {
            "thought": "LLM call failed. Falling back to deterministic safe action.",
            "action": allowed_actions[0]
        }
