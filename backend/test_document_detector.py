import cv2

from app.services.ocr.document_detector import DocumentDetector

image = cv2.imread("test_data/BL Facture.jpeg")

detector = DocumentDetector()

points = detector.detect(image)

result = detector.draw(image, points)

cv2.imwrite("document_detected.jpg", result)

print(points)