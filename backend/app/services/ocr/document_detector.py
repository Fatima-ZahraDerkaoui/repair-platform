import cv2
import numpy as np


class DocumentDetector:
    """
    Détection robuste d'un document A4.

    Fonctionnement :

        1. Resize rapide
        2. Gray
        3. Blur
        4. Canny
        5. Dilatation
        6. Recherche du plus grand contour
        7. Approximation en quadrilatère
    """

    def __init__(self):

        self.resize_width = 1200

    ####################################################################
    # PUBLIC
    ####################################################################

    def detect(self, image):

        original = image.copy()

        ratio = image.shape[1] / self.resize_width

        resized = self._resize(image)

        gray = cv2.cvtColor(
            resized,
            cv2.COLOR_BGR2GRAY
        )

        gray = cv2.GaussianBlur(
            gray,
            (5, 5),
            0
        )

        edges = cv2.Canny(
            gray,
            40,
            150
        )

        kernel = np.ones((5, 5), np.uint8)

        edges = cv2.dilate(
            edges,
            kernel,
            iterations=2
        )

        edges = cv2.erode(
            edges,
            kernel,
            iterations=1
        )

        contour = self._largest_contour(edges)

        if contour is None:
            return None

        peri = cv2.arcLength(
            contour,
            True
        )

        approx = cv2.approxPolyDP(
            contour,
            0.02 * peri,
            True
        )

        if len(approx) != 4:

            rect = cv2.minAreaRect(contour)

            approx = cv2.boxPoints(rect)

        approx = approx.reshape(4, 2)

        approx = approx.astype(np.float32)

        approx *= ratio

        return approx

    ####################################################################
    # Resize
    ####################################################################

    def _resize(self, image):

        h, w = image.shape[:2]

        ratio = self.resize_width / w

        return cv2.resize(
            image,
            (
                self.resize_width,
                int(h * ratio)
            ),
            interpolation=cv2.INTER_AREA
        )

    ####################################################################
    # Largest contour
    ####################################################################

    def _largest_contour(self, edges):

        contours, _ = cv2.findContours(
            edges,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        if len(contours) == 0:
            return None

        contours = sorted(
            contours,
            key=cv2.contourArea,
            reverse=True
        )

        image_area = edges.shape[0] * edges.shape[1]

        for c in contours:

            area = cv2.contourArea(c)

            if area < image_area * 0.20:
                continue

            return c

        return None

    ####################################################################
    # DEBUG
    ####################################################################

    def draw(self, image, points):

        img = image.copy()

        if points is None:
            return img

        pts = points.astype(int)

        cv2.polylines(
            img,
            [pts],
            True,
            (0, 255, 0),
            5
        )

        for p in pts:

            cv2.circle(
                img,
                tuple(p),
                12,
                (0, 0, 255),
                -1
            )

        return img