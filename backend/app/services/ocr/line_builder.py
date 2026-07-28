from collections import defaultdict


class LineBuilder:

    def build(self, ocr_result):

        lignes = defaultdict(list)

        for item in ocr_result:

            y = item["box"][1]

            cle = round(y / 15)

            lignes[cle].append(item)

        resultat = []

        for ligne in lignes.values():

            ligne.sort(key=lambda e: e["box"][0])

            resultat.append(ligne)

        return resultat