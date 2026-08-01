from collections import defaultdict


class TableBuilder:

    def __init__(self, tolerance=15):
        self.tolerance = tolerance

    def build(self, elements):
        """
        Regroupe les mots OCR appartenant à une même ligne.
        """

        rows = defaultdict(list)

        for element in elements:

            x1, y1, x2, y2 = element["box"]

            center_y = (y1 + y2) / 2

            key = round(center_y / self.tolerance)

            rows[key].append(element)

        lignes = []

        for _, row in sorted(rows.items()):

            row = sorted(
                row,
                key=lambda e: e["box"][0]
            )

            lignes.append(row)

        return lignes