from src.agents.adoption import AdoptionAnalystAgent
from src.agents.pricing import DynamicPricingAgent
from src.agents.outreach import OutreachCopywriterAgent
from src.agents.auditor import ComplianceAuditorAgent

class RootOrchestratorAgent:
    """
    Google ADK-inspired Root agent that delegates tasks to subagents
    and coordinates the overall CLM retention decision loop.
    """
    def __init__(self, llm):
        self.llm = llm
        self.adoption_agent = AdoptionAnalystAgent(llm)
        self.pricing_agent = DynamicPricingAgent(llm)
        self.outreach_agent = OutreachCopywriterAgent(llm)
        self.auditor_agent = ComplianceAuditorAgent(llm)

    def run(self, customer, allowed_actions):
        # Step 1: Analyze user adoption and wobble signals
        adoption_insights = self.adoption_agent.run(customer)
        
        # Step 2: Calculate price elasticity and margin-safe pricing strategy
        pricing_insights = self.pricing_agent.run(customer, adoption_insights)
        
        # Step 3: Write personalized messaging copy matching customer context
        outreach_draft = self.outreach_agent.run(customer, pricing_insights, allowed_actions)
        
        # Step 4: Audit copy for tone, truthfulness, and regulatory compliance
        final_audit = self.auditor_agent.run(customer, outreach_draft)
        
        # Aggregated reasoning summary
        thought = (
            f"[Adoption: {adoption_insights.get('risk_assessment', 'Normal')}] "
            f"[Pricing: {pricing_insights.get('recommendation_strategy', 'DO_NOTHING')}] "
            f"[Audited Tone: {final_audit.get('audit_notes', 'Safe')}]"
        )
        
        return {
            "thought": thought,
            "action": final_audit.get("finalized_action", "DO_NOTHING"),
            "content": final_audit.get("finalized_copy", "No message."),
            "adoption_logs": adoption_insights,
            "pricing_logs": pricing_insights
        }
