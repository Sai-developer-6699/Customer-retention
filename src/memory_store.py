class StrategyMemory:
    def __init__(self):
        # Format: {"Onboarding_Student": {"SEND_DISCOUNT": "SUCCESS", "SEND_TUTORIAL": "FAILED"}}
        self.registry = {}
        # A simple list to track the "Story of Learning" for your demo logs
        self.learning_logs = []

    def _get_key(self, customer):
        """Creates a lookup key based on stage and persona type."""
        persona_type = customer['name'].split()[-1] # e.g., 'Sam' or 'Clara'
        return f"{customer['lifecycle_stage']}_{persona_type}"

    def update(self, customer, action, status):
        """Updates the memory with the result of an action."""
        key = self._get_key(customer)
        if key not in self.registry:
            self.registry[key] = {}
        
        self.registry[key][action] = status
        
        log_entry = f"Learned: {action} was a {status} for {key}"
        self.learning_logs.append(log_entry)
        print(f"🧠 MEMORY UPDATED: {log_entry}")

    def get_forbidden_actions(self, customer):
        """Returns a list of actions that have failed for this persona type."""
        key = self._get_key(customer)
        if key not in self.registry:
            return []
        
        # Return actions marked as FAILED
        return [action for action, status in self.registry[key].items() if status == "FAILED"]

    def get_success_hints(self, customer):
        """Returns actions that have worked in the past for this persona."""
        key = self._get_key(customer)
        if key not in self.registry:
            return ""
        
        successes = [action for action, status in self.registry[key].items() if status == "SUCCESS"]
        if successes:
            return f"Note: {', '.join(successes)} has worked for this segment before."
        return ""