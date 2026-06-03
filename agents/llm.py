from configs.settings import get_settings


class GeminiCompatibleClient:
    """Thin optional Gemini adapter.

    The platform runs without a live LLM for deterministic local demos. Set
    ENABLE_LLM=true and GEMINI_API_KEY to route generation through Gemini.
    """

    def __init__(self) -> None:
        self.settings = get_settings()

    def enabled(self) -> bool:
        return bool(self.settings.enable_llm and self.settings.gemini_api_key)

    def generate_text(self, prompt: str) -> str | None:
        if not self.enabled():
            return None
        try:
            import google.generativeai as genai
        except ImportError:
            return None

        genai.configure(api_key=self.settings.gemini_api_key)
        model = genai.GenerativeModel(self.settings.gemini_model)
        response = model.generate_content(prompt)
        return getattr(response, "text", None)
