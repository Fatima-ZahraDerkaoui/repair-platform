import cv2

from app.services.ocr.geometry import GeometryProcessor

image = cv2.imread("test_data/BL Facture.jpeg")

geometry = GeometryProcessor()

points = geometry.detecter_document(image)

if points is None:
    print("Document non détecté")

else:

    image = geometry.corriger_perspective(
        image,
        points
    )

    cv2.imwrite(
        "test_data/facture_corrigee.jpg",
        image
    )

    print("Document corrigé.")