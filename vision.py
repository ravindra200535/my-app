import google.generativeai as genai
import json
import PIL.Image
import os

class VisionProcessor:
    """
    Vision Engine for 'The Big Game'.
    Uses Gemini 1.5 Flash to extract structured data from bill photos.
    """
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def extract_bill_data(self, image_path):
        """
        Sends image to Gemini and returns a cleaned list of items.
        """
        img = PIL.Image.open(image_path)
        
        prompt = """
        Analyze this bill/invoice image. Extract the list of products purchased.
        Return ONLY a JSON array of objects with these exact keys:
        "Product Name", "Quantity", "Unit Price", "Total"
        
        If the image is blurry or items are unreadable, return an empty list [].
        Ensure the quantity is a number. Handle handwritten notes if present.
        
        Output format example:
        [
            {"Product Name": "Sugar", "Quantity": 10, "Unit Price": 40.0, "Total": 400.0},
            {"Product Name": "Cooking Oil", "Quantity": 5, "Unit Price": 150.0, "Total": 750.0}
        ]
        """

        try:
            response = self.model.generate_content([prompt, img])
            # Extract JSON from response (handling potential markdown blocks)
            raw_text = response.text.strip()
            if "```json" in raw_text:
                raw_text = raw_text.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_text:
                raw_text = raw_text.split("```")[1].split("```")[0].strip()
            
            data = json.loads(raw_text)
            return data
        except Exception as e:
            print(f"Vision Error: {e}")
            return []

if __name__ == "__main__":
    # Placeholder for manual testing
    # processor = VisionProcessor(api_key="YOUR_KEY")
    # print(processor.extract_bill_data("bill.jpg"))
    pass
