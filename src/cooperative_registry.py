import json
import os

BENCHMARK_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "cooperative_benchmarks.json")

DEFAULT_BENCHMARKS = {
    "SEND_SMS_DISCOUNT": {"success_rate": 0.45, "runs": 120},
    "SEND_SMS_TUTORIAL": {"success_rate": 0.35, "runs": 90},
    "SEND_EMAIL_DISCOUNT": {"success_rate": 0.55, "runs": 200},
    "SEND_EMAIL_TUTORIAL": {"success_rate": 0.65, "runs": 180},
    "SEND_IN_APP_MESSAGE": {"success_rate": 0.70, "runs": 300},
    "SEND_PUSH_NOTIFICATION": {"success_rate": 0.40, "runs": 150},
    "CUSTOM_BUNDLE": {"success_rate": 0.60, "runs": 80}
}

def load_cooperative_benchmarks():
    """Loads shared multi-tenant benchmark metrics"""
    if not os.path.exists(os.path.dirname(BENCHMARK_FILE)):
        os.makedirs(os.path.dirname(BENCHMARK_FILE), exist_ok=True)
        
    if not os.path.exists(BENCHMARK_FILE):
        with open(BENCHMARK_FILE, "w") as f:
            json.dump(DEFAULT_BENCHMARKS, f, indent=2)
        return DEFAULT_BENCHMARKS
        
    try:
        with open(BENCHMARK_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_BENCHMARKS

def sync_local_to_global(local_registry):
    """Securely and anonymously pools local conversion metrics to global registry"""
    global_metrics = load_cooperative_benchmarks()
    
    for customer_id, records in local_registry.items():
        for action, status in records.items():
            if action in global_metrics:
                runs = global_metrics[action]["runs"]
                success_rate = global_metrics[action]["success_rate"]
                
                # Increment metrics
                new_runs = runs + 1
                is_success = 1.0 if status == "SUCCESS" else 0.0
                new_rate = round(((success_rate * runs) + is_success) / new_runs, 3)
                
                global_metrics[action]["runs"] = new_runs
                global_metrics[action]["success_rate"] = new_rate
                
    try:
        with open(BENCHMARK_FILE, "w") as f:
            json.dump(global_metrics, f, indent=2)
    except Exception as e:
        print("Cooperative Sync Failed:", e)
        
    return global_metrics
