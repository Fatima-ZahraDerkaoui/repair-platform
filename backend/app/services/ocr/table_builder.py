from operator import itemgetter


class TableBuilder:

    def __init__(self, tolerance=18):
        self.tolerance = tolerance

    def build(self, elements):

        if not elements:
            return []

        # -----------------------------------------
        # Tri par Y
        # -----------------------------------------

        elements = sorted(
            elements,
            key=lambda e: e["box"][1]
        )

        lignes = []

        ligne_courante = []

        y_reference = None

        for element in elements:

            x1, y1, x2, y2 = element["box"]

            centre = (y1 + y2) / 2

            if y_reference is None:

                ligne_courante.append(element)

                y_reference = centre

                continue

            # Même ligne ?

            if abs(centre - y_reference) <= self.tolerance:

                ligne_courante.append(element)

                y_reference = (
                    y_reference * (len(ligne_courante)-1)
                    + centre
                ) / len(ligne_courante)

            else:

                ligne_courante.sort(
                    key=lambda e: e["box"][0]
                )

                lignes.append(ligne_courante)

                ligne_courante = [element]

                y_reference = centre

        if ligne_courante:

            ligne_courante.sort(
                key=lambda e: e["box"][0]
            )

            lignes.append(ligne_courante)

        return lignes