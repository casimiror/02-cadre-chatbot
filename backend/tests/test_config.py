from app.core.config import Settings


def test_langfuse_base_url_reads_current_and_legacy_names(monkeypatch):
    monkeypatch.setenv("LANGFUSE_BASE_URL", "https://us.cloud.langfuse.com")
    assert Settings(_env_file=None).langfuse_base_url == "https://us.cloud.langfuse.com"
    monkeypatch.delenv("LANGFUSE_BASE_URL")
    monkeypatch.setenv("LANGFUSE_HOST", "https://eu.example.com")
    assert Settings(_env_file=None).langfuse_base_url == "https://eu.example.com"
