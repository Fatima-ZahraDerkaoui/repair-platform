import statistics
import re


class ColumnDetector:

    def __init__(self):

        self.expected_columns = [
            "reference",
            "designation",
            "qte",
            "pu",
            "total",
            "tva",
        ]

        # Tolérances horizontales
        self.numeric_cluster_tolerance = 55
        self.column_match_tolerance = 80

    # ==========================================================
    # CENTRE X
    # ==========================================================

    def center_x(self, element):

        x1, y1, x2, y2 = element["box"]

        return (x1 + x2) / 2

    # ==========================================================
    # CENTRE Y
    # ==========================================================

    def center_y(self, element):

        x1, y1, x2, y2 = element["box"]

        return (y1 + y2) / 2

    # ==========================================================
    # NORMALISATION GENERALE
    # ==========================================================

    def normalize(self, text):

        if text is None:
            return ""

        text = str(text)

        # Espaces multiples
        text = re.sub(r"\s+", " ", text)

        return text.strip().upper()

    # ==========================================================
    # NORMALISATION HEADER
    # ==========================================================

    def normalize_header(self, text):

        text = self.normalize(text)

        # Supprimer quelques caractères OCR parasites
        text = (
            text
            .replace(":", "")
            .replace(";", "")
            .strip()
        )

        replacements = {

            # --------------------------------------------------
            # REFERENCE
            # --------------------------------------------------

            "RÉFÉRENCE": "REFERENCE",
            "REFERENCE": "REFERENCE",
            "REF.": "REF",
            "REF": "REF",

            # --------------------------------------------------
            # DESIGNATION
            # --------------------------------------------------

            "DÉSIGNATION": "DESIGNATION",
            "DESIGNATION": "DESIGNATION",
            "DESCRIPTION": "DESIGNATION",

            # --------------------------------------------------
            # QUANTITE
            # --------------------------------------------------

            "QUANTITÉ": "QUANTITE",
            "QUANTITE": "QUANTITE",
            "QTÉ": "QTE",
            "QTE": "QTE",
            "QTY": "QTE",

            # --------------------------------------------------
            # PU
            # --------------------------------------------------

            "P.U": "PU",
            "P.U.": "PU",
            "PU": "PU",

            "P.U HT": "PU",
            "P.U TTC": "PU",
            "PU HT": "PU",
            "PU TTC": "PU",

            "PRIX": "PU",
            "PRIX U": "PU",
            "PRIX UNITAIRE": "PU",
            "PRIX UNITAIRE HT": "PU",
            "PRIX UNITAIRE TTC": "PU",

            # OCR fréquent
            "EXUNITAINO": "PU",
            "EXUNITAIRE": "PU",
            "EX UNITAIRE": "PU",
            "EX UNITAINO": "PU",
            "EXUNIT": "PU",

            # --------------------------------------------------
            # TOTAL
            # --------------------------------------------------

            "TOTAL": "TOTAL",
            "TOTAL HT": "TOTAL",
            "TOTAL H.T": "TOTAL",
            "TOTAL H.T.": "TOTAL",

            "TOTAL TTC": "TOTAL",
            "TOTAL T.T.C": "TOTAL",
            "TOTAL T.T.C.": "TOTAL",

            "MONTANT": "TOTAL",
            "MONTANT HT": "TOTAL",
            "MONTANT TTC": "TOTAL",
            "MONTANT T.T.C": "TOTAL",

            # --------------------------------------------------
            # TVA
            # --------------------------------------------------

            "TAUX TVA": "TVA",
            "TAUX T.V.A": "TVA",
            "TAUX": "TVA",
            "TVA": "TVA",
        }

        return replacements.get(text, text)

    # ==========================================================
    # NOMBRE
    # ==========================================================

    def is_numeric(self, text):

        text = self.normalize(text)

        if not text:
            return False

        cleaned = text

        cleaned = (
            cleaned
            .replace("DHS", "")
            .replace("MAD", "")
            .replace("DH", "")
            .replace("%", "")
            .replace(" ", "")
        )

        # OCR peut produire :
        # 720:00
        # 720,00
        # 720.00

        cleaned = cleaned.replace(",", ".")

        # Corriger ":" utilisé comme séparateur décimal
        if re.fullmatch(r"\d+:\d{1,2}", cleaned):
            cleaned = cleaned.replace(":", ".")

        try:

            float(cleaned)

            return True

        except (ValueError, TypeError):

            return False

    # ==========================================================
    # CONVERSION NUMERIQUE
    # ==========================================================

    def numeric_value(self, text):

        text = self.normalize(text)

        if not text:
            return None

        cleaned = (
            text
            .replace("DHS", "")
            .replace("MAD", "")
            .replace("DH", "")
            .replace("%", "")
            .replace(" ", "")
        )

        cleaned = cleaned.replace(",", ".")

        if re.fullmatch(r"\d+:\d{1,2}", cleaned):
            cleaned = cleaned.replace(":", ".")

        try:
            return float(cleaned)

        except (ValueError, TypeError):

            return None

    # ==========================================================
    # ELEMENT TABLEAU
    # ==========================================================

    def is_table_candidate(self, element):

        text = self.normalize(
            element.get("text", "")
        )

        if not text:
            return False

        y = self.center_y(element)

        # On évite le haut de facture
        if y < 250:
            return False

        # On garde une limite suffisamment large.
        # Le vrai filtrage vertical sera fait après détection
        # des headers.
        if y > 1800:
            return False

        return True

    # ==========================================================
    # HEADERS
    # ==========================================================

    def is_reference_header(self, text):

        text = self.normalize_header(text)

        return text in {
            "REFERENCE",
            "REF"
        }

    def is_designation_header(self, text):

        text = self.normalize_header(text)

        return text in {
            "DESIGNATION",
            "DESCRIPTION"
        }

    def is_quantity_header(self, text):

        text = self.normalize_header(text)

        return text in {
            "QUANTITE",
            "QTE"
        }

    def is_price_header(self, text):

        text = self.normalize_header(text)

        return text == "PU"

    def is_total_header(self, text):

        text = self.normalize_header(text)

        return text == "TOTAL"

    def is_tva_header(self, text):

        text = self.normalize_header(text)

        return text == "TVA"

    # ==========================================================
    # DETECTION HEADER PRINCIPAL
    # ==========================================================

    def detect_headers(self, elements):

        columns = {}

        header_elements = []

        for element in elements:

            text = self.normalize_header(
                element.get("text", "")
            )

            if not text:
                continue

            x = self.center_x(element)
            y = self.center_y(element)

            detected_column = None

            if self.is_reference_header(text):

                detected_column = "reference"

            elif self.is_designation_header(text):

                detected_column = "designation"

            elif self.is_quantity_header(text):

                detected_column = "qte"

            elif self.is_price_header(text):

                detected_column = "pu"

            elif self.is_total_header(text):

                detected_column = "total"

            elif self.is_tva_header(text):

                detected_column = "tva"

            if detected_column:

                header_elements.append(
                    {
                        "column": detected_column,
                        "x": x,
                        "y": y,
                        "text": text
                    }
                )

        # ------------------------------------------------------
        # Les headers d'un tableau sont normalement proches
        # verticalement.
        # ------------------------------------------------------

        if not header_elements:
            return columns

        # Pour chaque colonne, on prend le header le plus
        # proche du centre du groupe de headers.
        ys = [
            h["y"]
            for h in header_elements
        ]

        median_y = statistics.median(ys)

        for h in header_elements:

            if abs(h["y"] - median_y) <= 60:

                columns[h["column"]] = h["x"]

        return columns

    # ==========================================================
    # HEADER REFERENCE REEL
    # ==========================================================

    def has_real_reference_header(self, elements):

        for element in elements:

            text = self.normalize_header(
                element.get("text", "")
            )

            if text == "REFERENCE":

                return True

        return False

    # ==========================================================
    # OBTENIR Y HEADER
    # ==========================================================

    def detect_header_y(self, elements):

        header_candidates = []

        for element in elements:

            text = self.normalize_header(
                element.get("text", "")
            )

            if text in {
                "REFERENCE",
                "DESIGNATION",
                "QUANTITE",
                "QTE",
                "PU",
                "TOTAL",
                "TVA",
            }:

                header_candidates.append(
                    self.center_y(element)
                )

        if not header_candidates:

            return None

        return statistics.median(
            header_candidates
        )

    # ==========================================================
    # DETECTION DEBUT / FIN TABLEAU
    # ==========================================================

    def detect_table_bounds(
        self,
        elements,
        header_y
    ):

        if header_y is None:

            return None, None

        # ------------------------------------------------------
        # Détection du footer
        # ------------------------------------------------------

        footer_keywords = {
            "TOTAL HT",
            "TOTALHT",
            "TOTAL TVA",
            "TOTALTTC",
            "TOTAL TTC",
            "ARRÊTÉE",
            "ARRETEE",
            "MODE DE REGLEMENT",
            "MODE DE RÈGLEMENT",
        }

        footer_ys = []

        for element in elements:

            text = self.normalize(
                element.get("text", "")
            )

            compact = text.replace(" ", "")

            if (
                text in footer_keywords
                or compact in {
                    "TOTALHT",
                    "TOTALTVA",
                    "TOTALTTC"
                }
            ):

                y = self.center_y(element)

                if y > header_y:

                    footer_ys.append(y)

        # ------------------------------------------------------
        # Limite haute
        # ------------------------------------------------------

        table_start = header_y + 10

        # ------------------------------------------------------
        # Limite basse
        # ------------------------------------------------------

        if footer_ys:

            table_end = min(footer_ys) - 20

        else:

            # Pas de footer détecté.
            # On garde les éléments jusqu'à une limite
            # raisonnable.
            table_end = max(
                self.center_y(e)
                for e in elements
            )

        return table_start, table_end

    # ==========================================================
    # ELEMENTS REELLEMENT DANS LE TABLEAU
    # ==========================================================

    def get_table_body_elements(
        self,
        elements,
        header_y
    ):

        start_y, end_y = self.detect_table_bounds(
            elements,
            header_y
        )

        if start_y is None:
            return elements

        body = []

        for element in elements:

            y = self.center_y(element)

            if start_y <= y <= end_y:

                body.append(element)

        return body

    # ==========================================================
    # COLONNES NUMERIQUES
    # ==========================================================

    def detect_numeric_columns(self, elements):

        numeric_x = []

        for element in elements:

            text = self.normalize(
                element.get("text", "")
            )

            if not self.is_numeric(text):
                continue

            x = self.center_x(element)

            numeric_x.append(x)

        if not numeric_x:
            return []

        numeric_x.sort()

        clusters = []

        for x in numeric_x:

            if not clusters:

                clusters.append([x])

                continue

            center = statistics.mean(
                clusters[-1]
            )

            if abs(x - center) <= self.numeric_cluster_tolerance:

                clusters[-1].append(x)

            else:

                clusters.append([x])

        return [
            statistics.mean(cluster)
            for cluster in clusters
        ]

    # ==========================================================
    # NUMERIC COLUMN BY POSITION
    # ==========================================================

    def nearest_numeric_column(
        self,
        target_x,
        numeric_columns
    ):

        if not numeric_columns:

            return None

        return min(
            numeric_columns,
            key=lambda x: abs(x - target_x)
        )

    # ==========================================================
    # QUANTITE
    # ==========================================================

    def detect_quantity_column(
        self,
        elements,
        existing_columns
    ):

        # ------------------------------------------------------
        # Header prioritaire
        # ------------------------------------------------------

        if "qte" in existing_columns:

            return existing_columns["qte"]

        candidates = []

        for element in elements:

            text = self.normalize(
                element.get("text", "")
            )

            if not self.is_numeric(text):

                continue

            value = self.numeric_value(text)

            if value is None:

                continue

            # Une quantité article est généralement :
            # entière et raisonnable.
            if (
                value.is_integer()
                and 0 < value <= 100
            ):

                candidates.append(
                    self.center_x(element)
                )

        if not candidates:

            return None

        # ------------------------------------------------------
        # Chercher la zone de quantité.
        #
        # Si référence présente, la quantité est généralement
        # après designation et avant PU.
        # ------------------------------------------------------

        if "designation" in existing_columns:

            candidates_after_designation = [
                x
                for x in candidates
                if x > existing_columns["designation"]
            ]

            if candidates_after_designation:

                candidates = (
                    candidates_after_designation
                )

        if "pu" in existing_columns:

            before_pu = [
                x
                for x in candidates
                if x < existing_columns["pu"]
            ]

            if before_pu:

                candidates = before_pu

        # ------------------------------------------------------
        # Le centre robuste des candidats est meilleur qu'une
        # constante 792/970.
        # ------------------------------------------------------

        if candidates:

            return statistics.median(candidates)

        return None

    # ==========================================================
    # DETECTION PU / TOTAL
    # ==========================================================

    def detect_price_total_columns(
        self,
        elements,
        columns,
        numeric_columns
    ):

        # ======================================================
        # 1. HEADER PRIORITAIRE
        # ======================================================

        # Rien à faire si les deux sont déjà fiables.
        if (
            "pu" in columns
            and "total" in columns
            and abs(columns["total"] - columns["pu"]) > 100
        ):
            return

        # ======================================================
        # 2. POSITION QUANTITE
        # ======================================================

        qte_x = columns.get("qte")

        # Colonnes numériques réellement situées après QTE
        after_qte = []

        if qte_x is not None:

            after_qte = [
                x
                for x in numeric_columns
                if x > qte_x + 80
            ]

        else:

            after_qte = list(numeric_columns)

        # ======================================================
        # 3. SI PU EXISTE
        # ======================================================

        if "pu" in columns:

            pu_x = columns["pu"]

            # Si PU est clairement positionné, on cherche
            # TOTAL à droite.
            total_candidates = [
                x
                for x in after_qte
                if x > pu_x + 80
            ]

            if total_candidates:

                columns["total"] = max(
                    total_candidates
                )

        # ======================================================
        # 4. SI TOTAL EXISTE
        # ======================================================

        if "total" in columns:

            total_x = columns["total"]

            # Le PU doit être avant TOTAL.
            pu_candidates = [
                x
                for x in numeric_columns
                if x < total_x - 80
            ]

            if qte_x is not None:

                pu_candidates = [
                    x
                    for x in pu_candidates
                    if x > qte_x + 80
                ]

            if pu_candidates:

                columns["pu"] = max(
                    pu_candidates
                )

        # ======================================================
        # 5. SI LES DEUX MANQUENT
        # ======================================================

        if (
            "pu" not in columns
            and "total" not in columns
        ):

            candidates = sorted(after_qte)

            if len(candidates) >= 2:

                # Dans les factures classiques :
                #
                # QTE -> PU -> TOTAL
                #
                columns["pu"] = candidates[-2]
                columns["total"] = candidates[-1]

            elif len(candidates) == 1:

                columns["total"] = candidates[0]

        # ======================================================
        # 6. SI PU MANQUE
        # ======================================================

        if "pu" not in columns:

            if "total" in columns:

                total_x = columns["total"]

                candidates = [
                    x
                    for x in numeric_columns
                    if x < total_x - 80
                ]

                if qte_x is not None:

                    candidates = [
                        x
                        for x in candidates
                        if x > qte_x + 80
                    ]

                if candidates:

                    columns["pu"] = max(
                        candidates
                    )

        # ======================================================
        # 7. SI TOTAL MANQUE
        # ======================================================

        if "total" not in columns:

            if "pu" in columns:

                pu_x = columns["pu"]

                candidates = [
                    x
                    for x in numeric_columns
                    if x > pu_x + 80
                ]

                if candidates:

                    columns["total"] = max(
                        candidates
                    )

    # ==========================================================
    # DETECTION TVA
    # ==========================================================

    def detect_tva_column(
        self,
        elements,
        columns
    ):

        if "tva" in columns:

            return columns["tva"]

        candidates = []

        for element in elements:

            text = self.normalize(
                element.get("text", "")
            )

            if "%" not in text:

                continue

            value = self.numeric_value(text)

            if value is None:

                continue

            if 0 <= value <= 100:

                candidates.append(
                    self.center_x(element)
                )

        if not candidates:

            return None

        return statistics.median(
            candidates
        )

    # ==========================================================
    # VALIDATION DES COLONNES
    # ==========================================================

    def validate_columns(self, columns):

        # ------------------------------------------------------
        # Ordre logique
        #
        # reference < designation < qte < pu < total
        # ------------------------------------------------------

        ordered = [
            "reference",
            "designation",
            "qte",
            "pu",
            "total"
        ]

        result = dict(columns)

        previous_x = None

        for column in ordered:

            if column not in result:

                continue

            x = result[column]

            if previous_x is not None:

                # Si deux colonnes sont incohérentes,
                # on ne supprime pas immédiatement.
                # On laisse le fallback décider.
                pass

            previous_x = x

        return result

    # ==========================================================
    # FALLBACK FORMAT SANS REFERENCE
    # ==========================================================

    def apply_old_format_fallback(
        self,
        columns,
        numeric_columns
    ):

        # ------------------------------------------------------
        # Ancien format typique :
        #
        # DESIGNATION | TVA | PU | QTE | TOTAL
        #
        # Mais les X peuvent changer fortement d'une facture
        # à l'autre.
        # ------------------------------------------------------

        if "designation" not in columns:

            columns["designation"] = 144.0

        if "qte" not in columns:

            qte = self.detect_quantity_column(
                [],
                columns
            )

            if qte is not None:

                columns["qte"] = qte

        # ------------------------------------------------------
        # PU / TOTAL
        # ------------------------------------------------------

        self.detect_price_total_columns(
            [],
            columns,
            numeric_columns
        )

        # ------------------------------------------------------
        # Fallback uniquement si impossible de détecter.
        # ------------------------------------------------------

        if "qte" not in columns:

            # Ne plus utiliser 970 comme valeur universelle.
            # On choisit une position entre designation et PU.
            if "pu" in columns:

                columns["qte"] = (
                    columns["pu"] - 120
                )

            else:

                columns["qte"] = 970.0

        if "pu" not in columns:

            if "total" in columns:

                columns["pu"] = (
                    columns["total"] - 160
                )

            else:

                columns["pu"] = 900.0

        if "total" not in columns:

            columns["total"] = (
                columns["pu"] + 250
            )

        return columns

    # ==========================================================
    # FALLBACK FORMAT AVEC REFERENCE
    # ==========================================================

    def apply_new_format_fallback(
        self,
        columns,
        numeric_columns
    ):

        # ------------------------------------------------------
        # DESIGNATION
        # ------------------------------------------------------

        if "designation" not in columns:

            if "reference" in columns:

                columns["designation"] = (
                    columns["reference"] + 290
                )

            else:

                columns["designation"] = 500.0

        # ------------------------------------------------------
        # QTE
        # ------------------------------------------------------

        if "qte" not in columns:

            qte = self.detect_quantity_column(
                [],
                columns
            )

            if qte is not None:

                columns["qte"] = qte

        # ------------------------------------------------------
        # PU / TOTAL
        # ------------------------------------------------------

        self.detect_price_total_columns(
            [],
            columns,
            numeric_columns
        )

        # ------------------------------------------------------
        # Fallback
        # ------------------------------------------------------

        if "qte" not in columns:

            if "pu" in columns:

                columns["qte"] = (
                    columns["pu"] - 210
                )

            else:

                columns["qte"] = 790.0

        if "pu" not in columns:

            if "total" in columns:

                columns["pu"] = (
                    columns["total"] - 165
                )

            else:

                columns["pu"] = 1000.0

        if "total" not in columns:

            columns["total"] = (
                columns["pu"] + 165
            )

        return columns

    # ==========================================================
    # DETECTION PRINCIPALE
    # ==========================================================

    def detect(self, elements):

        # ======================================================
        # 1. ELEMENTS VALIDES
        # ======================================================

        table_elements = [
            e
            for e in elements
            if self.is_table_candidate(e)
        ]

        if not table_elements:

            return {}

        # ======================================================
        # 2. DETECTION HEADERS
        # ======================================================

        columns = self.detect_headers(
            table_elements
        )

        # ======================================================
        # 3. HEADER Y
        # ======================================================

        header_y = self.detect_header_y(
            table_elements
        )

        # ======================================================
        # 4. ELEMENTS DU CORPS TABLEAU
        # ======================================================

        body_elements = self.get_table_body_elements(
            table_elements,
            header_y
        )

        if not body_elements:

            body_elements = table_elements

        # ======================================================
        # 5. COLONNES NUMERIQUES
        #
        # IMPORTANT :
        # On utilise uniquement le corps du tableau.
        # Les valeurs 4150 / 830 / 4980 du footer ne polluent
        # donc plus les colonnes articles.
        # ======================================================

        numeric_columns = (
            self.detect_numeric_columns(
                body_elements
            )
        )

        # ======================================================
        # 6. TVA
        # ======================================================

        tva = self.detect_tva_column(
            body_elements,
            columns
        )

        if tva is not None:

            columns["tva"] = tva

        # ======================================================
        # 7. REFERENCE ?
        # ======================================================

        has_reference_column = (
            self.has_real_reference_header(
                table_elements
            )
        )

        # ======================================================
        # 8. QUANTITE
        # ======================================================

        if "qte" not in columns:

            qte = self.detect_quantity_column(
                body_elements,
                columns
            )

            if qte is not None:

                columns["qte"] = qte

        # ======================================================
        # 9. PU / TOTAL
        # ======================================================

        self.detect_price_total_columns(
            body_elements,
            columns,
            numeric_columns
        )

        # ======================================================
        # 10. FALLBACK
        # ======================================================

        if has_reference_column:

            columns = self.apply_new_format_fallback(
                columns,
                numeric_columns
            )

        else:

            columns = self.apply_old_format_fallback(
                columns,
                numeric_columns
            )

        # ======================================================
        # 11. REFERENCE
        # ======================================================

        if has_reference_column:

            if "reference" not in columns:

                columns["reference"] = 180.0

        else:

            columns.pop(
                "reference",
                None
            )

        # ======================================================
        # 12. VALIDATION
        # ======================================================

        columns = self.validate_columns(
            columns
        )

        # ======================================================
        # 13. ORDRE FINAL
        # ======================================================

        ordered_columns = {}

        for column in self.expected_columns:

            if column in columns:

                ordered_columns[column] = (
                    round(columns[column], 2)
                )

        return ordered_columns

    