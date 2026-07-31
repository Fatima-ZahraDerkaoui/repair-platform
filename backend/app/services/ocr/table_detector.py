import cv2
import numpy as np


class TableDetector:

    def __init__(self):
        pass

    def detect_table(self, image):

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Binarisation
        binary = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            31,
            15,
        )

        # Lignes horizontales
        horizontal_kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT,
            (80, 1),
        )

        horizontal = cv2.morphologyEx(
            binary,
            cv2.MORPH_OPEN,
            horizontal_kernel,
            iterations=2,
        )

        # Lignes verticales
        vertical_kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT,
            (1, 80),
        )

        vertical = cv2.morphologyEx(
            binary,
            cv2.MORPH_OPEN,
            vertical_kernel,
            iterations=2,
        )

        # Fusion
        table_mask = cv2.add(horizontal, vertical)

        contours, _ = cv2.findContours(
            table_mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )

        if len(contours) == 0:
            return image

        biggest = max(contours, key=cv2.contourArea)

        x, y, w, h = cv2.boundingRect(biggest)

        margin = 20

        x = max(0, x - margin)
        y = max(0, y - margin)

        w = min(image.shape[1] - x, w + margin * 2)
        h = min(image.shape[0] - y, h + margin * 2)

        crop = image[y:y+h, x:x+w]

        return crop


    def draw_table(self, image):

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        binary = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            31,
            15,
        )

        horizontal_kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT,
            (80, 1),
        )

        vertical_kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT,
            (1, 80),
        )

        horizontal = cv2.morphologyEx(
            binary,
            cv2.MORPH_OPEN,
            horizontal_kernel,
            iterations=2,
        )

        vertical = cv2.morphologyEx(
            binary,
            cv2.MORPH_OPEN,
            vertical_kernel,
            iterations=2,
        )

        mask = cv2.add(horizontal, vertical)

        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )

        output = image.copy()

        if contours:

            biggest = max(contours, key=cv2.contourArea)

            x, y, w, h = cv2.boundingRect(biggest)

            cv2.rectangle(
                output,
                (x, y),
                (x+w, y+h),
                (0, 255, 0),
                3,
            )

        return output