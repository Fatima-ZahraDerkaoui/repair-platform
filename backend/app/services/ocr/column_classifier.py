import math


class ColumnClassifier:

    def __init__(self, colonnes):

        self.colonnes = colonnes

    # -----------------------------------------------------

    def nearest_column(self, x):

        meilleure_colonne = None
        meilleure_distance = float("inf")

        for nom, position in self.colonnes.items():

            distance = abs(x - position)

            if distance < meilleure_distance:

                meilleure_distance = distance
                meilleure_colonne = nom

        return meilleure_colonne

    # -----------------------------------------------------

    def classify(self, elements):

        resultat = []

        for element in elements:

            x1, y1, x2, y2 = element["box"]

            centre_x = (x1 + x2) / 2
            centre_y = (y1 + y2) / 2

            colonne = self.nearest_column(centre_x)

            resultat.append({

                "text": element["text"],

                "box": element["box"],

                "x": centre_x,

                "y": centre_y,

                "column": colonne

            })

        return resultat