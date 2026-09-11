import json
import re

import torch
from PIL import Image
from transformers import AutoModelForImageTextToText, AutoProcessor

MODEL_NAME = "HuggingFaceTB/SmolVLM-256M-Instruct"

PROMPT = """You are an AI assistant for KalaConnect, a platform for Indian artisans.
Analyze the uploaded craft or artisan product image.

Identify only information that can reasonably be inferred from the visual characteristics of the image.
Do not invent or hallucinate exact facts such as the artisan's identity, exact location, exact age, exact price, authenticity, or unidentifiable material composition.

Return ONLY valid JSON using exactly this structure:
{
    "craft": "",
    "material": "",
    "product_type": "",
    "visual_description": "",
    "colors": [],
    "design_features": [],
    "craftsmanship_features": [],
    "possible_region": "",
    "confidence": 0.0
}

Rules:
- craft: likely craft category (e.g. pottery, weaving, embroidery, wood carving, metal craft, basketry, painting, jewelry, leather craft, etc.) or "unknown".
- material: visually identifiable or likely material (e.g. terracotta clay, silk, brass, teak wood, cotton, etc.) or "unknown".
- product_type: what the object appears to be (e.g. vase, saree, wall hanging, sculpture, tea set, etc.) or "unknown".
- visual_description: concise visual summary suitable for an artisan product catalogue.
- colors: list of main visible colors.
- design_features: list of visible motifs, patterns, shapes, or decorative elements.
- craftsmanship_features: list of visible handmade/artisan characteristics.
- possible_region: geographic or regional association only if visually justified (e.g. Jaipur, Bengal, Kashmir, Kutch, Bastar, etc.); otherwise use "unknown".
- confidence: a float number between 0.0 and 1.0 representing your confidence.
"""


class VisionModel:
    def __init__(self):
        print("Loading Vision model (SmolVLM-256M-Instruct)...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")

        self.processor = AutoProcessor.from_pretrained(MODEL_NAME)
        self.model = AutoModelForImageTextToText.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.bfloat16 if self.device == "cuda" else torch.float32,
        ).to(self.device)
        self.model.eval()

        print("Vision model loaded successfully.")

    def analyze_image(self, image_path: str) -> dict:
        image = Image.open(image_path).convert("RGB")

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image"},
                    {"type": "text", "text": PROMPT}
                ]
            }
        ]

        prompt_text = self.processor.apply_chat_template(
            messages,
            add_generation_prompt=True
        )

        inputs = self.processor(
            text=prompt_text,
            images=[image],
            return_tensors="pt"
        )
        inputs = inputs.to(self.device)

        with torch.inference_mode():
            generated_ids = self.model.generate(
                **inputs,
                max_new_tokens=350,
            )

        generated_ids_trimmed = [
            out_ids[len(in_ids):]
            for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]

        output_text = self.processor.batch_decode(
            generated_ids_trimmed,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False
        )[0]

        return self._parse_json(output_text)

    def _parse_json(self, text: str) -> dict:
        text = text.strip()

        # Remove markdown code fences if present
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)

        parsed = None
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                try:
                    parsed = json.loads(match.group())
                except json.JSONDecodeError:
                    pass

        if isinstance(parsed, dict):
            return self._normalize_analysis(parsed)

        return self._normalize_analysis({
            "craft": "unknown",
            "material": "unknown",
            "product_type": "unknown",
            "visual_description": text,
            "colors": [],
            "design_features": [],
            "craftsmanship_features": [],
            "possible_region": "unknown",
            "confidence": 0.0
        })

    @staticmethod
    def _normalize_analysis(data: dict) -> dict:
        craft = str(data.get("craft") or "unknown").strip()
        material = str(data.get("material") or "unknown").strip()
        product_type = str(data.get("product_type") or "unknown").strip()
        visual_description = str(data.get("visual_description") or "").strip()

        colors = data.get("colors")
        if not isinstance(colors, list):
            colors = [str(colors)] if colors else []
        else:
            colors = [str(c).strip() for c in colors if c]

        design_features = data.get("design_features")
        if not isinstance(design_features, list):
            design_features = [str(design_features)] if design_features else []
        else:
            design_features = [str(d).strip() for d in design_features if d]

        craftsmanship_features = data.get("craftsmanship_features")
        if not isinstance(craftsmanship_features, list):
            craftsmanship_features = [str(craftsmanship_features)] if craftsmanship_features else []
        else:
            craftsmanship_features = [str(cf).strip() for cf in craftsmanship_features if cf]

        possible_region = str(data.get("possible_region") or "unknown").strip()

        try:
            confidence = float(data.get("confidence", 0.0))
            confidence = max(0.0, min(1.0, confidence))
        except (ValueError, TypeError):
            confidence = 0.0

        return {
            "craft": craft if craft else "unknown",
            "material": material if material else "unknown",
            "product_type": product_type if product_type else "unknown",
            "visual_description": visual_description,
            "colors": colors,
            "design_features": design_features,
            "craftsmanship_features": craftsmanship_features,
            "possible_region": possible_region if possible_region else "unknown",
            "confidence": confidence
        }


vision_model = None


def get_vision_model() -> VisionModel:
    global vision_model
    if vision_model is None:
        vision_model = VisionModel()
    return vision_model