"""Configuration models."""

from typing import Optional
from pydantic_settings import BaseSettings


class AgentConfig(BaseSettings):
    """Agent configuration from environment variables."""

    # LLM
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 4096

    # Agent
    agent_name: str = "PowerfulAIAgent"
    agent_description: str = "A sophisticated multi-tool AI agent"
    max_iterations: int = 10
    timeout: int = 300
    verbose: bool = True
    debug: bool = False

    # GitHub
    github_token: Optional[str] = None
    github_user: Optional[str] = None
    github_api_endpoint: str = "https://api.github.com"

    # Database
    database_url: str = "sqlite:///./agent.db"
    redis_url: Optional[str] = None

    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/agent.log"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
