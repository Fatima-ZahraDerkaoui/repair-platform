from collections import defaultdict


class TableBuilder:

    TOLERANCE_Y = 20

    def build(self, elements):

        groupes = defaultdict(list)

        for element in elements:

            y = element["box"][1]

            ligne = round(y / self.TOLERANCE_Y)

            groupes[ligne].append(element)

        tableau = []

        for elements_ligne in groupes.values():

            elements_ligne.sort(
                key=lambda e: e["box"][0]
            )

            tableau.append(elements_ligne)

        tableau.sort(
            key=lambda ligne: ligne[0]["box"][1]
        )

        return tableau