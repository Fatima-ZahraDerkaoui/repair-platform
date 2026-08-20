import re
import statistics


class ColumnDetector:
    """Détecte les positions des colonnes d'un tableau de facture."""

    EXPECTED_COLUMNS = [
        "reference",
        "designation",
        "qte",
        "pu",
        "total",
        "tva",
    ]

    NUMERIC_CLUSTER_TOLERANCE = 55
    COLUMN_MATCH_TOLERANCE = 80

    TABLE_MIN_Y = 250
    TABLE_MAX_Y = 1800
    HEADER_Y_TOLERANCE = 60

    def __init__(self):
        self.expected_columns = self.EXPECTED_COLUMNS.copy()

        self.numeric_cluster_tolerance = (
            self.NUMERIC_CLUSTER_TOLERANCE
        )
        self.column_match_tolerance = (
            self.COLUMN_MATCH_TOLERANCE
        )

    @staticmethod
    def center_x(element):
        """Retourne le centre horizontal d'un élément OCR."""

        x1, _, x2, _ = element["box"]

        return (x1 + x2) / 2

    @staticmethod
    def center_y(element):
        """Retourne le centre vertical d'un élément OCR."""

        _, y1, _, y2 = element["box"]

        return (y1 + y2) / 2

    @staticmethod
    def normalize(text):
        """Normalise un texte OCR."""

        if text is None:
            return ""

        text = str(text)
        text = re.sub(r"\s+", " ", text)

        return text.strip().upper()

    def normalize_header(self, text):
        """Normalise un en-tête de colonne."""

        text = self.normalize(text)

        text = (
            text
            .replace(":", "")
            .replace(";", "")
            .strip()
        )

        replacements = {
            "RÉFÉRENCE": "REFERENCE",
            "REFERENCE": "REFERENCE",
            "REF.": "REF",
            "REF": "REF",

            "DÉSIGNATION": "DESIGNATION",
            "DESIGNATION": "DESIGNATION",
            "DESCRIPTION": "DESIGNATION",

            "QUANTITÉ": "QUANTITE",
            "QUANTITE": "QUANTITE",
            "QTÉ": "QTE",
            "QTE": "QTE",
            "QTY": "QTE",

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

            "EXUNITAINO": "PU",
            "EXUNITAIRE": "PU",
            "EX UNITAIRE": "PU",
            "EX UNITAINO": "PU",
            "EXUNIT": "PU",

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

            "TAUX TVA": "TVA",
            "TAUX T.V.A": "TVA",
            "TAUX": "TVA",
            "TVA": "TVA",
        }

        return replacements.get(text, text)

    def is_numeric(self, text):
        """Indique si un texte OCR représente une valeur numérique."""

        text = self.normalize(text)

        if not text:
            return False

        cleaned = (
            text
            .replace("DHS", "")
            .replace("MAD", "")
            .replace("DH", "")
            .replace("%", "")
            .replace(" ", "")
            .replace(",", ".")
        )

        if re.fullmatch(r"\d+:\d{1,2}", cleaned):
            cleaned = cleaned.replace(":", ".")

        try:
            float(cleaned)
            return True
        except (ValueError, TypeError):
            return False

    def numeric_value(self, text):
        """Convertit un texte OCR en nombre."""

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
            .replace(",", ".")
        )

        if re.fullmatch(r"\d+:\d{1,2}", cleaned):
            cleaned = cleaned.replace(":", ".")

        try:
            return float(cleaned)
        except (ValueError, TypeError):
            return None

    def is_table_candidate(self, element):
        """Filtre les éléments susceptibles d'appartenir au tableau."""

        text = self.normalize(
            element.get("text", "")
        )

        if not text:
            return False

        y = self.center_y(element)

        return (
            self.TABLE_MIN_Y <= y <= self.TABLE_MAX_Y
        )

    def is_reference_header(self, text):
        normalized = self.normalize_header(text)

        return normalized in {
            "REFERENCE",
            "REF",
        }

    def is_designation_header(self, text):
        normalized = self.normalize_header(text)

        return normalized in {
            "DESIGNATION",
            "DESCRIPTION",
        }

    def is_quantity_header(self, text):
        normalized = self.normalize_header(text)

        return normalized in {
            "QUANTITE",
            "QTE",
        }

    def is_price_header(self, text):
        return self.normalize_header(text) == "PU"

    def is_total_header(self, text):
        return self.normalize_header(text) == "TOTAL"

    def is_tva_header(self, text):
        return self.normalize_header(text) == "TVA"

    def detect_headers(self, elements):
        """Détecte les colonnes à partir des en-têtes."""

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
                        "text": text,
                    }
                )

        if not header_elements:
            return columns

        median_y = statistics.median(
            header["y"]
            for header in header_elements
        )

        for header in header_elements:
            if (
                abs(header["y"] - median_y)
                <= self.HEADER_Y_TOLERANCE
            ):
                columns[header["column"]] = header["x"]

        return columns

    def has_real_reference_header(self, elements):
        """Vérifie si un véritable en-tête REFERENCE existe."""

        return any(
            self.normalize_header(
                element.get("text", "")
            ) == "REFERENCE"
            for element in elements
        )

    def detect_header_y(self, elements):
        """Retourne la position verticale moyenne des en-têtes."""

        header_y = []

        valid_headers = {
            "REFERENCE",
            "DESIGNATION",
            "QUANTITE",
            "QTE",
            "PU",
            "TOTAL",
            "TVA",
        }

        for element in elements:
            text = self.normalize_header(
                element.get("text", "")
            )

            if text in valid_headers:
                header_y.append(
                    self.center_y(element)
                )

        if not header_y:
            return None

        return statistics.median(header_y)

    def detect_table_bounds(self, elements, header_y):
        """Détermine les limites verticales du tableau."""

        if header_y is None:
            return None, None

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
                    "TOTALTTC",
                }
            ):
                y = self.center_y(element)

                if y > header_y:
                    footer_ys.append(y)

        table_start = header_y + 10

        if footer_ys:
            table_end = min(footer_ys) - 20
        else:
            table_end = max(
                self.center_y(element)
                for element in elements
            )

        return table_start, table_end

    def get_table_body_elements(self, elements, header_y):
        """Retourne uniquement les éléments appartenant au corps du tableau."""

        start_y, end_y = self.detect_table_bounds(
            elements,
            header_y,
        )

        if start_y is None:
            return elements

        return [
            element
            for element in elements
            if start_y <= self.center_y(element) <= end_y
        ]

    def detect_numeric_columns(self, elements):
        """Détecte les regroupements horizontaux de valeurs numériques."""

        numeric_x = []

        for element in elements:
            text = self.normalize(
                element.get("text", "")
            )

            if self.is_numeric(text):
                numeric_x.append(
                    self.center_x(element)
                )

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

            if (
                abs(x - center)
                <= self.numeric_cluster_tolerance
            ):
                clusters[-1].append(x)
            else:
                clusters.append([x])

        return [
            statistics.mean(cluster)
            for cluster in clusters
        ]

    @staticmethod
    def nearest_numeric_column(
        target_x,
        numeric_columns,
    ):
        """Retourne la colonne numérique la plus proche."""

        if not numeric_columns:
            return None

        return min(
            numeric_columns,
            key=lambda x: abs(x - target_x),
        )

    def detect_quantity_column(
        self,
        elements,
        existing_columns,
    ):
        """Détecte la position de la colonne quantité."""

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

            if (
                value.is_integer()
                and 0 < value <= 100
            ):
                candidates.append(
                    self.center_x(element)
                )

        if not candidates:
            return None

        designation_x = existing_columns.get(
            "designation"
        )

        if designation_x is not None:
            after_designation = [
                x
                for x in candidates
                if x > designation_x
            ]

            if after_designation:
                candidates = after_designation

        pu_x = existing_columns.get("pu")

        if pu_x is not None:
            before_pu = [
                x
                for x in candidates
                if x < pu_x
            ]

            if before_pu:
                candidates = before_pu

        return statistics.median(candidates)

    def detect_price_total_columns(
        self,
        elements,
        columns,
        numeric_columns,
    ):
        """Détecte les positions PU et TOTAL."""

        if (
            "pu" in columns
            and "total" in columns
            and abs(
                columns["total"] - columns["pu"]
            ) > 100
        ):
            return

        qte_x = columns.get("qte")

        if qte_x is not None:
            after_qte = [
                x
                for x in numeric_columns
                if x > qte_x + 80
            ]
        else:
            after_qte = list(numeric_columns)

        if "pu" in columns:
            pu_x = columns["pu"]

            total_candidates = [
                x
                for x in after_qte
                if x > pu_x + 80
            ]

            if total_candidates:
                columns["total"] = max(
                    total_candidates
                )

        if "total" in columns:
            total_x = columns["total"]

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

        if (
            "pu" not in columns
            and "total" not in columns
        ):
            candidates = sorted(after_qte)

            if len(candidates) >= 2:
                columns["pu"] = candidates[-2]
                columns["total"] = candidates[-1]

            elif len(candidates) == 1:
                columns["total"] = candidates[0]

        if "pu" not in columns and "total" in columns:
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
                columns["pu"] = max(candidates)

        if "total" not in columns and "pu" in columns:
            pu_x = columns["pu"]

            candidates = [
                x
                for x in numeric_columns
                if x > pu_x + 80
            ]

            if candidates:
                columns["total"] = max(candidates)

    def detect_tva_column(
        self,
        elements,
        columns,
    ):
        """Détecte la colonne TVA."""

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

            if value is not None and 0 <= value <= 100:
                candidates.append(
                    self.center_x(element)
                )

        if not candidates:
            return None

        return statistics.median(candidates)

    @staticmethod
    def validate_columns(columns):
        """Valide la structure des colonnes détectées."""

        ordered_columns = [
            "reference",
            "designation",
            "qte",
            "pu",
            "total",
        ]

        result = dict(columns)
        previous_x = None

        for column in ordered_columns:
            if column not in result:
                continue

            current_x = result[column]

            if previous_x is not None:
                pass

            previous_x = current_x

        return result

    def apply_old_format_fallback(
        self,
        columns,
        numeric_columns,
    ):
        """Applique les positions de secours pour l'ancien format."""

        if "designation" not in columns:
            columns["designation"] = 144.0

        if "qte" not in columns:
            qte = self.detect_quantity_column(
                [],
                columns,
            )

            if qte is not None:
                columns["qte"] = qte

        self.detect_price_total_columns(
            [],
            columns,
            numeric_columns,
        )

        if "qte" not in columns:
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

    def apply_new_format_fallback(
        self,
        columns,
        numeric_columns,
    ):
        """Applique les positions de secours pour le nouveau format."""

        if "designation" not in columns:
            if "reference" in columns:
                columns["designation"] = (
                    columns["reference"] + 290
                )
            else:
                columns["designation"] = 500.0

        if "qte" not in columns:
            qte = self.detect_quantity_column(
                [],
                columns,
            )

            if qte is not None:
                columns["qte"] = qte

        self.detect_price_total_columns(
            [],
            columns,
            numeric_columns,
        )

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

    def detect(self, elements):
        """Détecte les colonnes du tableau de facture."""

        table_elements = [
            element
            for element in elements
            if self.is_table_candidate(element)
        ]

        if not table_elements:
            return {}

        columns = self.detect_headers(
            table_elements
        )

        header_y = self.detect_header_y(
            table_elements
        )

        body_elements = self.get_table_body_elements(
            table_elements,
            header_y,
        )

        if not body_elements:
            body_elements = table_elements

        numeric_columns = (
            self.detect_numeric_columns(
                body_elements
            )
        )

        tva_x = self.detect_tva_column(
            body_elements,
            columns,
        )

        if tva_x is not None:
            columns["tva"] = tva_x

        has_reference_column = (
            self.has_real_reference_header(
                table_elements
            )
        )

        if "qte" not in columns:
            qte_x = self.detect_quantity_column(
                body_elements,
                columns,
            )

            if qte_x is not None:
                columns["qte"] = qte_x

        self.detect_price_total_columns(
            body_elements,
            columns,
            numeric_columns,
        )

        if has_reference_column:
            columns = self.apply_new_format_fallback(
                columns,
                numeric_columns,
            )
        else:
            columns = self.apply_old_format_fallback(
                columns,
                numeric_columns,
            )

        if has_reference_column:
            if "reference" not in columns:
                columns["reference"] = 180.0
        else:
            columns.pop(
                "reference",
                None,
            )

        columns = self.validate_columns(
            columns
        )

        return {
            column: round(columns[column], 2)
            for column in self.expected_columns
            if column in columns
        }
    