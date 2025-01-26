from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import traceback
from django.views.decorators.csrf import csrf_exempt

import numpy as np
import torch
import gradio as gr
from urdu_ocr.read import text_recognizer
from urdu_ocr.model import Model
from urdu_ocr.utils import CTCLabelConverter
from ultralytics import YOLO
from PIL import Image, ImageDraw, UnidentifiedImageError
from io import BytesIO
import base64


# Load OCR Models (Move model loading outside of the view for efficiency)
try:
    """ vocab / character number configuration """
    file = open("urdu_ocr/UrduGlyphs.txt","r",encoding="utf-8")
    content = file.readlines()
    content = ''.join([str(elem).strip('\n') for elem in content])
    content = content+" "
    """ model configuration """
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    converter = CTCLabelConverter(content)
    recognition_model = Model(num_class=len(converter.character), device=device)
    recognition_model = recognition_model.to(device)
    recognition_model.load_state_dict(torch.load("urdu_ocr/best_norm_ED.pth", map_location=device))
    recognition_model.eval()
    detection_model = YOLO("urdu_ocr/yolov8m_UrduDoc.pt")
except Exception as e:
    print(f"Error during model initialization: {e}")
    detection_model = None
    recognition_model = None

# Create your views here.


class UrduOCRAPIView(APIView):
    # Handling GET request
    def __init__(self):
        pass

    def get(self, request):
        return Response({"status": "Failure", "message": "Get Method Not Allowed"}, status=400)
    
    def post(self, request):
        # Ensure Models are Loaded
        if not detection_model or not recognition_model:
            return JsonResponse({"error": "Model initialization failed. Please check the setup."}, status=500)
        try:
            if 'image' not in request.FILES:
                return JsonResponse({"error": "No image file found in the request. Please upload an image."}, status=400)
            # Parse Image Input
            image_data = request.FILES['image']
            if not image_data.content_type.startswith("image/"):
                return JsonResponse({"error": "Invalid file type. Please upload an image."}, status=400)
            # Load the Image
            try:
                image = Image.open(image_data).convert("RGB")
            except UnidentifiedImageError:
                return JsonResponse({"error": "Uploaded file is not a valid image."}, status=400)

            
            # Line Detection
            detection_results = detection_model.predict(
                source=image, conf=0.2, imgsz=1280, save=False, nms=True, device=device)
            bounding_boxes = detection_results[0].boxes.xyxy.cpu().numpy().tolist()
            if not bounding_boxes:
                return JsonResponse({"error": "No text regions detected in the image."}, status=200)
            
            bounding_boxes.sort(key=lambda x: x[1])  # Sort boxes by Y-axis
            
            # Draw Bounding Boxes
            draw = ImageDraw.Draw(image)
            for box in bounding_boxes:
                color = tuple(np.random.randint(0, 255, 3))
                draw.rectangle(box, outline=color, width=5)
            
            # Crop Detected Lines and Recognize Text
            cropped_images = [image.crop(box) for box in bounding_boxes]
            texts = [text_recognizer(img, recognition_model, converter, device) for img in cropped_images]
            recognized_text = "\n".join(texts)

            print("recognized_text:", recognized_text)
            
            # Encode Image with Bounding Boxes
            buffered = BytesIO()
            image.save(buffered, format="JPEG")
            encoded_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            # Return JSON Response
            return JsonResponse({
                "recognized_text": recognized_text,
                "detected_image": f"data:image/jpeg;base64,{encoded_image}"
            })
        except Exception as e:
            traceback.print_exc()
            return Response({"status": "Failure", "message": str(e)}, status=400)