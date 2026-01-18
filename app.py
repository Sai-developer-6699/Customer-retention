import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.2,
    api_key=os.getenv("OPENAI_API_KEY")
)

import streamlit as st
import time

from data.customer import personas
from src.agents import behavior_analysis_agent, decision_agent
from src.simulation import simulate_user_behavior, evaluate_agent_action
from src.memory_store import StrategyMemory

# ─────────────────────────────────────────────
# STREAMLIT CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="🤖 Agentic CLM | Autonomous Customer Lifecycle",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CUSTOM CSS FOR MILD COLOR PALETTE
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Mild Story Card Colors */
    .story-card-success {
        background: linear-gradient(135deg, #c8e6c9 0%, #a5d6a7 100%);
        border: 1px solid #81c784;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .story-card-warning {
        background: linear-gradient(135deg, #ffe0b2 0%, #ffcc80 100%);
        border: 1px solid #ffb74d;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .story-card-danger {
        background: linear-gradient(135deg, #e1bee7 0%, #ce93d8 100%);
        border: 1px solid #ba68c8;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .story-card-neutral {
        background: linear-gradient(135deg, #e0e0e0 0%, #bdbdbd 100%);
        border: 1px solid #9e9e9e;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    /* Mild Action Container */
    .action-container {
        background: rgba(255, 255, 255, 0.6);
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border: 1px solid rgba(0, 0, 0, 0.1);
    }
    
    /* Mild Memory Update Dialog */
    .memory-update-dialog {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-radius: 4px;
        font-size: 0.9rem;
        color: #333333 !important;
    }
    
    .memory-update-dialog strong {
        color: #1a1a1a !important;
    }
    
    .memory-update-dialog small {
        color: #555555 !important;
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

# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────
def get_action_icon(action):
    icons = {
        "SEND_DISCOUNT": "🎁",
        "SEND_TUTORIAL": "📚",
        "ASK_INTEREST": "💬",
        "DO_NOTHING": "😴"
    }
    return icons.get(action, "⚡")

def format_impact(impact):
    if impact > 0:
        return f"+{impact} ↗"
    elif impact < 0:
        return f"{impact} ↘"
    return f"{impact} →"

def get_impact_color(impact):
    if impact > 0:
        return ":green"
    elif impact < 0:
        return ":red"
    return ":gray"

def count_personas_evaluated(memory):
    """Count unique persona types that have been evaluated"""
    evaluated_personas = set()
    for key in memory.registry.keys():
        # Extract persona from key like "Onboarding_Sam"
        persona = key.split('_')[-1]
        evaluated_personas.add(persona)
    return len(evaluated_personas)

# ─────────────────────────────────────────────
# SIDEBAR: LEARNING LEDGER & STATS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧠 Agent Learning Ledger")
    st.markdown("---")
    
    # Day Counter
    st.metric("📅 Day", st.session_state.day_count)
    
    # Learning Status (Dynamic)
    personas_evaluated = count_personas_evaluated(st.session_state.memory)
    total_registry_entries = sum(len(strategies) for strategies in st.session_state.memory.registry.values())
    
    if st.session_state.day_count == 0:
        st.info("🔍 **Agent is exploring...**\n\nNo simulation run yet. The agent hasn't learned any patterns.")
    elif personas_evaluated < 5:
        st.warning(f"🔍 **Agent is exploring...**\n\nEvaluated {personas_evaluated}/5+ persona types. Learning in progress.")
    else:
        st.success(f"✅ **Agent has learned!**\n\nEvaluated {personas_evaluated} persona types with {total_registry_entries} strategy memories.")
    
    st.markdown("---")
    
    # Learning Registry (Show action results per persona)
    if st.session_state.memory.registry:
        st.markdown("### 🎓 Strategy Memory by Persona")
        for key, strategies in st.session_state.memory.registry.items():
            # Format: "Onboarding_Sam" -> "Sam (Onboarding)"
            parts = key.split('_', 1)
            if len(parts) == 2:
                persona_name = parts[1]
                lifecycle_stage = parts[0]
                st.markdown(f"**{persona_name}** ({lifecycle_stage})")
            else:
                st.markdown(f"**{key}**")
            
            for action, status in strategies.items():
                status_icon = "✅" if status == "SUCCESS" else "❌"
                action_icon = get_action_icon(action)
                st.markdown(f"  {status_icon} {action_icon} `{action}` → {status}")
            st.markdown("")
    else:
        st.info("🎓 No learning entries yet.")
    
    st.markdown("---")
    
    # Recent Memory Updates (Last 5)
    if st.session_state.memory_updates:
        st.markdown("### 🔔 Recent Learning Updates")
        for update in st.session_state.memory_updates[-5:]:
            with st.container():
                st.markdown(f"""
                <div class="memory-update-dialog">
                    <strong style="color: #1a1a1a;">{update['status_icon']} {update['action']}</strong><br>
                    <small style="color: #555555;">{update['message']}</small>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("### 🔔 Recent Learning Updates")
        st.caption("No learning updates yet. Run simulation to see agent learning.")
    
    st.markdown("---")
    
    # Customer Status Summary
    st.markdown("### 👥 Customer Status")
    active_count = sum(1 for c in st.session_state.customers if c.get("status") == "Active")
    churned_count = sum(1 for c in st.session_state.customers if c.get("status") == "Churned")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("✅ Active", active_count)
    with col2:
        st.metric("💀 Churned", churned_count)
    
    # Reset Button
    st.markdown("---")
    if st.button("🔄 Reset Simulation", use_container_width=True):
        st.session_state.customers = personas
        st.session_state.memory = StrategyMemory()
        st.session_state.story_log = []
        st.session_state.day_count = 0
        st.session_state.memory_updates = []
        st.rerun()

# ─────────────────────────────────────────────
# MAIN HEADER
# ─────────────────────────────────────────────
st.title("🤖 Autonomous Customer Lifecycle Agent")
st.markdown("""
**An AI agent that observes, decides, acts, and learns from every customer interaction.**

Each step tells a story of strategic decision-making and adaptation.
""")
st.markdown("---")

# ─────────────────────────────────────────────
# BIG ACTION BUTTON (CLEAR AUTONOMY STEP)
# ─────────────────────────────────────────────
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    if st.button("▶️ **Run Next Day Simulation**", use_container_width=True, type="primary"):
        st.session_state.day_count += 1
        daily_stories = []
        day_memory_updates = []
        
        with st.spinner("🧠 Agent is thinking and making decisions..."):
            # Track learning logs before
            learning_logs_before = len(st.session_state.memory.learning_logs)
            
            for customer in st.session_state.customers:
                
                # Skip churned customers
                if customer.get("status") == "Churned":
                    continue
                
                # 1. ENVIRONMENT: Simulate behavior
                behavior_log = simulate_user_behavior(customer)
                
                # 2. OBSERVE
                _ = behavior_analysis_agent(customer)
                
                # 3. DECIDE (returns dict with thought + action)
                decision = decision_agent(customer, st.session_state.memory)
                action = decision.get("action")
                thought = decision.get("thought", "No reasoning provided.")
                
                # 4. ACT + EVALUATE
                impact = evaluate_agent_action(
                    customer,
                    action,
                    st.session_state.memory
                )
                
                # 5. Track memory updates (check if new learning log was added)
                if action != "DO_NOTHING" and len(st.session_state.memory.learning_logs) > learning_logs_before:
                    # New learning occurred - get the latest log entry
                    latest_log = st.session_state.memory.learning_logs[-1]
                    # Format: "Learned: SEND_DISCOUNT was a SUCCESS for Onboarding_Sam"
                    if "SUCCESS" in latest_log:
                        status_icon = "✅"
                        status = "SUCCESS"
                    else:
                        status_icon = "❌"
                        status = "FAILED"
                    
                    update_msg = latest_log.replace("Learned: ", "")
                    day_memory_updates.append({
                        "status_icon": status_icon,
                        "action": action,
                        "message": update_msg
                    })
                    learning_logs_before = len(st.session_state.memory.learning_logs)
                
                # 6. BUILD STORY
                daily_stories.append({
                    "customer": customer.copy(),  # Copy to preserve state at decision time
                    "thought": thought,
                    "action": action,
                    "impact": impact,
                    "behavior": behavior_log
                })
        
        # Add to story log and memory updates
        st.session_state.story_log.extend(daily_stories)
        st.session_state.memory_updates.extend(day_memory_updates)
        
        # Show success message
        st.success(f"✨ Day {st.session_state.day_count} completed! {len(daily_stories)} decisions made.")

st.markdown("---")

# ─────────────────────────────────────────────
# STORY TELLING UI: Show Recent Stories (No HTML code displayed)
# ─────────────────────────────────────────────
if st.session_state.story_log:
    st.markdown("### 📖 Agent Decision Stories")
    
    # Show latest day's stories (or all if less than 5)
    recent_stories = st.session_state.story_log[-5:] if len(st.session_state.story_log) > 5 else st.session_state.story_log
    
    for story in recent_stories:
        customer = story["customer"]
        thought = story["thought"]
        action = story["action"]
        impact = story["impact"]
        status = customer.get("status", "Active")
        
        # Determine card class based on impact and status
        if status == "Churned":
            card_class = "story-card-danger"
        elif impact > 0:
            card_class = "story-card-success"
        elif impact < 0:
            card_class = "story-card-warning"
        else:
            card_class = "story-card-neutral"
        
        action_icon = get_action_icon(action)
        impact_text = format_impact(impact)
        
        # Build story card HTML (all in one block to avoid HTML display)
        status_badge = "💀" if status == "Churned" else "✅"
        impact_color_class = get_impact_color(impact).replace(":", "")
        
        card_html = f'''
        <div class="{card_class}" style="margin: 1.5rem 0;">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                <div>
                    <h3 style="margin: 0; color: #333;">{status_badge} {customer['name']}</h3>
                    <p style="margin: 0.3rem 0; color: #666; font-size: 0.9rem;">{customer.get('persona', '')}</p>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 1.1rem; font-weight: bold; color: #333;">{customer.get('engagement_score', 0)}/100</div>
                    <div style="width: 100px; height: 8px; background: rgba(0,0,0,0.1); border-radius: 4px; margin-top: 0.3rem;">
                        <div style="width: {customer.get('engagement_score', 0)}%; height: 100%; background: #4caf50; border-radius: 4px;"></div>
                    </div>
                </div>
            </div>
            
            
                    🧠 Agent Thought:
                    {thought}

                
                    {action_icon} Action Taken:
                    {action}
                
                
                   📊 Impact:
                    {impact_text} engagement
                   
            
            {f'<div style="background: rgba(220,53,69,0.1); padding: 0.8rem; border-radius: 6px; margin-top: 1rem; text-align: center; border: 1px solid rgba(220,53,69,0.3);"><strong style="color: #dc3545;">💀 CUSTOMER CHURNED</strong></div>' if status == "Churned" else ''}
        </div>
        '''
        
        st.markdown(card_html, unsafe_allow_html=True)
else:
    st.info("👈 Click 'Run Next Day Simulation' to start the agent's autonomous decision-making journey!")

# ─────────────────────────────────────────────
# CUSTOMER OVERVIEW (Compact Cards)
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("### 👥 Customer Overview")

# Group customers by status
active_customers = [c for c in st.session_state.customers if c.get("status") != "Churned"]
churned_customers = [c for c in st.session_state.customers if c.get("status") == "Churned"]

# Active Customers
if active_customers:
    cols = st.columns(min(3, len(active_customers)))
    for idx, customer in enumerate(active_customers[:6]):  # Show max 6
        with cols[idx % 3]:
            with st.container():
                st.markdown(f"""
                **{customer['name']}**  
                📊 {customer['engagement_score']}/100  
                🎯 {customer['lifecycle_stage']}  
                ⏱️ {customer['time_since_last_event']} days inactive  
                {f"🔄 Last: `{customer['last_action']}`" if customer.get('last_action') else "🆕 New"}
                """)
                st.progress(customer['engagement_score'] / 100)

# Churned Customers (Visibly Handled)
if churned_customers:
    st.markdown("#### 💀 Churned Customers")
    churn_cols = st.columns(min(3, len(churned_customers)))
    for idx, customer in enumerate(churned_customers):
        with churn_cols[idx % 3]:
            st.error(f"**{customer['name']}** - Churned")
