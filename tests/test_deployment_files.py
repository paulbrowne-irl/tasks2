import json
from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_firebase_rewrites_to_flask_cloud_run_service():
    config = json.loads((ROOT / "firebase.json").read_text())
    rewrite = config["hosting"]["rewrites"][0]
    assert rewrite["run"]["serviceId"] == "task-management"
    assert rewrite["run"]["pinTag"] is True


def test_dockerfile_runs_flask_app():
    dockerfile = (ROOT / "Dockerfile").read_text()
    assert "python:3.12-slim" in dockerfile
    assert '"--factory"' in dockerfile
    assert '"app:create_app"' in dockerfile


def test_env_example_documents_required_configuration():
    text = (ROOT / ".env.example").read_text()
    for key in ("FLASK_SECRET_KEY", "TASKS_SPREADSHEET_ID", "GOOGLE_CLIENT_ID", "FIREBASE_PROJECT_ID"):
        assert key in text
