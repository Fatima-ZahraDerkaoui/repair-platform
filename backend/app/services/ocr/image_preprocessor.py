import cv2
import numpy as np


class ImagePreprocessor:

    def preprocess(self, chemin_image, debug=False):

        image = self._charger_image(chemin_image)

        image = self._corriger_rotation_90(image)

        image = self._redimensionner(image)

        image = self._ameliorer_contraste(image)

        image = self._supprimer_bruit(image)

        image = self._accentuer(image)

        if debug:
            cv2.imwrite("debug_preprocess.jpg", image)

        return image

    ####################################################################
    # Chargement
    ####################################################################

    def _charger_image(self, chemin):

        image = cv2.imread(chemin)

        if image is None:
            raise Exception("Impossible de lire l'image.")

        return image

    ####################################################################
    # Rotation 90°
    ####################################################################

    def _corriger_rotation_90(self, image):

        h, w = image.shape[:2]

        if h > w:
            image = cv2.rotate(
                image,
                cv2.ROTATE_90_CLOCKWISE
            )

        return image

    ####################################################################
    # Resize
    ####################################################################

    def _redimensionner(self, image):

        largeur = 1800

        ratio = largeur / image.shape[1]

        hauteur = int(image.shape[0] * ratio)

        return cv2.resize(
            image,
            (largeur, hauteur),
            interpolation=cv2.INTER_CUBIC
        )

    ####################################################################
    # Contraste
    ####################################################################

    def _ameliorer_contraste(self, image):

        lab = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2LAB
        )

        l, a, b = cv2.split(lab)

        clahe = cv2.createCLAHE(
            clipLimit=2.0,
            tileGridSize=(8, 8)
        )

        l = clahe.apply(l)

        lab = cv2.merge((l, a, b))

        return cv2.cvtColor(
            lab,
            cv2.COLOR_LAB2BGR
        )

    ####################################################################
    # Bruit
    ####################################################################

    def _supprimer_bruit(self, image):

        return cv2.fastNlMeansDenoisingColored(
            image,
            None,
            10,
            10,
            7,
            21
        )

    ####################################################################
    # Netteté
    ####################################################################

    def _accentuer(self, image):

        kernel = np.array([
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0]
        ])

        return cv2.filter2D(
            image,
            -1,
            kernel
        )

    def sauvegarder(self, image, chemin_sortie):
        cv2.imwrite(chemin_sortie, image)