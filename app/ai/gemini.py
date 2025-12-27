import google.generativeai as genai
from app.config import settings
import json
from typing import Optional

# Configure Gemini API
genai.configure(api_key=settings.GOOGLE_API_KEY)

# Initialize the model (using gemini-2.5-flash - latest fast model)
model = genai.GenerativeModel('gemini-2.5-flash')


class GeminiClient:
    """Google Gemini AI client"""
    
    @staticmethod
    def analyze_message(message: str, sender_username: str, receiver_username: str) -> dict:
        """
        Analyze a message to determine if it's a task, expense, payment, or normal message
        
        Args:
            message: The message content to analyze.
            sender_username: The username of the sender.
            receiver_username: The username of the receiver.
        
        Returns:
            dict: A dictionary containing the analysis result (type, item, amount, confidence).
        """
        prompt = f"""
        Analyze the user message and categorize it into one of the following types:
        1. TASK: Something that needs to be acquired or done (future tense, implies an action).
        2. EXPENSE: Something was acquired or done, and a cost is mentioned (past tense, implies a transaction).
        3. PAYMENT: A debt payment was made (mentions paying/giving money back, settling debt).
        4. NORMAL: A regular conversational message.

        Consider the context of a two-person household or shared expense scenario.
        
        Sender: {sender_username}
        Receiver: {receiver_username}
        Message: "{message}"

        Return the analysis in JSON format. Ensure the JSON is valid and contains only the specified fields.
        
        Example for TASK:
        Message: "mop alınacak"
        Output: {{"type": "task", "item": "mop", "amount": null, "confidence": 0.95}}
        
        Example for EXPENSE:
        Message: "mop aldım 300tl"
        Output: {{"type": "expense", "item": "mop", "amount": 300, "confidence": 0.98}}
        
        Example for PAYMENT:
        Message: "200 TL ödedim"
        Output: {{"type": "payment", "item": null, "amount": 200, "confidence": 0.95}}
        
        Example for PAYMENT (full debt):
        Message: "borcumu kapattım"
        Output: {{"type": "payment", "item": null, "amount": null, "confidence": 0.90}}
        
        Example for NORMAL:
        Message: "Merhaba nasılsın?"
        Output: {{"type": "normal", "item": null, "amount": null, "confidence": 1.0}}
        
        If an item or amount cannot be clearly extracted for TASK, EXPENSE, or PAYMENT, set them to null.
        For PAYMENT type, if no amount is specified, set amount to null (means pay all debts).
        Confidence should be a float between 0 and 1.
        """
        
        print(f"[GEMINI] Sending to API: {message}")
        
        try:
            response = model.generate_content(prompt)
            # Assuming the response is directly parsable JSON
            analysis_text = response.text.strip()
            print(f"[GEMINI] API response: {analysis_text}")
            
            # Attempt to parse JSON, handle potential markdown formatting
            if analysis_text.startswith("```json"):
                analysis_text = analysis_text[7:]
            if analysis_text.endswith("```"):
                analysis_text = analysis_text[:-3]
            
            analysis = json.loads(analysis_text)
            print(f"[GEMINI] Successfully parsed analysis: {analysis}")
            return analysis
        except Exception as e:
            print(f"[GEMINI ERROR] Exception: {e}")
            print(f"[GEMINI ERROR] Falling back to normal")
            import traceback
            traceback.print_exc()
            # Fallback for API errors or invalid JSON
            return {"type": "normal", "item": None, "amount": None, "confidence": 0.0}
