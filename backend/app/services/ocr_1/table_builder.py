class TableBuilder:

    def __init__(self, tolerance=18):
        self.tolerance = tolerance

    def build(self, elements):

        if not elements:
            return []

        # =====================================================
        # Trier tous les blocs OCR du haut vers le bas
        # =====================================================

        elements = sorted(
            elements,
            key=lambda e: (e["box"][1] + e["box"][3]) / 2
        )

        lignes = []

        ligne_courante = []

        y_reference = None

        # =====================================================
        # Construction dynamique des lignes
        # =====================================================

        for element in elements:

            x1, y1, x2, y2 = element["box"]

            centre_y = (y1 + y2) / 2

            # Première ligne
            if y_reference is None:

                ligne_courante.append(element)

                y_reference = centre_y

                continue

            # Même ligne ?
            if abs(centre_y - y_reference) <= self.tolerance:

                ligne_courante.append(element)

                # Mise à jour du centre moyen
                y_reference = (
                    y_reference * (len(ligne_courante) - 1)
                    + centre_y
                ) / len(ligne_courante)

            else:

                # Trier de gauche vers la droite
                ligne_courante.sort(
                    key=lambda e: e["box"][0]
                )

                lignes.append(ligne_courante)

                ligne_courante = [element]

                y_reference = centre_y

        # Dernière ligne
        if ligne_courante:

            ligne_courante.sort(
                key=lambda e: e["box"][0]
            )

            lignes.append(ligne_courante)

        # =====================================================
        # Fusion intelligente des descriptions multi-lignes
        # =====================================================

        resultat = []

        article_courant = None

        dans_tableau = False

        for ligne in lignes:

            texte = " ".join(
                c["text"]
                for c in ligne
            )

            upper = texte.upper()

            # Début du tableau
            if "DÉSIGNATION" in upper or "DESIGNATION" in upper:

                dans_tableau = True

                continue

            if not dans_tableau:
                continue

            # Fin du tableau
            if "TOTAL HT" in upper:

                if article_courant:

                    resultat.append(article_courant)

                    article_courant = None

                break

            premier = ligne[0]["text"].strip()

            # Nouvelle référence (générique)
            nouvelle_reference = (
                len(premier) >= 4
                and "-" in premier
            )

            if nouvelle_reference:

                if article_courant:

                    resultat.append(article_courant)

                article_courant = ligne.copy()

            else:

                if article_courant:

                    article_courant.extend(ligne)

        if article_courant:

            resultat.append(article_courant)

        # =====================================================
        # Tri final de chaque article
        # =====================================================

        for ligne in resultat:

            ligne.sort(
                key=lambda e: e["box"][0]
            )

        return resultat