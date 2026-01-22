class StrategyMemory:
    def __init__(self):
        """
        Format:
        {
          "Churn Risk_Betty": {
              "SEND_DISCOUNT": {"SUCCESS": 1, "FAILED": 2},
              "ASK_INTEREST": {"SUCCESS": 0, "FAILED": 1}
          }
        }
        """
        self.registry = {}
        self.learning_logs = []

    def _get_key(self, customer):
        """Key based on lifecycle stage + persona name (demo-friendly)."""
        persona_type = customer['name'].split()[-1]  # Sam, Clara, Betty
        return f"{customer['lifecycle_stage']}_{persona_type}"

    def update(self, customer, action, status):
        """Accumulates learning instead of overwriting it."""
        key = self._get_key(customer)

        if key not in self.registry:
            self.registry[key] = {}

        if action not in self.registry[key]:
            self.registry[key][action] = {"SUCCESS": 0, "FAILED": 0}

        self.registry[key][action][status] += 1

        log_entry = (
            f"Learned: {action} → {status} "
            f"(S:{self.registry[key][action]['SUCCESS']}, "
            f"F:{self.registry[key][action]['FAILED']}) "
            f"for {key}"
        )
        self.learning_logs.append(log_entry)
        print(f"🧠 MEMORY UPDATED: {log_entry}")

    def get_forbidden_actions(self, customer):
        """
        An action becomes forbidden if it has FAILED at least once.
        (Perfect for hackathon demos — deterministic & clear)
        """
        key = self._get_key(customer)
        if key not in self.registry:
            return []

        forbidden = []
        for action, stats in self.registry[key].items():
            if stats["FAILED"] >= 1:
                forbidden.append(action)

        return forbidden

    def get_success_hints(self, customer):
        """Returns successful strategies as human-readable hints."""
        key = self._get_key(customer)
        if key not in self.registry:
            return "No prior learnings for this persona."

        successes = [
            f"{action} (x{stats['SUCCESS']})"
            for action, stats in self.registry[key].items()
            if stats["SUCCESS"] > 0
        ]

        if successes:
            return "Previously successful: " + ", ".join(successes)

        return "No successful strategies yet."
