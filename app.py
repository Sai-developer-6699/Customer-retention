import os
import random
import time
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Streamlit App Config
st.set_page_config(
    page_title="RetentionX | Premium CLM & Price Analytics",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Products and Customer imports
from data.customer import personas
from data.products import products
from src.agents import behavior_analysis_agent, decision_agent
from src.simulation import simulate_user_behavior, evaluate_agent_action
from src.memory_store import StrategyMemory

# ─────────────────────────────────────────────
# PREMIUM DARK CLASSIC / GLASSMORPHIC CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
    
    /* App background & typography */
    .stApp {
        background-color: #0b0f19;
        color: #e2e8f0;
        font-family: 'Outfit', sans-serif;
    }
    
    /* Hide Streamlit default UI */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Glassmorphic Cards */
    .premium-card {
        background: rgba(17, 24, 39, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .premium-card:hover {
        transform: translateY(-2px);
        border-color: rgba(59, 130, 246, 0.3);
        box-shadow: 0 12px 40px 0 rgba(59, 130, 246, 0.1);
    }
    
    /* Live Log Card styles */
    .log-card {
        border-left: 4px solid #3b82f6;
    }
    .log-card-success {
        border-left: 4px solid #10b981;
        background: rgba(16, 185, 129, 0.06);
    }
    .log-card-failed {
        border-left: 4px solid #ef4444;
        background: rgba(239, 68, 68, 0.06);
    }
    .log-card-neutral {
        border-left: 4px solid #64748b;
        background: rgba(100, 116, 139, 0.06);
    }
    
    /* Custom Pill Badges */
    .channel-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }
    .badge-sms {
        background: rgba(168, 85, 247, 0.15);
        color: #c084fc;
        border: 1px solid rgba(168, 85, 247, 0.3);
    }
    .badge-email {
        background: rgba(59, 130, 246, 0.15);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }
    .badge-inapp {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .badge-push {
        background: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    .badge-nothing {
        background: rgba(100, 116, 139, 0.15);
        color: #94a3b8;
        border: 1px solid rgba(100, 116, 139, 0.3);
    }
    
    /* Stats box */
    .stat-container {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
    }
    .stat-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #ffffff;
    }
    .stat-label {
        font-size: 0.7rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.2rem;
    }
    .stat-percentage {
        font-size: 0.8rem;
        color: #10b981;
        font-weight: 600;
    }
    
    /* Header Gradient Text */
    .logo-text {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #60a5fa 0%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────
if "customers" not in st.session_state:
    st.session_state.customers = personas

if "memory" not in st.session_state:
    st.session_state.memory = StrategyMemory()

if "story_log" not in st.session_state:
    st.session_state.story_log = []

if "day_count" not in st.session_state:
    st.session_state.day_count = 0

if "memory_updates" not in st.session_state:
    st.session_state.memory_updates = []

if "pending_approvals" not in st.session_state:
    st.session_state.pending_approvals = []

# Pricing history initialization
if "price_history" not in st.session_state:
    st.session_state.price_history = {
        "Pro Subscription": [29.0],
        "Enterprise Plan": [99.0],
        "API Add-on": [15.0],
        "Pro + API Bundle": [39.0]
    }

# Active prices paid tracking
if "base_prices" not in st.session_state:
    st.session_state.base_prices = {
        "P001": 29.0,
        "P002": 99.0,
        "P003": 15.0,
        "P004": 39.0
    }

def save_state_to_json(llm_provider="openai"):
    import json
    state = {
        "day_count": st.session_state.day_count,
        "price_history": st.session_state.price_history,
        "customers": st.session_state.customers,
        "memory_registry": st.session_state.memory.registry,
        "story_log": st.session_state.story_log,
        "llm_provider": llm_provider,
        "pending_approvals": st.session_state.get("pending_approvals", [])
    }
    frontend_dir = os.path.join(os.getcwd(), "frontend", "public")
    if not os.path.exists(frontend_dir):
        os.makedirs(frontend_dir, exist_ok=True)
    state_file = os.path.join(frontend_dir, "state.json")
    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)

# Save initial state on boot
if "initial_saved" not in st.session_state:
    save_state_to_json("openai")
    st.session_state.initial_saved = True

# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────
def get_action_details(action):
    """Returns icon and UI badge class name"""
    details = {
        "SEND_SMS_DISCOUNT": ("💬 SMS", "badge-sms"),
        "SEND_SMS_TUTORIAL": ("💬 SMS", "badge-sms"),
        "SEND_EMAIL_DISCOUNT": ("✉️ EMAIL", "badge-email"),
        "SEND_EMAIL_TUTORIAL": ("✉️ EMAIL", "badge-email"),
        "SEND_IN_APP_MESSAGE": ("💻 IN-APP", "badge-inapp"),
        "SEND_PUSH_NOTIFICATION": ("🔔 PUSH", "badge-push"),
        "CUSTOM_BUNDLE": ("🎁 BUNDLE", "badge-inapp"),
        "DO_NOTHING": ("😴 INACTION", "badge-nothing")
    }
    return details.get(action, ("⚡ ACTION", "badge-nothing"))

def get_message_content(action, customer_name):
    """Generates the actual copy sent to the customer"""
    if action == "SEND_SMS_DISCOUNT":
        return f"SMS: 'Hey {customer_name}! Don't lose your access. Apply code SAVEMORE30 on your next renew for 30% off!'"
    elif action == "SEND_SMS_TUTORIAL":
        return f"SMS: 'Hi {customer_name}, we updated your setup instructions! View our quick guides here: bit.ly/pro-onboarding'"
    elif action == "SEND_EMAIL_DISCOUNT":
        return f"Email: 'Subject: Personal discount on your plan\nBody: Hi {customer_name},\nWe appreciate your subscription. Here is an exclusive 25% discount valid for the next 3 days...'"
    elif action == "SEND_EMAIL_TUTORIAL":
        return f"Email: 'Subject: Developer setup & integration guide\nBody: Hello {customer_name},\nHere is a detailed deep dive tutorial to help you get the most out of your webhooks and API rate limits...'"
    elif action == "SEND_IN_APP_MESSAGE":
        return f"In-App Nudge: 'Modal Check-in: Need assistance setting up your developer workspace? Chat with our experts!'"
    elif action == "SEND_PUSH_NOTIFICATION":
        return f"Push Notification: 'Alert: Custom API limits warning - Tap to optimize your endpoints.'"
    elif action == "CUSTOM_BUNDLE":
        return f"Bundle: 'Add-on Offer: Get 50,000 extra API queries added to your plan for only $5/mo!'"
    return "No message sent (System stayed idle)."

def get_channel_metrics():
    """Calculates metrics for outreach channels from StrategyMemory"""
    metrics = {
        "SMS": {"sent": 0, "success": 0},
        "Email": {"sent": 0, "success": 0},
        "In-App": {"sent": 0, "success": 0},
        "Push": {"sent": 0, "success": 0}
    }
    
    # Calculate from the StrategyMemory registry
    registry = st.session_state.memory.registry
    for key, strategies in registry.items():
        for action, stats in strategies.items():
            successes = stats.get("SUCCESS", 0)
            failures = stats.get("FAILED", 0)
            total = successes + failures
            
            if "SMS" in action:
                metrics["SMS"]["sent"] += total
                metrics["SMS"]["success"] += successes
            elif "EMAIL" in action:
                metrics["Email"]["sent"] += total
                metrics["Email"]["success"] += successes
            elif "IN_APP" in action:
                metrics["In-App"]["sent"] += total
                metrics["In-App"]["success"] += successes
            elif "PUSH" in action:
                metrics["Push"]["sent"] += total
                metrics["Push"]["success"] += successes
                
    return metrics

# ─────────────────────────────────────────────
# SIDEBAR CONTROLS & MEMORY LEDGER
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div style='text-align: center; margin-bottom: 1.5rem;'><span class='logo-text'>RetentionX</span><br><small style='color: #94a3b8;'>Live CLM Orchestrator</small></div>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Simulation stats
    st.metric("📅 Day Counter", st.session_state.day_count)
    
    # Controls
    st.markdown("### 🛠 ... Settings")
    llm_provider = st.selectbox("LLM Provider (Group A)", ["openai", "gemini"], index=0, help="Switch between OpenAI GPT-4o-mini and Google Gemini 1.5 Flash for the active agent campaigns.")
    auto_pricing = st.toggle("Simulate Product Price Changes", value=True, help="Fluctuates product base prices each day to test price sensitivity response.")
    
    # Manual pricing sliders if auto is off
    if not auto_pricing:
        st.markdown("##### Manual Base Prices")
        st.session_state.base_prices["P001"] = st.slider("Pro Subscription ($)", 10.0, 50.0, float(st.session_state.base_prices["P001"]), 1.0)
        st.session_state.base_prices["P002"] = st.slider("Enterprise Plan ($)", 50.0, 200.0, float(st.session_state.base_prices["P002"]), 5.0)
        st.session_state.base_prices["P003"] = st.slider("API Add-on ($)", 5.0, 30.0, float(st.session_state.base_prices["P003"]), 1.0)
    
    st.markdown("---")
    
    # Memory ledger status
    st.markdown("### 🧠 Agent Strategy Memory")
    if st.session_state.memory.registry:
        for key, strategies in st.session_state.memory.registry.items():
            parts = key.split('_', 1)
            persona_name = parts[1] if len(parts) == 2 else key
            stage = parts[0] if len(parts) == 2 else ""
            
            with st.expander(f"👤 {persona_name} ({stage})"):
                for action, stats in strategies.items():
                    s_count = stats.get("SUCCESS", 0)
                    f_count = stats.get("FAILED", 0)
                    st.write(f"**{action.replace('SEND_', '')}**")
                    st.write(f"✅ Success: {s_count} | ❌ Fail: {f_count}")
    else:
        st.info("No strategy memory recorded yet. Run a simulation day to train the agent.")

    st.markdown("---")
    st.markdown("### 🤝 Global Benchmarks (Cooperative)")
    from src.cooperative_registry import load_cooperative_benchmarks
    global_benchmarks = load_cooperative_benchmarks()
    for act, stats in global_benchmarks.items():
        rate = stats.get("success_rate", 0.0) * 100
        runs = stats.get("runs", 0)
        act_clean = act.replace("SEND_", "").replace("_", " ")
        st.write(f"**{act_clean}**: {rate:.1f}% conversion ({runs} runs pooled)")

    st.markdown("---")
    if st.button("🔄 Reset Environment", use_container_width=True):
        st.session_state.customers = personas
        st.session_state.memory = StrategyMemory()
        st.session_state.story_log = []
        st.session_state.day_count = 0
        st.session_state.memory_updates = []
        st.session_state.pending_approvals = []
        st.session_state.price_history = {
            "Pro Subscription": [29.0],
            "Enterprise Plan": [99.0],
            "API Add-on": [15.0],
            "Pro + API Bundle": [39.0]
        }
        st.session_state.base_prices = {
            "P001": 29.0,
            "P002": 99.0,
            "P003": 15.0,
            "P004": 39.0
        }
        save_state_to_json(llm_provider)
        st.rerun()

    st.markdown("---")
    st.markdown("### 📥 Export Simulation Data")
    
    # 1. Export registry JSON
    import json
    registry_json = json.dumps(st.session_state.memory.registry, indent=2)
    st.download_button(
        label="Download Learning Memory (JSON)",
        data=registry_json,
        file_name="strategy_memory.json",
        mime="application/json",
        use_container_width=True
    )
    
    # 2. Export story log CSV
    if st.session_state.story_log:
        story_df = pd.DataFrame([{
            "Day": s["day"],
            "Customer ID": s["customer"]["id"],
            "Customer Name": s["customer"]["name"],
            "Action": s["action"],
            "Impact": s["impact"],
            "Thought": s["thought"]
        } for s in st.session_state.story_log])
        st.download_button(
            label="Download Story Logs (CSV)",
            data=story_df.to_csv(index=False),
            file_name="retention_stories.csv",
            mime="text/csv",
            use_container_width=True
        )

# ─────────────────────────────────────────────
# MAIN DASHBOARD HEADER
# ─────────────────────────────────────────────
st.markdown("<div style='margin-bottom: 2rem;'><h1 style='margin: 0; font-weight: 800; color: #ffffff;'>⚡ Live Interaction & Pricing Dashboard</h1><p style='margin: 0.5rem 0 0 0; color: #94a3b8; font-size: 1.1rem;'>Track real-time SaaS pricing history alongside autonomous marketing channels (SMS, Email, In-App, Push) driving customer retention.</p></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# A/B TESTING RETENTION ANALYTICS
# ─────────────────────────────────────────────
group_a_scores = [c["engagement_score"] for c in st.session_state.customers if c.get("test_group") == "Group A (AI-driven CLM)"]
group_b_scores = [c["engagement_score"] for c in st.session_state.customers if c.get("test_group") == "Group B (Standard Rules)"]
avg_a = sum(group_a_scores) / len(group_a_scores) if group_a_scores else 0.0
avg_b = sum(group_b_scores) / len(group_b_scores) if group_b_scores else 0.0
ab_lift = ((avg_a - avg_b) / avg_b * 100) if avg_b > 0 else 0.0

st.markdown("### 🧪 A/B Testing Baseline Lift")
col_ab1, col_ab2, col_ab3 = st.columns(3)
with col_ab1:
    st.metric(
        label="AI-Led OODA (Group A) Avg Engagement", 
        value=f"{avg_a:.1f}/100", 
        delta=f"{avg_a - avg_b:+.1f} vs Control",
        help="Average engagement score of customers managed by the autonomous AI agents."
    )
with col_ab2:
    st.metric(
        label="Static Rules (Group B) Avg Engagement", 
        value=f"{avg_b:.1f}/100",
        help="Average engagement score of customers managed by fixed baseline marketing rules."
    )
with col_ab3:
    st.metric(
        label="AI Retention Performance Lift", 
        value=f"{ab_lift:+.1f}%",
        help="Percentage lift in customer retention/engagement achieved by the LLM OODA loop over standard rules."
    )

st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# ROW 1: OUTREACH CHANNEL STATISTICS
# ─────────────────────────────────────────────
ch_metrics = get_channel_metrics()

st.markdown("### 📊 Live Outreach Channels")
col_sms, col_email, col_inapp, col_push = st.columns(4)

with col_sms:
    sms_sent = ch_metrics["SMS"]["sent"]
    sms_success = ch_metrics["SMS"]["success"]
    sms_rate = (sms_success / sms_sent * 100) if sms_sent > 0 else 0.0
    st.markdown(f"""
    <div class="stat-container">
        <div class="stat-value">💬 {sms_sent}</div>
        <div class="stat-label">SMS Alerts Sent</div>
        <div class="stat-percentage">{sms_rate:.1f}% Success Rate</div>
    </div>
    """, unsafe_allow_html=True)

with col_email:
    email_sent = ch_metrics["Email"]["sent"]
    email_success = ch_metrics["Email"]["success"]
    email_rate = (email_success / email_sent * 100) if email_sent > 0 else 0.0
    st.markdown(f"""
    <div class="stat-container">
        <div class="stat-value">✉️ {email_sent}</div>
        <div class="stat-label">Emails Delivered</div>
        <div class="stat-percentage">{email_rate:.1f}% Success Rate</div>
    </div>
    """, unsafe_allow_html=True)

with col_inapp:
    inapp_sent = ch_metrics["In-App"]["sent"]
    inapp_success = ch_metrics["In-App"]["success"]
    inapp_rate = (inapp_success / inapp_sent * 100) if inapp_sent > 0 else 0.0
    st.markdown(f"""
    <div class="stat-container">
        <div class="stat-value">💻 {inapp_sent}</div>
        <div class="stat-label">In-App Modals</div>
        <div class="stat-percentage">{inapp_rate:.1f}% Success Rate</div>
    </div>
    """, unsafe_allow_html=True)

with col_push:
    push_sent = ch_metrics["Push"]["sent"]
    push_success = ch_metrics["Push"]["success"]
    push_rate = (push_success / push_sent * 100) if push_sent > 0 else 0.0
    st.markdown(f"""
    <div class="stat-container">
        <div class="stat-value">🔔 {push_sent}</div>
        <div class="stat-label">Push Notifications</div>
        <div class="stat-percentage">{push_rate:.1f}% Success Rate</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# INTERACTIVE RUN BUTTON
# ─────────────────────────────────────────────
col_run1, col_run2, col_run3 = st.columns([1, 2, 1])
with col_run2:
    if st.session_state.pending_approvals:
        st.warning("⚠️ Action Required: You have campaigns in the HITL staging queue below. Please Approve or Reject them to advance.")
        st.button("▶️ **Simulate Next Day Outreach & Pricing**", use_container_width=True, type="primary", disabled=True)
    else:
        if st.button("▶️ **Simulate Next Day Outreach & Pricing**", use_container_width=True, type="primary"):
            st.session_state.day_count += 1
            daily_stories = []
            
            # 1. Update prices if auto pricing is toggled
            if auto_pricing:
                for prod_id, prod_data in products.items():
                    prod_name = prod_data["name"]
                    last_price = st.session_state.price_history[prod_name][-1]
                    # Price walk of +-4%
                    change = random.uniform(-0.04, 0.04)
                    new_price = round(max(5.0, last_price * (1 + change)), 2)
                    st.session_state.price_history[prod_name].append(new_price)
                    st.session_state.base_prices[prod_id] = new_price
            else:
                # Keep manual price constant in history
                for prod_id, prod_data in products.items():
                    prod_name = prod_data["name"]
                    st.session_state.price_history[prod_name].append(st.session_state.base_prices[prod_id])

            # Associate day count to memory for message timestamps
            st.session_state.memory.day_count = st.session_state.day_count

            with st.spinner("🧠 Agent is analyzing vibes, checking memory, and executing retention campaigns..."):
                for customer in st.session_state.customers:
                    if customer.get("status") == "Churned":
                        continue
                    
                    # Dynamic subscription details based on current day prices
                    prod_id = customer.get("product_id", "P001")
                    base_price = st.session_state.base_prices[prod_id]
                    
                    # Advance time (Simulate behavior)
                    behavior_log = simulate_user_behavior(customer)
                    
                    # Observe
                    _ = behavior_analysis_agent(customer)
                    
                    # Decide
                    decision = decision_agent(customer, st.session_state.memory, llm_provider=llm_provider)
                    action = decision.get("action")
                    thought = decision.get("thought", "No reasoning provided.")
                    content = decision.get("content", "No message.")
                    
                    # HITL routing: if action is DO_NOTHING, apply immediately. Otherwise hold.
                    if action == "DO_NOTHING":
                        impact = evaluate_agent_action(customer, action, st.session_state.memory, content=content)
                        daily_stories.append({
                            "day": st.session_state.day_count,
                            "customer": customer.copy(),
                            "base_price": base_price,
                            "thought": thought,
                            "action": action,
                            "impact": impact,
                            "behavior": behavior_log
                        })
                    else:
                        st.session_state.pending_approvals.append({
                            "customer_id": customer["id"],
                            "customer_name": customer["name"],
                            "action": action,
                            "content": content,
                            "thought": thought,
                            "base_price": base_price,
                            "behavior_log": behavior_log
                        })
            
            st.session_state.story_log.extend(daily_stories)
            save_state_to_json(llm_provider)
            st.success(f"Successfully initialized Day {st.session_state.day_count}! Review pending outreach items below.")
            st.rerun()

# ─────────────────────────────────────────────
# HUMAN-IN-THE-LOOP (HITL) AUDIT DESK
# ─────────────────────────────────────────────
if st.session_state.pending_approvals:
    st.markdown("---")
    st.markdown("### 📥 Campaign Staging Queue (Human-in-the-Loop)")
    st.info("The following outreach campaigns were generated by the AI agent mesh and are staged for your review. Adjust the message copy or approve/reject them to resume the simulation.")
    
    # We will copy the list to avoid mutations during iteration
    pending_list = list(st.session_state.pending_approvals)
    for idx, approval in enumerate(pending_list):
        cust_id = approval["customer_id"]
        cust_name = approval["customer_name"]
        action = approval["action"]
        thought = approval["thought"]
        draft_copy = approval["content"]
        
        # Find customer object in st.session_state.customers
        customer = next((c for c in st.session_state.customers if c["id"] == cust_id), None)
        if not customer:
            continue
            
        with st.container(border=True):
            col_ap1, col_ap2 = st.columns([3, 1])
            with col_ap1:
                st.markdown(f"**👤 Customer:** {cust_name} ({customer.get('segment', 'N/A')}) | **📢 Suggested Action:** `{action}`")
                st.markdown(f"*🧠 Agent Thought:* {thought}")
                
                # Let them edit the text copy inline!
                edited_copy = st.text_area(f"Edit Message Copy ({cust_name})", value=draft_copy, key=f"edit_copy_{cust_id}_{idx}")
            with col_ap2:
                st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
                if st.button("✅ Approve", key=f"approve_{cust_id}_{idx}", use_container_width=True):
                    # Execute approved campaign
                    impact = evaluate_agent_action(customer, action, st.session_state.memory, content=edited_copy)
                    # Add to story log
                    st.session_state.story_log.append({
                        "day": st.session_state.day_count,
                        "customer": customer.copy(),
                        "base_price": approval["base_price"],
                        "thought": f"Approved by CSM. Original thought: {thought}",
                        "action": action,
                        "impact": impact,
                        "behavior": approval["behavior_log"]
                    })
                    # Sync local memory registry to global cooperative registry
                    from src.cooperative_registry import sync_local_to_global
                    sync_local_to_global(st.session_state.memory.registry)
                    
                    # Remove from queue
                    st.session_state.pending_approvals.pop(idx)
                    save_state_to_json(llm_provider)
                    st.rerun()
                    
                if st.button("❌ Reject", key=f"reject_{cust_id}_{idx}", use_container_width=True):
                    # Force action to DO_NOTHING
                    impact = evaluate_agent_action(customer, "DO_NOTHING", st.session_state.memory)
                    # Add to story log
                    st.session_state.story_log.append({
                        "day": st.session_state.day_count,
                        "customer": customer.copy(),
                        "base_price": approval["base_price"],
                        "thought": f"Rejected by CSM. Fallback to DO_NOTHING. Original thought: {thought}",
                        "action": "DO_NOTHING",
                        "impact": impact,
                        "behavior": "Campaign rejected by administrator."
                    })
                    # Remove from queue
                    st.session_state.pending_approvals.pop(idx)
                    save_state_to_json(llm_provider)
                    st.rerun()

# ─────────────────────────────────────────────
# ROW 2: LIVE FEED & PRICING ANALYTICS
# ─────────────────────────────────────────────
col_left, col_right = st.columns([5, 3])

with col_left:
    st.markdown("### 💬 Live Outreach Feed (OODA Decisions)")
    
    if st.session_state.story_log:
        # Show last 4 entries
        recent_stories = st.session_state.story_log[-4:]
        recent_stories.reverse()
        
        for story in recent_stories:
            cust = story["customer"]
            action = story["action"]
            thought = story["thought"]
            impact = story["impact"]
            day = story["day"]
            behavior = story["behavior"]
            base_p = story["base_price"]
            
            # Determine card style based on impact
            if cust["status"] == "Churned":
                card_style = "log-card-failed"
                status_icon = "💀"
            elif impact > 0:
                card_style = "log-card-success"
                status_icon = "✅"
            elif impact < 0:
                card_style = "log-card-failed"
                status_icon = "⚠️"
            else:
                card_style = "log-card-neutral"
                status_icon = "ℹ️"
                
            channel_name, badge_class = get_action_details(action)
            message_text = get_message_content(action, cust["name"])
            
            # Calculate actual price paid if discount is applied
            # If SMS_DISCOUNT or EMAIL_DISCOUNT, price is discounted
            price_multiplier = 0.7 if "DISCOUNT" in action and impact > 0 else 1.0
            actual_price = round(base_p * price_multiplier, 2)
            
            st.markdown(f"""
            <div class="premium-card {card_style}">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <div>
                        <span class="channel-badge {badge_class}">{channel_name}</span>
                        <strong style="font-size: 1.15rem; margin-left: 0.5rem; color: #fff;">{status_icon} {cust['name']}</strong>
                        <span style="color: #94a3b8; font-size: 0.8rem; margin-left: 0.5rem;">Day {day} • {cust['persona']}</span>
                    </div>
                    <div style="text-align: right;">
                        <span style="color: #38bdf8; font-weight: 700; font-size: 1.1rem;">${actual_price}/mo</span>
                        {f'<span style="text-decoration: line-through; color: #64748b; font-size: 0.85rem; margin-left: 0.3rem;">${base_p}</span>' if price_multiplier < 1.0 else ''}
                    </div>
                </div>
                <div style="font-size: 0.9rem; line-height: 1.5; margin-top: 0.5rem; color: #cbd5e1;">
                    <div style="margin-bottom: 0.3rem;">💻 <strong>Behavior Check:</strong> {behavior}</div>
                    <div style="margin-bottom: 0.3rem;">🧠 <strong>Agent Reasoning:</strong> <i>{thought}</i></div>
                    <div style="margin-bottom: 0.3rem; background: rgba(0,0,0,0.2); padding: 0.5rem; border-radius: 6px;">📱 <strong>Sent Outreach Copy:</strong> <code>{message_text}</code></div>
                    <div style="margin-top: 0.4rem; display: flex; justify-content: space-between;">
                        <span>📊 Engagement Impact: <strong style="color: {'#10b981' if impact >= 0 else '#ef4444'};">{'🏼' if impact == 0 else ('+' if impact > 0 else '')}{impact} Score</strong></span>
                        <span>Current Total Score: <strong>{cust['engagement_score']}/100</strong></span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Live log is empty. Use the simulate button to watch the CLM agent execute actions.")

with col_right:
    st.markdown("### 🏷️ Product Prices & Trends")
    
    # Price Trend Chart
    df_prices = pd.DataFrame(st.session_state.price_history)
    df_prices.index.name = "Day"
    st.line_chart(df_prices, use_container_width=True)
    
    # Product list layout
    st.markdown("##### Current Base Catalog")
    for prod_id, data in products.items():
        current_p = st.session_state.base_prices[prod_id]
        features_list = " • ".join(data["features"][:3])
        st.markdown(f"""
        <div class="premium-card" style="padding: 1rem; margin-bottom: 0.8rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="font-weight: 700; color: #fff;">{data['name']}</div>
                <div style="color: #a855f7; font-weight: 800; font-size: 1.15rem;">${current_p}</div>
            </div>
            <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 0.3rem;">{data['description']}</div>
            <div style="font-size: 0.7rem; color: #3b82f6; margin-top: 0.3rem; font-weight: 500;">{features_list}</div>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# ROW 3: CUSTOMER LIFECYCLE OVERVIEW
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("### 👥 Customer Directory & Lifecycle Stage")

cols = st.columns(5)
for idx, customer in enumerate(st.session_state.customers):
    prod_id = customer.get("product_id", "P001")
    prod_name = products[prod_id]["name"]
    base_price = st.session_state.base_prices[prod_id]
    
    with cols[idx]:
        # Determine status background
        if customer["status"] == "Churned":
            status_style = "border-top: 4px solid #ef4444; background: rgba(239, 68, 68, 0.05);"
            status_text = "💀 CHURNED"
        else:
            status_style = "border-top: 4px solid #10b981;"
            status_text = "✅ ACTIVE"
            
        st.markdown(f"""
        <div class="premium-card" style="{status_style} padding: 1.2rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <strong style="color: #fff; font-size: 1.1rem;">{customer['name']}</strong>
                <span style="font-size: 0.7rem; font-weight: 700; color: {'#10b981' if customer['status'] == 'Active' else '#ef4444'};">{status_text}</span>
            </div>
            <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 0.2rem;">{customer['persona']}</div>
            <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.05); margin: 0.6rem 0;">
            <div style="font-size: 0.8rem; display: grid; gap: 0.25rem;">
                <div>🏷️ <strong>Stage:</strong> {customer['lifecycle_stage']}</div>
                <div>💼 <strong>Plan:</strong> {prod_name}</div>
                <div>💬 <strong>SMS Outreach:</strong> {customer.get('sms_count', 0)}/2</div>
                <div>🎁 <strong>Discounts Applied:</strong> {customer.get('discount_count', 0)}/2</div>
                <div>⏱️ <strong>Inactivity:</strong> {customer['time_since_last_event']} days</div>
            </div>
            <div style="margin-top: 0.8rem;">
                <div style="display: flex; justify-content: space-between; font-size: 0.75rem; margin-bottom: 0.25rem;">
                    <span>Engagement Score</span>
                    <strong>{customer['engagement_score']}/100</strong>
                </div>
                <div style="width: 100%; height: 6px; background: rgba(255,255,255,0.05); border-radius: 3px; overflow: hidden;">
                    <div style="width: {customer['engagement_score']}%; height: 100%; background: {'#ef4444' if customer['engagement_score'] < 30 else ('#fbbf24' if customer['engagement_score'] < 70 else '#10b981')};"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
