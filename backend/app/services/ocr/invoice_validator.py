class InvoiceValidator:

    def __init__(self, tolerance=0.10):

        self.tolerance = tolerance
        self.line_tolerance = tolerance
        self.total_tolerance = tolerance

    # ======================================================

    def almost_equal(self, a, b, tolerance=None):

        if a is None or b is None:
            return False

        if tolerance is None:
            tolerance = self.tolerance

        return abs(a - b) <= tolerance

    # ======================================================

    def validate_article(self, article):

        errors = []

        if not article["designation"]:
            errors.append("designation vide")

        if article["prix_unitaire"] is None:
            errors.append("prix unitaire absent")

        if article["quantite"] is None:
            errors.append("quantite absente")

        if article["total"] is None:
            errors.append("total absent")

        if (
            article["prix_unitaire"] is not None
            and article["quantite"] is not None
            and article["total"] is not None
        ):

            attendu = (
                article["prix_unitaire"]
                * article["quantite"]
            )

            if not self.almost_equal(attendu, article["total"]):

                errors.append(
                    f"total incorrect ({attendu:.2f} attendu)"
                )

        return errors

    # ======================================================

    def validate_articles(self, articles):

        resultat = []

        for i, article in enumerate(articles):

            resultat.append({

                "index": i + 1,

                "reference": article["reference"],

                "errors": self.validate_article(article)

            })

        return resultat

    # ======================================================

    def validate_totals(self, facture):

        errors = []

        articles = facture.get("articles", [])

        # ==================================================
        # 1. Calcul du total des lignes
        # ==================================================

        total_lignes = 0.0

        for article in articles:

            total = article.get("total")

            if total is not None:
                total_lignes += total

        total_lignes = round(total_lignes, 2)

        # ==================================================
        # 2. Vérification avec Total HT
        # ==================================================

        total_ht = facture.get("total_ht")

        if total_ht is not None:

            total_ht = round(total_ht, 2)

            if not self.almost_equal(
                total_lignes,
                total_ht
            ):

                errors.append(
                    f"Somme lignes = {total_lignes:.2f}"
                    f" / HT facture = {total_ht:.2f}"
                )

        # ==================================================
        # 3. Vérification HT + TVA = TTC
        # ==================================================

        total_tva = facture.get("total_tva")
        total_ttc = facture.get("total_ttc")

        if (
            total_ht is not None
            and total_tva is not None
            and total_ttc is not None
        ):

            attendu_ttc = round(
                total_ht + total_tva,
                2
            )

            if not self.almost_equal(
                attendu_ttc,
                total_ttc
            ):

                errors.append(
                    f"HT + TVA = {attendu_ttc:.2f}"
                    f" / TTC facture = {total_ttc:.2f}"
                )

        return errors

    # ======================================================

    def compute_score(self, facture):

        score = 100

        if facture.get("numero") is None:
            score -= 10

        if facture.get("date") is None:
            score -= 10

        if facture.get("supplier") is None:
            score -= 10

        articles = facture.get("articles", [])

        for article in articles:

            if self.validate_article(article):

                score -= 5

        if self.validate_totals(facture):

            score -= 10

        return max(score, 0)

    # ======================================================
    def validate(self, facture):

        articles = facture.get("articles", [])

        return {

            "score": self.compute_score(facture),

            # contrôles globaux
            "required": self.validate_required_fields(facture),

            "amounts": self.validate_amounts(facture),

            "references": self.validate_duplicate_reference(articles),

            "tva": self.validate_tva_values(articles),

            "designation": self.validate_designation(articles),

            "quantity": self.validate_quantity(articles),

            "price": self.validate_price(articles),

            "articles": self.validate_articles(articles),

            "invoice_totals": self.validate_totals(facture),

            "line_totals": self.validate_line_total(articles)
        }

    def validate_required_fields(self, facture):

        errors = []

        required = [
            "numero",
            "date",
            "supplier",
            "articles"
        ]

        for field in required:

            if not facture.get(field):

                errors.append(f"{field} manquant")

        return errors

    def validate_amounts(self, facture):

        errors = []

        ht = facture.get("total_ht")
        tva = facture.get("total_tva")
        ttc = facture.get("total_ttc")

        if None in (ht, tva, ttc):

            return errors

        attendu = round(ht + tva, 2)

        if not self.almost_equal(attendu, ttc):

            errors.append(

                f"HT + TVA = {attendu:.2f} mais TTC = {ttc:.2f}"

            )

        return errors

    def validate_tva_values(self, articles):

        errors = []

        valeurs_valides = {
            0,
            7,
            10,
            14,
            20
        }

        for i, article in enumerate(articles):

            tva = article.get("tva")

            if tva is None:
                continue

            if tva not in valeurs_valides:

                errors.append(
                    f"Article {i+1}: TVA inhabituelle ({tva})"
                )

        return errors

    def validate_duplicate_reference(self, articles):

        errors = []

        deja = set()

        for article in articles:

            ref = article["reference"]

            if not ref:

                continue

            if ref in deja:

                errors.append(

                    f"Référence dupliquée : {ref}"

                )

            deja.add(ref)

        return errors

    def validate_designation(self, articles):

        errors = []

        for i, article in enumerate(articles):

            designation = article.get(
                "designation"
            )

            if not designation:

                errors.append(
                    f"Article {i+1}: désignation vide"
                )

                continue

            designation = str(
                designation
            ).strip()

            if len(designation) < 3:

                errors.append(
                    f"Article {i+1}: désignation trop courte"
                )

        return errors

    def validate_quantity(self, articles):

        errors = []

        for i, article in enumerate(articles):

            qte = article["quantite"]

            if qte is None:

                continue

            if qte <= 0:

                errors.append(

                    f"Article {i+1}: quantité <= 0"

                )

            if qte > 1000:

                errors.append(

                    f"Article {i+1}: quantité suspecte ({qte})"

                )

        return errors

    def validate_price(self, articles):

        errors = []

        for i, article in enumerate(articles):

            pu = article["prix_unitaire"]

            if pu is None:

                continue

            if pu < 0:

                errors.append(

                    f"Article {i+1}: prix négatif"

                )

        return errors

    def validate_line_total(self, articles):

        errors = []

        for i, article in enumerate(articles):

            if None in (

                article["prix_unitaire"],
                article["quantite"],
                article["total"]

            ):

                continue

            attendu = round(

                article["prix_unitaire"]
                * article["quantite"],

                2

            )

            if not self.almost_equal(

                attendu,

                article["total"]

            ):

                errors.append(

                    f"Article {i+1}: total incorrect"

                )

        return errors

