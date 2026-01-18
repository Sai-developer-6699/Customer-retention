import sys
import os
import json
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

# Mock environment variables
os.environ["GOOGLE_API_KEY"] = "fake_key"

# Mock dependencies
sys.modules["langchain"] = MagicMock()
sys.modules["langchain.prompts"] = MagicMock()
sys.modules["langchain.schema"] = MagicMock()
sys.modules["langchain_google_genai"] = MagicMock()
sys.modules["dotenv"] = MagicMock()

# Mock ChatGoogleGenerativeAI before importing agent
import src.agents

# Configure the existing mock llm
mock_response = MagicMock()
mock_response.content = json.dumps({
    "thought": "User is at risk, sending discount.",
    "action": "SEND_DISCOUNT",
    "params": {}
})
src.agents.llm.invoke.return_value = mock_response

from src.agents import decision_agent
from src.simulation import simulate_user_behavior, evaluate_agent_action

def test_simulation_exports():
    print("Testing simulation exports...")
    assert callable(simulate_user_behavior), "simulate_user_behavior not exported"
    assert callable(evaluate_agent_action), "evaluate_agent_action not exported"
    print("PASS: Simulation exports work.")

def test_decision_agent():
    print("Testing decision_agent...")
    customer = {
        "name": "Test User",
        "persona": "Student",
        "history": ["Login", "Inactive"],
        "time_since_last_event": 5,
        "status": "At Risk",
        "last_action": "DO_NOTHING"
    }
    
    mock_memory = MagicMock()
    mock_memory.get_forbidden_actions.return_value = []
    mock_memory.get_success_hints.return_value = ""
    
    action = decision_agent(customer, mock_memory)
    
    print(f"Agent returned: {action}")
    assert action == "SEND_DISCOUNT", f"Expected SEND_DISCOUNT, got {action}"
    print("PASS: Decision agent works.")

if __name__ == "__main__":
    try:
        test_simulation_exports()
        test_decision_agent()
        print("ALL TESTS PASSED")
    except Exception as e:
        print(f"TEST FAILED: {e}")
        sys.exit(1)
