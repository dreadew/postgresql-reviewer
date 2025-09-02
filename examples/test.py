import requests


def test_endpoint(name, response):
    if response.status_code == 200:
        print(f"✅ {name} successful")
        return True
    else:
        print(f"❌ {name} failed with status {response.status_code}: {response.text}")
        return False


# Test single review
print("Testing single review...")
response = requests.post(
    "http://localhost:8000/review",
    json={
        "sql": "SELECT * FROM orders WHERE customer_id = 123",
        "query_plan": "EXPLAIN output",
        "tables": [
            {"name": "orders", "columns": [{"name": "customer_id", "type": "int"}]}
        ],
        "server_info": {"version": "15.0"},
        "environment": "test",
    },
)
test_endpoint("Single review", response)
if response.status_code == 200:
    print("Single review response:", response.json())

# Test config analysis
print("\nTesting config analysis...")
config_response = requests.post(
    "http://localhost:8000/config/analyze",
    json={
        "config": {
            "shared_buffers": "128MB",
            "work_mem": "4MB",
            "maintenance_work_mem": "64MB",
        },
        "environment": "production",
    },
)
test_endpoint("Config analysis", config_response)
if config_response.status_code == 200:
    print("Config analysis response:", config_response.json())

# Test batch review
print("\nTesting batch review...")
batch_response = requests.post(
    "http://localhost:8000/review/batch",
    json={
        "queries": [
            {
                "sql": "SELECT * FROM orders WHERE customer_id = 123",
                "query_plan": "EXPLAIN output",
                "tables": [
                    {
                        "name": "orders",
                        "columns": [{"name": "customer_id", "type": "int"}],
                    }
                ],
                "server_info": {"version": "15.0"},
            },
            {
                "sql": "SELECT COUNT(*) FROM users",
                "query_plan": "EXPLAIN output",
                "tables": [
                    {"name": "users", "columns": [{"name": "id", "type": "int"}]}
                ],
                "server_info": {"version": "15.0"},
            },
        ],
        "environment": "test",
    },
)
test_endpoint("Batch review", batch_response)
if batch_response.status_code == 200:
    print("Batch review response:", batch_response.json())
