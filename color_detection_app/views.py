from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import traceback, cv2, io
import numpy as np
import pandas as pd
from PIL import Image

class ColorDetectionAPIView(APIView):
    # Handling GET request
    def get(self, request):
        return Response({"status": "Failure", "message": "Get Method Not Allowed"}, status=400)
    
    def post(self, request):
        try:
            # Getting the image file from the request
            image_file = request.FILES.get('image')
            if not image_file:
                return Response({"status": "Failure", "message": "No image provided"}, status=400)

            # Getting the coordinates from the request
            xpos = int(request.data.get('xpos'))
            ypos = int(request.data.get('ypos'))

            print(f"xpos : {xpos}\n ypos : {ypos}")

            # Reading the image from the file
            image_stream = io.BytesIO(image_file.read())
            image = Image.open(image_stream)
            img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            # Reading the CSV for color reference
            csv = pd.read_csv('color_detection_app/colors.csv', names=["color", "color_name", "hex", "R", "G", "B"], header=None)

            # Getting the color at the provided coordinates
            b, g, r = img[ypos, xpos]
            color_name = self.getColorName(r, g, b, csv)

            return Response({"status": "Success", "message": f"Detected Color: {color_name}"}, status=200)
        
        except Exception as e:
            traceback.print_exc()
            return Response({"status": "Failure", "message": str(e)}, status=400)
        

    def getColorName(self, R, G, B, csv):
        minimum = 10000
        cname = "Unknown"
        for i in range(len(csv)):
            d = abs(R - int(csv.loc[i, "R"])) + abs(G - int(csv.loc[i, "G"])) + abs(B - int(csv.loc[i, "B"]))
            if d <= minimum:
                minimum = d
                cname = csv.loc[i, "color_name"]
        return cname
