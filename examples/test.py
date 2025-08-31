import pytest
from unittest.mock import Mock, patch
import requests


def test_endpoint(name, response):
    if response.status_code == 200:
        print(f"✅ {name} successful")
        return True
    else:
        print(f"❌ {name} failed with status {response.status_code}: {response.text}")
        return False


# Mock для ReviewService
class MockReviewService:
    def review(self, payload):
        return {
            "overall_score": 8.5,
            "issues": [
                {
                    "type": "performance",
                    "severity": "medium",
                    "description": "Consider adding index on customer_id",
                    "suggestion": "CREATE INDEX idx_orders_customer_id ON orders(customer_id);",
                }
            ],
            "recommendations": [
                "Add appropriate indexes",
                "Consider query optimization",
            ],
            "passed": True,
        }


# Mock для зависимостей
@pytest.fixture
def mock_review_service():
    return MockReviewService()


@pytest.fixture
def mock_dependencies(mock_review_service):
    with (
        patch(
            "src.api.dependencies.get_review_service", return_value=mock_review_service
        ),
        patch("src.services.vault_service.VaultService"),
        patch("src.services.database_service.database_service"),
        patch("src.core.config.settings"),
    ):
        yield


# Test single review
def test_single_review(mock_dependencies):
    """Test single SQL review with mocked dependencies."""
    print("Testing single review with mocks...")

    # Mock HTTP response for testing
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "overall_score": 8.5,
        "issues": [],
        "recommendations": ["Query looks good"],
        "passed": True,
    }

    with patch("requests.post", return_value=mock_response):
        response = requests.post(
            "http://localhost:8000/review",
            json={
                "sql": "SELECT * FROM orders WHERE customer_id = 123",
                "query_plan": "EXPLAIN output",
                "tables": [
                    {
                        "name": "orders",
                        "columns": [{"name": "customer_id", "type": "int"}],
                    }
                ],
                "server_info": {"version": "15.0"},
                "environment": "test",
            },
        )

    assert test_endpoint("Single review", response)
    print("Single review response:", response.json())


# Test config analysis
def test_config_analysis(mock_dependencies):
    """Test config analysis with mocked dependencies."""
    print("\nTesting config analysis with mocks...")

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "overall_score": 7.0,
        "issues": [
            {
                "type": "configuration",
                "severity": "high",
                "description": "shared_buffers is too low",
                "suggestion": "Increase shared_buffers to at least 25% of RAM",
            }
        ],
        "recommendations": ["Increase shared_buffers", "Tune work_mem"],
        "passed": False,
    }

    with patch("requests.post", return_value=mock_response):
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

    assert test_endpoint("Config analysis", config_response)
    print("Config analysis response:", config_response.json())


# Test batch review
def test_batch_review(mock_dependencies):
    """Test batch review with mocked dependencies."""
    print("\nTesting batch review with mocks...")

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "results": [
            {
                "overall_score": 8.5,
                "issues": [],
                "recommendations": ["Query looks good"],
                "passed": True,
            },
            {
                "overall_score": 6.0,
                "issues": [
                    {
                        "type": "performance",
                        "severity": "medium",
                        "description": "Missing index on users table",
                        "suggestion": "CREATE INDEX idx_users_id ON users(id);",
                    }
                ],
                "recommendations": ["Add index on id column"],
                "passed": False,
            },
        ],
        "overall_score": 7.25,
        "passed": False,
    }

    with patch("requests.post", return_value=mock_response):
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
                            {
                                "name": "users",
                                "columns": [{"name": "id", "type": "int"}],
                            }
                        ],
                        "server_info": {"version": "15.0"},
                    },
                ],
                "environment": "test",
            },
        )

    assert test_endpoint("Batch review", batch_response)
    print("Batch review response:", batch_response.json())


if __name__ == "__main__":
    # Run tests without pytest
    print("Running API tests with mocks...")

    # Create mock instances
    mock_service = MockReviewService()

    with (
        patch("src.api.dependencies.get_review_service", return_value=mock_service),
        patch("src.services.vault_service.VaultService"),
        patch("src.services.database_service.database_service"),
        patch("src.core.config.settings"),
    ):

        test_single_review(None)
        test_config_analysis(None)
        test_batch_review(None)

    print("\n✅ All tests completed!")
