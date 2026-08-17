from pathlib import Path

import cv2
import numpy as np


class ImagePreprocessor:

    # ==========================================================
    # LOAD
    # ==========================================================

    def load(self, image_path):

        image_path = Path(
            image_path
        )

        if not image_path.exists():

            raise FileNotFoundError(
                f"Image introuvable : {image_path}"
            )

        image_path = str(
            image_path.resolve()
        )

        image = cv2.imread(
            image_path
        )

        if image is None:

            raise ValueError(
                f"OpenCV ne peut pas lire l'image : "
                f"{image_path}"
            )

        return image

    # ==========================================================
    # ROTATION
    # ==========================================================

    def rotate_if_needed(self, image):

        h, w = image.shape[:2]

        if h < w:

            image = cv2.rotate(
                image,
                cv2.ROTATE_90_COUNTERCLOCKWISE
            )

        return image

    # ==========================================================
    # DOCUMENT DETECTION
    # ==========================================================

    def detect_document(self, image):

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        blur = cv2.GaussianBlur(
            gray,
            (5, 5),
            0
        )

        edges = cv2.Canny(
            blur,
            50,
            150
        )

        kernel = np.ones(
            (5, 5),
            np.uint8
        )

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

        contours, _ = cv2.findContours(
            edges,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        if not contours:

            return self.crop_content(
                image
            )

        contours = sorted(
            contours,
            key=cv2.contourArea,
            reverse=True
        )

        image_area = (
            image.shape[0] *
            image.shape[1]
        )

        for contour in contours:

            area = cv2.contourArea(
                contour
            )

            if area < image_area * 0.20:
                continue

            peri = cv2.arcLength(
                contour,
                True
            )

            approx = cv2.approxPolyDP(
                contour,
                0.02 * peri,
                True
            )

            if len(approx) == 4:

                points = approx.reshape(
                    4,
                    2
                )

                return self.four_point_transform(
                    image,
                    points
                )

        return self.crop_content(
            image
        )

    # ==========================================================
    # ORDER POINTS
    # ==========================================================

    def order_points(self, pts):

        rect = np.zeros(
            (4, 2),
            dtype="float32"
        )

        s = pts.sum(
            axis=1
        )

        rect[0] = pts[
            np.argmin(s)
        ]

        rect[2] = pts[
            np.argmax(s)
        ]

        diff = np.diff(
            pts,
            axis=1
        )

        rect[1] = pts[
            np.argmin(diff)
        ]

        rect[3] = pts[
            np.argmax(diff)
        ]

        return rect

    # ==========================================================
    # PERSPECTIVE TRANSFORM
    # ==========================================================

    def four_point_transform(
        self,
        image,
        pts
    ):

        rect = self.order_points(
            pts
        )

        tl, tr, br, bl = rect

        width_a = np.linalg.norm(
            br - bl
        )

        width_b = np.linalg.norm(
            tr - tl
        )

        max_width = max(
            int(width_a),
            int(width_b)
        )

        height_a = np.linalg.norm(
            tr - br
        )

        height_b = np.linalg.norm(
            tl - bl
        )

        max_height = max(
            int(height_a),
            int(height_b)
        )

        dst = np.array(
            [
                [0, 0],
                [max_width - 1, 0],
                [max_width - 1, max_height - 1],
                [0, max_height - 1]
            ],
            dtype="float32"
        )

        matrix = cv2.getPerspectiveTransform(
            rect,
            dst
        )

        return cv2.warpPerspective(
            image,
            matrix,
            (
                max_width,
                max_height
            )
        )

    # ==========================================================
    # RESIZE
    # ==========================================================

    def resize(self, image):

        height, width = image.shape[:2]

        target_height = 1800

        if height < target_height:

            ratio = (
                target_height /
                height
            )

            image = cv2.resize(
                image,
                (
                    int(width * ratio),
                    target_height
                ),
                interpolation=cv2.INTER_CUBIC
            )

        return image

    # ==========================================================
    # CLAHE
    # ==========================================================

    def clahe(self, image):

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        clahe = cv2.createCLAHE(
            clipLimit=2.5,
            tileGridSize=(8, 8)
        )

        return clahe.apply(
            gray
        )

    # ==========================================================
    # DENOISE
    # ==========================================================

    def denoise(self, image):

        return cv2.fastNlMeansDenoising(
            image,
            None,
            12,
            7,
            21
        )

    # ==========================================================
    # SHARPEN
    # ==========================================================

    def sharpen(self, image):

        kernel = np.array(
            [
                [-1, -1, -1],
                [-1, 9, -1],
                [-1, -1, -1]
            ]
        )

        return cv2.filter2D(
            image,
            -1,
            kernel
        )

    # ==========================================================
    # PREPROCESS
    # ==========================================================

    def preprocess(
        self,
        image_path
    ):

        image = self.load(
            image_path
        )

        image = self.rotate_if_needed(
            image
        )

        image = self.detect_document(
            image
        )

        image = self.resize(
            image
        )

        image = self.clahe(
            image
        )

        image = self.denoise(
            image
        )

        image = self.sharpen(
            image
        )

        return image

    # ==========================================================
    # CROP CONTENT
    # ==========================================================

    def crop_content(self, image):

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        _, thresh = cv2.threshold(
            gray,
            245,
            255,
            cv2.THRESH_BINARY_INV
        )

        kernel = np.ones(
            (7, 7),
            np.uint8
        )

        thresh = cv2.morphologyEx(
            thresh,
            cv2.MORPH_CLOSE,
            kernel
        )

        coords = cv2.findNonZero(
            thresh
        )

        if coords is None:

            return image

        x, y, w, h = cv2.boundingRect(
            coords
        )

        margin = 20

        x = max(
            0,
            x - margin
        )

        y = max(
            0,
            y - margin
        )

        w = min(
            image.shape[1] - x,
            w + margin * 2
        )

        h = min(
            image.shape[0] - y,
            h + margin * 2
        )

        return image[
            y:y + h,
            x:x + w
        ]