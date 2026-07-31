import cv2
import numpy as np


class GeometryProcessor:

    """
    Détection robuste d'un document A4.

    Pipeline :

        Image
            ↓
        Gray
            ↓
        CLAHE
            ↓
        Gaussian Blur
            ↓
        Bilateral Filter
            ↓
        Canny
            ↓
        Morph Close
            ↓
        Dilatation
            ↓
        Recherche des contours
            ↓
        Sélection des meilleurs candidats
    """

    def __init__(self):

        self.min_document_area = 0.20
        self.max_document_area = 0.98

    ####################################################################
    # Détection complète
    ####################################################################

    def detecter_document(self, image):

        edges = self.detecter_bords(image)

        contours = self.rechercher_contours(edges)

        if len(contours) == 0:
            return None

        candidats = []

        hauteur, largeur = image.shape[:2]
        aire_image = largeur * hauteur

        for contour in contours:

            aire = cv2.contourArea(contour)

            if aire < aire_image * self.min_document_area:
                continue

            if aire > aire_image * self.max_document_area:
                continue

            perimetre = cv2.arcLength(contour, True)

            approx = cv2.approxPolyDP(
                contour,
                0.02 * perimetre,
                True
            )

            if len(approx) != 4:
                continue

            if not cv2.isContourConvex(approx):
                continue

            candidats.append(approx.reshape(4, 2))

        if len(candidats) == 0:
            return None

        meilleur = None
        meilleur_score = -1

        for contour in candidats:

            score = self.evaluer_contour(
                contour,
                image
            )

            if score > meilleur_score:

                meilleur_score = score

                meilleur = contour

        return meilleur

    ####################################################################
    # Détection des bords
    ####################################################################

    def detecter_bords(self, image):

        gris = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        clahe = cv2.createCLAHE(
            clipLimit=2.5,
            tileGridSize=(8, 8)
        )

        gris = clahe.apply(gris)

        gris = cv2.GaussianBlur(
            gris,
            (5, 5),
            0
        )

        gris = cv2.bilateralFilter(
            gris,
            9,
            75,
            75
        )

        edges = cv2.Canny(
            gris,
            50,
            150
        )

        kernel = np.ones(
            (5, 5),
            np.uint8
        )

        edges = cv2.morphologyEx(
            edges,
            cv2.MORPH_CLOSE,
            kernel,
            iterations=2
        )

        edges = cv2.dilate(
            edges,
            kernel,
            iterations=1
        )

        return edges

    ####################################################################
    # Recherche des contours
    ####################################################################

    def rechercher_contours(self, edges):

        contours, _ = cv2.findContours(
            edges,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        contours = sorted(
            contours,
            key=cv2.contourArea,
            reverse=True
        )

        return contours

    ####################################################################
    # Tri des points
    ####################################################################

    def trier_points(self, points):

        points = np.array(
            points,
            dtype="float32"
        )

        resultat = np.zeros(
            (4, 2),
            dtype="float32"
        )

        somme = points.sum(axis=1)

        resultat[0] = points[np.argmin(somme)]
        resultat[2] = points[np.argmax(somme)]

        difference = np.diff(points, axis=1)

        resultat[1] = points[np.argmin(difference)]
        resultat[3] = points[np.argmax(difference)]

        return resultat

    ####################################################################
    # Angles proches de 90°
    ####################################################################

    def score_angles(self, contour):

        pts = self.trier_points(contour)

        score = 0

        for i in range(4):

            p1 = pts[i]

            p2 = pts[(i + 1) % 4]

            p3 = pts[(i + 2) % 4]

            v1 = p1 - p2

            v2 = p3 - p2

            angle = self.angle(v1, v2)

            erreur = abs(angle - 90)

            if erreur < 20:

                score += 5

        return score


    ####################################################################
    # Calcul angle
    ####################################################################

    def angle(self, v1, v2):

        produit = np.dot(v1, v2)

        norme = np.linalg.norm(v1) * np.linalg.norm(v2)

        if norme == 0:

            return 0

        cos = produit / norme

        cos = np.clip(cos, -1, 1)

        return np.degrees(np.arccos(cos))

    ####################################################################
    # Perspective Transform
    ####################################################################

    def corriger_perspective(
        self,
        image,
        points
    ):

        points = self.trier_points(points)

        (tl, tr, br, bl) = points

        largeurA = np.linalg.norm(br - bl)

        largeurB = np.linalg.norm(tr - tl)

        largeur = int(max(
            largeurA,
            largeurB
        ))

        hauteurA = np.linalg.norm(tr - br)

        hauteurB = np.linalg.norm(tl - bl)

        hauteur = int(max(
            hauteurA,
            hauteurB
        ))

        destination = np.array([

            [0, 0],

            [largeur - 1, 0],

            [largeur - 1, hauteur - 1],

            [0, hauteur - 1]

        ], dtype="float32")

        matrice = cv2.getPerspectiveTransform(
            points,
            destination
        )

        return cv2.warpPerspective(
            image,
            matrice,
            (largeur, hauteur)
        )

    ####################################################################
    # Debug
    ####################################################################

    def debug_contours(
        self,
        image,
        contours
    ):

        copie = image.copy()

        cv2.drawContours(
            copie,
            contours,
            -1,
            (0,255,0),
            3
        )

        cv2.imwrite(
            "debug_contours.jpg",
            copie
        )