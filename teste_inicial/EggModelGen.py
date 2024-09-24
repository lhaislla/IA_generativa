import google.generativeai as genai

class EggModelGen:

    def __init__(self, temperature = 1, top_p = 0.95, top_k = 64, max_output_tokens = 8192, response_mime_type="text/plain"):
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.max_output_tokens = max_output_tokens
        self.response_mime_type = response_mime_type

    def create_model(self, initial_instruction = '', model_type="gemini-1.5-flash", ):
        self.model = genai.GenerativeModel(
            model_name=model_type,
            generation_config= {
                "temperature": self.temperature,
                "top_p": self.top_p,
                "top_k": self.top_k,
                "max_output_tokens": self.max_output_tokens,
                "response_mime_type": self.response_mime_type,
            },
            system_instruction=initial_instruction,
        )
