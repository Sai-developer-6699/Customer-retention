import time
from src.agents import behavior_analysis_agent

def run_simulation_step(customer, decision_agent_chain, memory):
    # STEP 1: OBSERVE
    analysis = behavior_analysis_agent(customer)
    
    # STEP 2: DECIDE (Call LLM)
    decision = decision_agent_chain.run(
        name=customer['name'],
        persona=customer['persona'],
        status_summary=analysis['summary'],
        memory=memory.get_success_hints(customer)
    )
    
    # STEP 3: ACT
    # (Trigger a tool in tools.py based on decision['action'])
    
    return analysis, decision

import random

def simulate_time_step(customer):
    """Call this every loop to advance 'time' for the user."""
    customer["time_since_last_event"] += 1
    
    # Behavior logic: High engagement = likely event. High 'time_since' = likely churn.
    activity_threshold = customer["engagement_score"] / 100.0
    
    if random.random() < activity_threshold:
        event = random.choice(["Login", "Feature Use", "Search"])
        customer["history"].append(event)
        customer["time_since_last_event"] = 0 # Reset on activity
        return f"User performed: {event}"
    
    return "User was inactive."
def evaluate_outcome(customer, action, memory=None):
    """
    Deterministic environment reaction.
    LLM decides WHAT to do.
    This function decides WHAT HAPPENS.
    """

    impact = 0
    history = customer["history"]

    # ─────────────────────────────
    # ACTION: SEND_DISCOUNT
    # ─────────────────────────────
    if action == "SEND_DISCOUNT":
        history.append("Discount Email Sent")

        if customer["sensitivity"]["discount"] > 0.6:
            history.append("Discount Accepted")
            impact = +8
        else:
            history.append("Discount Ignored")
            impact = -4

    # ─────────────────────────────
    # ACTION: SEND_TUTORIAL
    # ─────────────────────────────
    elif action == "SEND_TUTORIAL":
        history.append("Tutorial Email Sent")

        if customer["sensitivity"]["content"] > 0.6:
            history.append("Tutorial Completed")
            impact = +6
        else:
            history.append("Tutorial Skipped")
            impact = -3

    # ─────────────────────────────
    # ACTION: ASK_INTEREST
    # ─────────────────────────────
    elif action == "ASK_INTEREST":
        history.append("Interest Check Sent")

        if customer["engagement_score"] > 40:
            history.append("Responded: Interested")
            impact = +3
        else:
            history.append("Responded: Not Interested")
            customer["not_interested_count"] += 1
            impact = -5

    # ─────────────────────────────
    # ACTION: DO_NOTHING
    # ─────────────────────────────
    elif action == "DO_NOTHING":
        impact = -5 - customer["time_since_last_event"]
        history.append("No Action Taken")

    # ─────────────────────────────
    # APPLY IMPACT
    # ─────────────────────────────
    customer["engagement_score"] = max(
        0, min(100, customer["engagement_score"] + impact)
    )

    # Time handling
    if action == "DO_NOTHING":
        customer["time_since_last_event"] += 1
    else:
        customer["time_since_last_event"] = 0

    # ─────────────────────────────
    # CHURN ELIMINATION (KEY AGENTIC MOMENT)
    # ─────────────────────────────
    if customer["not_interested_count"] >= 2:
        customer["status"] = "Churned"
        history.append("Customer Marked as Churned")
        impact = 0  # stop further decay

    if customer["segment"] == "Price-Sensitive" and customer["not_interested_count"] >= 2:
        customer["status"] = "Churned"
        customer["lifecycle_stage"] = "Churned"
        customer["history"].append("Agent stopped investing due to low ROI")
    # ─────────────────────────────
    # LEARNING (Strategy Memory)
    # ─────────────────────────────
    if memory is not None and action != "DO_NOTHING":
        status = "SUCCESS" if impact > 0 else "FAILED"
        memory.update(customer, action, status)

    # ─────────────────────────────
    # STATE TRACKING (CRITICAL)
    # ─────────────────────────────
    customer["last_action"] = action
    customer["action_history"].append(action)

    return impact

# Aliases for app.py compatibility
simulate_user_behavior = simulate_time_step
evaluate_agent_action = evaluate_outcome