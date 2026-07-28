import cv2

from app.services.ocr.image_preprocessor import ImagePreprocessor

IMAGE = "test_data/BL Facture.jpeg"      # <-- ton image
SORTIE = "test_data/facture_clean.jpg"

preprocessor = ImagePreprocessor()

image = preprocessor.preprocess(IMAGE)

cv2.imwrite(SORTIE, image)

print("Prétraitement terminé.")

cv2.imshow("Image", image)
cv2.waitKey(0)
cv2.destroyAllWindows()