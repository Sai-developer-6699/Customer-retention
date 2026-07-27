import sys
import os
import json
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

# Mock environment variables
os.environ["GOOGLE_API_KEY"] = "fake_key"
os.environ["OPENAI_API_KEY"] = "fake_key"


# Mock dependencies
sys.modules["langchain"] = MagicMock()
sys.modules["langchain.prompts"] = MagicMock()
sys.modules["langchain.schema"] = MagicMock()
sys.modules["langchain_google_genai"] = MagicMock()
sys.modules["langchain_openai"] = MagicMock()
sys.modules["dotenv"] = MagicMock()

# Mock ChatOpenAI and ChatGoogleGenerativeAI before importing agent
import src.agents

# Configure the existing mock llm
class MockResponse:
    def __init__(self, content):
        self.content = content

mock_llm_inst = MagicMock()
mock_llm_inst.invoke = MagicMock(side_effect=[
    MockResponse(json.dumps({
        "risk_assessment": "High risk - inactivity",
        "adoption_friction_points": "No login for 4 days"
    })),
    MockResponse(json.dumps({
        "recommendation_strategy": "DISCOUNT",
        "reasoning": "Price sensitive segment"
    })),
    MockResponse(json.dumps({
        "selected_action": "SEND_SMS_DISCOUNT",
        "draft_copy": "Hey Sam! Apply SAVEMORE30 for 30% off Pro Plan!"
    })),
    MockResponse(json.dumps({
        "approved": True,
        "finalized_action": "SEND_SMS_DISCOUNT",
        "finalized_copy": "Hey Sam! Apply SAVEMORE30 for 30% off Pro Plan! Reply STOP to opt out.",
        "audit_notes": "Opt-out text added for compliance."
    }))
])
src.agents.get_llm = MagicMock(return_value=mock_llm_inst)


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
        "id": "C999",
        "name": "Test User",
        "persona": "Student",
        "engagement_score": 85,
        "history": ["Login", "Inactive"],
        "time_since_last_event": 5,
        "status": "At Risk",
        "last_action": "DO_NOTHING",
        "discount_count": 0,
        "sms_count": 0,
        "segment": "Price-Sensitive",
        "lifecycle_stage": "Onboarding",
        "action_history": [],
        "sensitivity": {"discount": 0.9, "content": 0.3}
    }

    
    mock_memory = MagicMock()
    mock_memory.get_forbidden_actions.return_value = []
    mock_memory.get_success_hints.return_value = ""
    
    result = decision_agent(customer, mock_memory)
    
    print(f"Agent returned: {result}")
    assert isinstance(result, dict), f"Expected dict, got {type(result)}"
    assert result["action"] == "SEND_SMS_DISCOUNT", f"Expected SEND_SMS_DISCOUNT, got {result['action']}"
    print("PASS: Decision agent works.")

if __name__ == "__main__":
    try:
        test_simulation_exports()
        test_decision_agent()
        print("ALL TESTS PASSED")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"TEST FAILED: {e}")
        sys.exit(1)
