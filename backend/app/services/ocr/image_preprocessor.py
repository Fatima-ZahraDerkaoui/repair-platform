import cv2
import numpy as np


class ImagePreprocessor:

    def __init__(self):
        pass

    # ---------------------------------------------------------

    def load(self, image_path: str):

        image = cv2.imread(image_path)

        if image is None:
            raise ValueError("Impossible de lire l'image.")

        return image

    # ---------------------------------------------------------

    def rotate_if_needed(self, image):

        h, w = image.shape[:2]

        # Facture scannée en portrait
        if h < w:
            image = cv2.rotate(
                image,
                cv2.ROTATE_90_COUNTERCLOCKWISE
            )

        return image

    # ---------------------------------------------------------

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

        contours, _ = cv2.findContours(
            edges,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        if not contours:
            return image

        contour = max(
            contours,
            key=cv2.contourArea
        )

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
            return image

        pts = approx.reshape(4, 2)

        return self.four_point_transform(
            image,
            pts
        )

    # ---------------------------------------------------------

    def order_points(self, pts):

        rect = np.zeros(
            (4, 2),
            dtype="float32"
        )

        s = pts.sum(axis=1)

        rect[0] = pts[np.argmin(s)]

        rect[2] = pts[np.argmax(s)]

        diff = np.diff(
            pts,
            axis=1
        )

        rect[1] = pts[np.argmin(diff)]

        rect[3] = pts[np.argmax(diff)]

        return rect

    # ---------------------------------------------------------

    def four_point_transform(
            self,
            image,
            pts
    ):

        rect = self.order_points(
            pts
        )

        (tl, tr, br, bl) = rect

        widthA = np.linalg.norm(
            br - bl
        )

        widthB = np.linalg.norm(
            tr - tl
        )

        maxWidth = max(
            int(widthA),
            int(widthB)
        )

        heightA = np.linalg.norm(
            tr - br
        )

        heightB = np.linalg.norm(
            tl - bl
        )

        maxHeight = max(
            int(heightA),
            int(heightB)
        )

        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]
        ], dtype="float32")

        M = cv2.getPerspectiveTransform(
            rect,
            dst
        )

        warped = cv2.warpPerspective(
            image,
            M,
            (
                maxWidth,
                maxHeight
            )
        )

        return warped

    # ---------------------------------------------------------

    def resize(self, image):

        h, w = image.shape[:2]

        target = 1800

        if h < target:

            ratio = target / h

            image = cv2.resize(
                image,
                (
                    int(w * ratio),
                    target
                ),
                interpolation=cv2.INTER_CUBIC
            )

        return image

    # ---------------------------------------------------------

    def clahe(self, image):

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        clahe = cv2.createCLAHE(
            clipLimit=2.5,
            tileGridSize=(8, 8)
        )

        gray = clahe.apply(gray)

        return gray

    # ---------------------------------------------------------

    def denoise(self, image):

        return cv2.fastNlMeansDenoising(
            image,
            None,
            12,
            7,
            21
        )

    # ---------------------------------------------------------

    def sharpen(self, image):

        kernel = np.array([
            [-1, -1, -1],
            [-1, 9, -1],
            [-1, -1, -1]
        ])

        return cv2.filter2D(
            image,
            -1,
            kernel
        )

    # ---------------------------------------------------------

    def preprocess(
            self,
            image_path: str
    ):

        image = self.load(image_path)

        image = self.rotate_if_needed(image)

        image = self.detect_document(image)

        image = self.resize(image)

        image = self.clahe(image)

        image = self.denoise(image)

        image = self.sharpen(image)

        return image