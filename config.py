API_PROVIDER = 'gemini'  # Choose the LLM provider: 'gemini', 'openai', 'custom'

# Endpoint configuration
PROVIDER_CONFIG = {
    'gemini': {
        'endpoint': 'https://api.gemini.com/v1/',
        'api_key': 'your_gemini_api_key',
    },
    'openai': {
        'endpoint': 'https://api.openai.com/v1/',
        'api_key': 'your_openai_api_key',
    },
    'custom': {
        'endpoint': 'https://api.custombackend.com/v1/',
        'api_key': 'your_custom_api_key',
    },
}

# Automatic activation logic
def activate_llm_provider(provider):
    if provider in PROVIDER_CONFIG:
        # Assuming activation code here
t        print(f'Activating provider: {provider}')
        # Additional activation logic
    else:
        raise ValueError('Invalid provider selection')
