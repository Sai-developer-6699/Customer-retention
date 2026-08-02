# 🤖 Autonomous Customer Lifecycle Management (CLM) Agent

> An AI-powered autonomous agent that manages customer engagement through an intelligent observe-decide-act-evaluate-learn (OODA) loop. Built with LangChain, OpenAI, and Streamlit.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Latest-red.svg)](https://streamlit.io/)
[![LangChain](https://img.shields.io/badge/LangChain-Latest-green.svg)](https://langchain.com/)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Key Components](#key-components)
- [Requirements](#requirements)
- [How It Works](#how-it-works)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

This project demonstrates **agentic AI** in action through an autonomous customer lifecycle management system. The agent:

1. **Observes** customer behavior and engagement patterns
2. **Decides** on optimal actions using LLM-powered strategic reasoning
3. **Acts** by sending personalized interventions (discounts, tutorials, etc.)
4. **Evaluates** the impact of actions on customer engagement
5. **Learns** from outcomes to adapt future strategies

### Why Agentic AI?

Unlike traditional rule-based systems, this agent:
- ✅ **Adapts** its strategy based on learned outcomes
- ✅ **Avoids** repeating failed approaches
- ✅ **Explores** new strategies while learning
- ✅ **Personalizes** actions based on customer segments
- ✅ **Demonstrates** autonomous decision-making with reasoning

---

## ✨ Features

### Core Capabilities

- 🤖 **Autonomous Decision Making**: LLM-powered agent chooses actions with reasoning
- 🧠 **Memory-Based Learning**: Tracks successful/failed strategies per customer segment
- 📊 **Dynamic Adaptation**: Automatically avoids actions that failed before
- 🎨 **Storytelling UI**: Beautiful narrative-based interface (no boring tables!)
- 👥 **Multiple Customer Personas**: 5 diverse customer types for realistic simulation
- 📈 **Engagement Tracking**: Real-time monitoring of customer engagement scores
- 💀 **Churn Detection**: Automatic identification and handling of churned customers
- 🔔 **Learning Visualization**: Real-time display of agent learning in sidebar

### UI Features

- **Story Cards**: Visual narrative showing Thought → Action → Impact
- **Learning Ledger**: Sidebar showing agent's memory and adaptations
- **Engagement Metrics**: Progress bars and score indicators
- **Mild Color Palette**: Professional pastel colors for better UX
- **One-Button Autonomy**: Simple interface with clear simulation steps

---

## 🏗️ Architecture

The system follows a clean modular architecture:

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI (app.py)                │
│  - Story cards, Learning ledger, Customer overview     │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
┌───────▼────────┐          ┌─────────▼──────────┐
│  Agents        │          │  Simulation        │
│  (agents.py)   │◄─────────┤  (simulation.py)   │
│                │          │                     │
│ - Observe      │          │ - Behavior sim      │
│ - Decide (LLM) │          │ - Impact eval       │
└───────┬────────┘          └─────────┬──────────┘
        │                             │
        └──────────────┬──────────────┘
                       │
              ┌────────▼────────┐
              │  Memory Store   │
              │ (memory_store.py)│
              │                 │
              │ - Strategy reg  │
              │ - Learning logs │
              └─────────────────┘
```

### Agentic Loop (OODA)

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ OBSERVE  │───▶│ DECIDE   │───▶│   ACT    │───▶│ EVALUATE │───▶│  LEARN   │
│ Behavior │    │ (LLM)    │    │  Action  │    │  Impact  │    │  Memory  │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
     ▲                                                                    │
     └──────────────────────────────────────────────────────────────────┘
                              (Feedback Loop)
```

---

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- OpenAI API key (for GPT-4o-mini)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/customer-agent.git
cd customer-agent
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Set Up Environment Variables

Create a `.env` file in the root directory:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

**Note**: The `.env` file is already in `.gitignore` to protect your API keys.

### Step 4: Verify Installation

```bash
python verify_agent.py
```

You should see:
```
Testing simulation exports...
PASS: Simulation exports work.
Testing decision_agent...
PASS: Decision agent works.
ALL TESTS PASSED
```

---

## 💻 Usage

### Start the Streamlit Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### Using the Application

1. **Initial State**: The app loads with 5 customer personas ready for simulation
2. **Run Simulation**: Click **"▶️ Run Next Day Simulation"** button
3. **Observe Results**: 
   - View story cards showing agent decisions
   - Check Learning Ledger in sidebar for adaptations
   - Monitor customer engagement scores
4. **Iterate**: Click the button multiple times to see the agent learn and adapt

### Understanding the UI

#### Main Dashboard
- **Story Cards**: Each card shows a customer's journey with:
  - 🧠 Agent's thought process
  - 🎯 Action taken
  - 📊 Impact on engagement

#### Sidebar (Learning Ledger)
- **Day Counter**: Current simulation day
- **Learning Status**: Shows agent's learning progress
- **Strategy Memory**: Successful/failed actions per persona
- **Recent Learning Updates**: Latest adaptations
- **Customer Status**: Active vs Churned summary

#### Customer Overview
- Quick view of all customers with engagement scores
- Visual indicators for churned customers

---

## 📁 Project Structure

```
customer-agent/
├── app.py                 # Streamlit UI application
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in git)
├── .gitignore            # Git ignore rules
├── README.md             # This file
│
├── data/
│   └── customer.py       # Customer personas and data
│
├── src/
│   ├── agents.py         # Agent logic (observe, decide)
│   ├── simulation.py     # Environment simulation (act, evaluate)
│   ├── memory_store.py   # Learning/memory system
│   └── tools.py          # Action tools (future expansion)
│
└── verify_agent.py       # Test/verification script
```

---

## 🔧 Key Components

### 1. **Agents** (`src/agents.py`)

- **`behavior_analysis_agent(customer)`**: Deterministic analysis of customer state
- **`decision_agent(customer, memory)`**: LLM-powered strategic decision making

**Features:**
- Hard rules for edge cases (churned customers)
- LLM integration for strategic reasoning
- Forbidden actions filtering based on memory
- Fallback logic for error handling

### 2. **Simulation** (`src/simulation.py`)

- **`simulate_user_behavior(customer)`**: Simulates customer activity
- **`evaluate_agent_action(customer, action, memory)`**: Evaluates action impact

**Features:**
- Customer sensitivity-based impact calculation
- Engagement score updates
- Churn detection and handling
- Memory integration for learning

### 3. **Memory Store** (`src/memory_store.py`)

- **`StrategyMemory`**: Class for tracking learning

**Methods:**
- `update(customer, action, status)`: Record action outcomes
- `get_forbidden_actions(customer)`: Get failed actions to avoid
- `get_success_hints(customer)`: Get successful strategies

**Memory Format:**
```python
{
    "Onboarding_Sam": {
        "SEND_DISCOUNT": "SUCCESS",
        "SEND_TUTORIAL": "FAILED"
    }
}
```

### 4. **UI** (`app.py`)

- Streamlit-based storytelling interface
- Real-time learning visualization
- Beautiful card-based layout

---

## 📦 Requirements

See `requirements.txt` for full list:

- `streamlit` - Dashboard UI
- `langchain` - Agent orchestration
- `langchain-openai` - OpenAI integration
- `python-dotenv` - Environment variable management
- `pandas` - Data handling
- `pydantic` - Data validation (optional)

---

## 🎓 How It Works

### Example Flow

1. **Customer State**: "Student Sam" has engagement score of 85, inactive for 0 days
2. **Observe**: Agent analyzes → "Healthy customer, price-sensitive"
3. **Decide**: LLM reasons → "Send discount to boost engagement"
4. **Act**: System sends `SEND_DISCOUNT` action
5. **Evaluate**: Impact calculated → +8 engagement (successful!)
6. **Learn**: Memory updated → "SEND_DISCOUNT was SUCCESS for Onboarding_Sam"

### Learning Example

**First Attempt:**
- Agent tries `SEND_TUTORIAL` on "Corporate Clara"
- Impact: -3 (failed - she's too busy for tutorials)
- Memory: `"SEND_TUTORIAL": "FAILED"` for "Retention_Clara"

**Next Attempt:**
- Agent sees `SEND_TUTORIAL` is forbidden for Clara
- Agent chooses `SEND_DISCOUNT` instead (or other allowed action)
- Adapts strategy based on learned failure!

---

## 📸 Screenshots

*Note: Add screenshots of your UI here*

### Main Dashboard
- Story cards showing customer interactions

### Learning Ledger
- Strategy memory and adaptations

### Customer Overview
- Engagement scores and status

---

## 🤝 Contributing

This is a hackathon project. Suggestions and improvements are welcome!

### Completed Enhancements

- [x] **Add more action types**: Extended the action space to support specific channels: SMS coupons, SMS guides, Email discounts, Email tutorials, In-App modals, and Mobile push notifications.
- [x] **Implement A/B testing for actions**: Created a baseline comparison between AI-driven CLM (Group A) and rules-based static outreach (Group B) with dynamic lift metrics.
- [x] **Add customer lifetime value calculations**: Implemented dynamic CLV accumulation on each customer profile reflecting billing price walks and applied discount benefits.
- [x] **Export learning data to CSV/JSON**: Added interactive download buttons in the dashboard sidebar to export Strategy Memory as JSON and Story Logs as CSV.
- [x] **Add metrics dashboard with charts**: Integrated interactive subscription price trend line charts alongside channel-specific volume and success rate analytics.
- [x] **Support for multiple LLM providers**: Added sidebar controls to switch the active OODA decision engine between OpenAI (`gpt-4o-mini`) and Google Gemini (`gemini-1.5-flash`).
- [x] **Add configuration file for parameters**: Externalized parameters (fatigue limits, base price fluctuations, and churn scores) into `config.json`.

---

## 📝 Notes

### API Costs

This project uses OpenAI's GPT-4o-mini model, which is cost-effective:
- ~$0.15 per 1M input tokens
- ~$0.60 per 1M output tokens
- Each decision uses minimal tokens (~500-1000 tokens)

### Performance

- Decision latency: ~1-2 seconds per customer (LLM call)
- UI updates: Real-time
- Memory operations: Instant (in-memory dictionary)

### Limitations

- Current implementation is for demonstration/learning
- Customer data is simulated (not real customer data)
- Actions are simulated (not actual email/notification sending)

---

## 📄 License

This project is created for educational/hackathon purposes.

---

## 👤 Author

Created for hackathon demonstration of agentic AI principles.

---

## 🙏 Acknowledgments

- LangChain for agent orchestration framework
- OpenAI for GPT-4o-mini model
- Streamlit for rapid UI development
- Community for inspiration and feedback

---

## 🔗 Related Resources

- [LangChain Documentation](https://python.langchain.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [OpenAI API Documentation](https://platform.openai.com/docs)

---

**⭐ If you find this project helpful, consider giving it a star!**

---

*Last Updated: January 2025*
