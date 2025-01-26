# detection/views.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from PIL import Image
import numpy as np
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import traceback
from tensorflow.keras.models import load_model
import os; 
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'

# Load the ResNet50V model
# model = load_model("currency_detection\models\MobileNet_model.h5")
model = load_model("currency_detection\models\ResNet50V2_model.h5", compile=False)

class CurrencyDetectionAPIView(APIView):
    # Handling GET request
    def __init__(self):
        self.th = 0.5

    def get(self, request):
        return Response({"status": "Failure", "message": "Get Method Not Allowed"}, status=400)
    
    def post(self, request):
        try:
            img = Image.open(request.FILES['image'])
            img = img.resize((224, 224))  # Resizing for ResNet50 input
            img_array = np.array(img).reshape((1, 224, 224, 3)) / 255.0
            predictions = model.predict(img_array)
            predicted_class = np.argmax(predictions)
            confidence_score = predictions[0][predicted_class]

            print("confidence_score:",confidence_score)
            print("predicted_class:",predicted_class)
            
            # Map predictions to your currency class labels
            class_labels = ['1000Rs', '1000Rsback', '100Rs', '100Rsback', '10Rs', '10Rsback', '20Rs', '20Rsback', 
                            '5000Rs', '5000Rsback', '500Rs', '500Rsback', '50Rs', '50Rsback']
            
            # Check if the confidence score is greater than 70%
            if confidence_score > self.th and 0 <= predicted_class < len(class_labels):
                currency_label = class_labels[predicted_class]
            else:
                currency_label = 'Not a valid currency note'

            return JsonResponse({'status': 'Success', 'message': f'Detected Currency: {currency_label}'})
        except Exception as e:
            traceback.print_exc()
            return Response({"status": "Failure", "message": str(e)}, status=400)