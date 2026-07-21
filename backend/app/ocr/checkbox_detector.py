import cv2
import numpy as np


class CheckboxDetector:

    def __init__(self):

        # Taille de référence de ta fiche
        self.reference_width = 1054
        self.reference_height = 689

        # =========================================================
        # COORDONNÉES DES CASES DE TA FICHE
        # Format : (x, y, largeur, hauteur)
        # =========================================================

        self.checkbox_config = {

            # -----------------------------------------------------
            # TYPE DE MATÉRIEL
            # -----------------------------------------------------
            "type_materiel": {

                "PC": (590, 94, 20, 20),

                "PC Portable": (823, 94, 20, 20),

                "Imprimante": (590, 130, 20, 20),

                "Unité centrale": (823, 130, 20, 20),

                "Autre": (590, 165, 20, 20)
            },

            # -----------------------------------------------------
            # SYSTÈME D'EXPLOITATION
            # -----------------------------------------------------
            "systeme_exploitation": {

                "Windows 10": (60, 245, 20, 20),

                "Windows 11": (60, 275, 20, 20),

                "Linux": (60, 300, 20, 20),

                "Autre": (60, 330, 20, 20)
            },

            # -----------------------------------------------------
            # OFFICE
            # -----------------------------------------------------
            "office": {

                "Office 2013": (430, 245, 20, 20),

                "Office 2024": (430, 280, 20, 20),

                "Microsoft 365": (430, 315, 20, 20)
            },

            # -----------------------------------------------------
            # ORIGINE DU PROBLÈME
            # -----------------------------------------------------
            "origine_probleme": {

                "Matériel": (700, 240, 20, 20),

                "Logiciel": (700, 265, 20, 20),

                "Réseau": (700, 285, 20, 20),

                "Virus": (700, 310, 20, 20),

                "Mise à jour": (700, 335, 20, 20),

                "Inconnue": (700, 355, 20, 20),

                "Autre": (700, 385, 20, 20)
            },

            # -----------------------------------------------------
            # INTERVENTION
            # -----------------------------------------------------
            "intervention": {

                "Réinstallation": (60, 415, 20, 20),

                "Désinstallation": (60, 440, 20, 20),

                "Dépannage": (60, 460, 20, 20),

                "Sauvegarde": (60, 485, 20, 20),

                "Récupération de données": (360, 415, 20, 20),

                "Nettoyage": (360, 440, 20, 20),

                "Formatage C": (360, 460, 20, 20),

                "Formatage D": (360, 485, 20, 20),

                "Configuration Boites Mails": (680, 415, 20, 20),

                "Configuration Réseau": (680, 440, 20, 20),

                "Mise à jour": (680, 460, 20, 20),

                "Suppression de virus": (680, 485, 20, 20),

                "Autre": (680, 500, 20, 20)
            },

            # -----------------------------------------------------
            # URGENT
            # -----------------------------------------------------
            "urgent": {

                "OUI": (60, 665, 20, 20),

                "NON": (230, 665, 20, 20)
            },

            # -----------------------------------------------------
            # PROBLÈME RÉSOLU
            # -----------------------------------------------------
            "resolu": {

                "OUI": (540, 665, 20, 20),

                "NON": (730, 665, 20, 20)
            }
        }

    # =============================================================
    # ADAPTATION DES COORDONNÉES SI L'IMAGE A UNE AUTRE TAILLE
    # =============================================================

    def scale_coordinates(self, image):

        height, width = image.shape[:2]

        scale_x = width / self.reference_width

        scale_y = height / self.reference_height

        return scale_x, scale_y

    # =============================================================
    # DÉTECTION D'UNE CASE COCHÉE
    # =============================================================

    def is_checked(self, image, coordinates):

        x, y, w, h = coordinates

        scale_x, scale_y = self.scale_coordinates(image)

        # Adapter les coordonnées à la taille réelle de l'image
        x = int(x * scale_x)
        y = int(y * scale_y)

        w = int(w * scale_x)
        h = int(h * scale_y)

        # Vérifier que la zone est dans l'image
        height, width = image.shape[:2]

        if (
            x < 0
            or y < 0
            or x + w > width
            or y + h > height
        ):
            return False, 0.0

        # Extraire la case
        roi = image[
            y:y + h,
            x:x + w
        ]

        if roi.size == 0:
            return False, 0.0

        # =========================================================
        # DÉTECTION DE LA COULEUR BLEUE
        # =========================================================

        hsv = cv2.cvtColor(
            roi,
            cv2.COLOR_BGR2HSV
        )

        # Bleu utilisé par le stylo
        lower_blue = np.array([
            90,
            40,
            30
        ])

        upper_blue = np.array([
            140,
            255,
            255
        ])

        blue_mask = cv2.inRange(
            hsv,
            lower_blue,
            upper_blue
        )

        # Pourcentage de pixels bleus
        blue_pixels = cv2.countNonZero(
            blue_mask
        )

        total_pixels = roi.shape[0] * roi.shape[1]

        blue_ratio = blue_pixels / total_pixels

        # Seuil
        checked = blue_ratio > 0.03

        return checked, blue_ratio

    # =============================================================
    # DÉTECTER UNE SECTION
    # =============================================================

    def detect_section(self, image, section_name):

        if section_name not in self.checkbox_config:

            raise ValueError(
                f"Section inconnue : {section_name}"
            )

        selected = []

        results = {}

        section = self.checkbox_config[
            section_name
        ]

        for label, coordinates in section.items():

            checked, ratio = self.is_checked(
                image,
                coordinates
            )

            results[label] = {

                "checked": checked,

                "blue_ratio": round(
                    ratio,
                    4
                )
            }

            if checked:

                selected.append(label)

        return selected, results

    # =============================================================
    # DÉTECTER TOUTES LES CASES
    # =============================================================

    def detect_all(self, image):

        result = {}

        debug_result = {}

        for section_name in self.checkbox_config:

            selected, details = self.detect_section(
                image,
                section_name
            )

            result[section_name] = selected

            debug_result[section_name] = details

        return result, debug_result

    # =============================================================
    # VERSION FINALE SIMPLIFIÉE
    # =============================================================

    def detect(self, image_path):

        image = cv2.imread(
            image_path
        )

        if image is None:

            raise FileNotFoundError(
                f"Image introuvable : {image_path}"
            )

        result, debug = self.detect_all(
            image
        )

        return result