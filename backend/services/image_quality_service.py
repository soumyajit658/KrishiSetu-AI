from io import BytesIO
from PIL import Image, ImageStat
from typing import Dict, Any, List

def check_image_quality(image_bytes: bytes) -> Dict[str, Any]:
    """
    Validate image quality before diagnosis:
    - Checks resolution
    - Checks brightness (underexposure / overexposure)
    - Checks sharpness / contrast
    - Checks presence of botanical / agricultural tones
    """
    try:
        img = Image.open(BytesIO(image_bytes))
        width, height = img.size

        # 1. Resolution Check
        if width < 120 or height < 120:
            return {
                "passed": False,
                "score": 30,
                "issues": ["Image resolution is too low for microscopic/lesion detection."],
                "guidance": [
                    "Take photo at a higher resolution (at least 600x600 pixels).",
                    "Avoid taking screenshots of small thumbnail images."
                ]
            }

        img_rgb = img.convert("RGB")
        stat = ImageStat.Stat(img_rgb)
        r, g, b = stat.mean

        # 2. Brightness Check
        avg_brightness = (r + g + b) / 3.0
        issues = []
        guidance = []

        if avg_brightness < 35:
            issues.append("Image is too dark (underexposed).")
            guidance.append("Take the photograph in clear, indirect natural daylight.")
            guidance.append("Avoid casting shadows from your body or phone onto the leaf.")

        if avg_brightness > 235:
            issues.append("Image is washed out / too bright (overexposed glare).")
            guidance.append("Avoid direct harsh sun reflection or flash glare on wet leaves.")

        # 3. Contrast / Sharpness Check
        stddev = stat.stddev
        avg_contrast = sum(stddev) / len(stddev)
        if avg_contrast < 14:
            issues.append("Image appears blurry or lacks textural contrast.")
            guidance.append("Tap your screen to focus sharply on the leaf lesions or stem.")
            guidance.append("Hold the phone steady or support your arm while capturing.")

        # 4. Botanical Color Heuristic
        # Sample resized thumbnail
        sample = img_rgb.resize((50, 50))
        pixels = list(sample.getdata())
        plant_tones = sum(
            1 for pr, pg, pb in pixels
            # Green foliage OR brown/yellow chlorotic/soil/stem tones
            if (pg > pr and pg > pb and pg > 45) or 
               (pr > 75 and pg > 50 and pb < 70) or 
               (pr > 90 and pg > 40 and pb < 55)
        )
        ratio = plant_tones / len(pixels)
        if ratio < 0.15:
            issues.append("Leaf or agricultural subject is not clearly visible.")
            guidance.append("Ensure the crop leaf, plant, or field fills at least 50% of the camera frame.")
            guidance.append("Remove foreign non-agricultural objects from the background.")

        passed = len(issues) == 0
        score = max(20, min(100, int(100 - (len(issues) * 25))))

        if not passed:
            guidance.extend([
                "Photograph both the top and underside of the affected leaf.",
                "Capture both a close-up of the symptom and a whole-plant photo."
            ])

        return {
            "passed": passed,
            "score": score,
            "issues": issues,
            "guidance": list(dict.fromkeys(guidance))  # deduplicate
        }

    except Exception as e:
        return {
            "passed": False,
            "score": 20,
            "issues": [f"Could not decode image format: {str(e)}"],
            "guidance": ["Upload a standard JPG, PNG, or WebP photo."]
        }
