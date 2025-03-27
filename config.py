# 

# Default Chat Models for commentary enrichment
DEFAULT_CHAT_MODELS = {
    "DeepSeek Reasoner": {
        "api_url": "https://api.deepseek.com/v1/chat/completions",
        "model_name": "deepseek-reasoner"
    },
    "Claude 3.5 Sonnet (via OpenRouter)": {
        "api_url": "https://openrouter.ai/api/v1/chat/completions",
        "model_name": "anthropic/claude-3-sonnet"
    }
}

# Embedding models available via OpenAI
EMBEDDING_MODELS = {
    "Small": "text-embedding-3-small",
    "Large": "text-embedding-ada-002"
}

# Embedding API endpoint (OpenAI)
EMBEDDING_API_URL = "https://api.openai.com/v1"
