import statistics


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
    # NORMALISATION
    # ==========================================================

    def normalize(self, text):

        if text is None:
            return ""

        return str(text).strip().upper()

    # ==========================================================
    # NOMBRE
    # ==========================================================

    def is_numeric(self, text):

        text = self.normalize(text)

        if not text:
            return False

        text = (
            text
            .replace("DHS", "")
            .replace("MAD", "")
            .replace("DH", "")
            .replace("%", "")
            .replace(" ", "")
        )

        text = text.replace(",", ".")

        try:
            float(text)
            return True
        except (ValueError, TypeError):
            return False

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

        if y < 250:
            return False

        if y > 1400:
            return False

        return True

    # ==========================================================
    # HEADERS
    # ==========================================================
    def is_reference_header(self, text):

        text = self.normalize(text)

        return text in {
            "REFERENCE",
            "RÉFÉRENCE",
            "REF",
            "REF."
        }


    def is_designation_header(self, text):

        text = self.normalize(text)

        return text in {
            "DESIGNATION",
            "DÉSIGNATION",
            "DESCRIPTION"
        }


    def is_quantity_header(self, text):

        text = self.normalize(text)

        return text in {
            "QUANTITE",
            "QUANTITÉ",
            "QTE",
            "QTÉ",
            "QTY"
        }


    def is_price_header(self, text):

        text = self.normalize(text)

        return text in {
            "PU",
            "P.U",
            "P.U.",
            "P.U HT",
            "P.U TTC",
            "PU HT",
            "PU TTC",
            "PRIX",
            "PRIX UNITAIRE",
            "PRIX UNITAIRE HT",
            "PRIX UNITAIRE TTC",
            "PRIX U"
        }


    def is_total_header(self, text):

        text = self.normalize(text)

        return text in {
            "TOTAL",
            "TOTAL HT",
            "TOTAL H.T",
            "TOTAL TTC",
            "TOTAL T.T.C",
            "MONTANT",
            "MONTANT HT",
            "MONTANT TTC",
            "MONTANT T.T.C"
        }


    def is_tva_header(self, text):

        text = self.normalize(text)

        return text in {
            "TVA",
            "TAUX TVA",
            "TAUX T.V.A",
            "TAUX"
        }

    def has_real_reference_header(self, elements):

        for element in elements:

            text = self.normalize(
                element.get("text", "")
            )

            if text in {
                "REFERENCE",
                "RÉFÉRENCE",
                "REF",
                "REF."
            }:
                return True

        return False

    # ==========================================================
    # DETECTION HEADERS
    # ==========================================================

    def detect_headers(self, elements):

        columns = {}

        for element in elements:

            text = self.normalize(
                element.get("text", "")
            )

            x = self.center_x(element)

            if self.is_reference_header(text):
                columns["reference"] = x

            elif self.is_designation_header(text):
                columns["designation"] = x

            elif self.is_quantity_header(text):
                columns["qte"] = x

            elif self.is_price_header(text):
                columns["pu"] = x

            elif self.is_total_header(text):
                columns["total"] = x

            elif self.is_tva_header(text):
                columns["tva"] = x

        return columns

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

            if abs(x - center) <= 45:
                clusters[-1].append(x)
            else:
                clusters.append([x])

        return [
            statistics.mean(cluster)
            for cluster in clusters
        ]

    # ==========================================================
    # QUANTITE
    # ==========================================================

    def detect_quantity_column(
        self,
        elements,
        existing_columns
    ):

        if "qte" in existing_columns:
            return existing_columns["qte"]

        candidates = []

        for element in elements:

            text = self.normalize(
                element.get("text", "")
            )

            if not self.is_numeric(text):
                continue

            cleaned = (
                text
                .replace(",", ".")
                .replace(" ", "")
            )

            try:
                value = float(cleaned)
            except (ValueError, TypeError):
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

        return min(
            candidates,
            key=lambda x: abs(x - 792)
        )

    # ==========================================================
    # PU / TOTAL
    # ==========================================================
    def detect_price_total_columns(
        self,
        elements,
        columns,
        numeric_columns
    ):

        # ======================================================
        # 1. Si les deux headers sont détectés
        # ======================================================

        if "pu" in columns and "total" in columns:
            return

        # ======================================================
        # 2. Nouveau format avec référence
        # ======================================================

        if "reference" in columns:

            # Si PU manque, chercher une colonne numérique
            # située après QTE et avant TOTAL éventuel.

            available = list(numeric_columns)

            if "qte" in columns:

                available = [
                    x for x in available
                    if abs(x - columns["qte"]) > 50
                ]

            # TVA éventuelle
            if "tva" in columns:

                available = [
                    x for x in available
                    if abs(x - columns["tva"]) > 50
                ]

            available = sorted(available)

            # --------------------------------------------------
            # PU
            # --------------------------------------------------

            if "pu" not in columns:

                if len(available) >= 2:

                    columns["pu"] = available[-2]

                elif len(available) == 1:

                    columns["pu"] = available[0]

            # --------------------------------------------------
            # TOTAL
            # --------------------------------------------------

            if "total" not in columns:

                if len(available) >= 2:

                    columns["total"] = available[-1]

            return

        # ======================================================
        # 3. Ancien format
        # ======================================================

        candidates = []

        for x in numeric_columns:

            if (
                "qte" in columns
                and abs(x - columns["qte"]) < 50
            ):
                continue

            if (
                "tva" in columns
                and abs(x - columns["tva"]) < 50
            ):
                continue

            candidates.append(x)

        candidates = sorted(candidates)

        if len(candidates) >= 2:

            if "pu" not in columns:
                columns["pu"] = candidates[-2]

            if "total" not in columns:
                columns["total"] = candidates[-1]

        elif len(candidates) == 1:

            if "total" not in columns:
                columns["total"] = candidates[0]

    # ==========================================================
    # DETECTION PRINCIPALE
    # ==========================================================

    def detect(self, elements):

        table_elements = [
            e
            for e in elements
            if self.is_table_candidate(e)
        ]

        if not table_elements:
            return {}

        columns = self.detect_headers(
            table_elements
        )

        numeric_columns = (
            self.detect_numeric_columns(
                table_elements
            )
        )

        has_reference_column = (
            self.has_real_reference_header(
                table_elements
            )
        )

        # ======================================================
        # NOUVEAU FORMAT
        # ======================================================

        if has_reference_column:

            defaults_new = {
                "reference": 224.0,
                "designation": 514.5,
                "qte": 792.0,
                "pu": 1002.0,
                "total": 1168.0,
            }

            if "designation" not in columns:
                columns["designation"] = (
                    defaults_new["designation"]
                )

            if "qte" not in columns:

                qte = self.detect_quantity_column(
                    table_elements,
                    columns
                )

                columns["qte"] = (
                    qte
                    if qte is not None
                    else defaults_new["qte"]
                )

            self.detect_price_total_columns(
                table_elements,
                columns,
                numeric_columns
            )

            for column, value in defaults_new.items():

                if column not in columns:
                    columns[column] = value

        # ======================================================
        # ANCIEN FORMAT
        # ======================================================

        else:

            if "designation" not in columns:
                columns["designation"] = 144.0

            if "qte" not in columns:

                qte = self.detect_quantity_column(
                    table_elements,
                    columns
                )

                columns["qte"] = (
                    qte
                    if qte is not None
                    else 970.0
                )

            self.detect_price_total_columns(
                table_elements,
                columns,
                numeric_columns
            )

            defaults_old = {
                "designation": 144.0,
                "tva": 771.0,
                "pu": 869.5,
                "qte": 970.0,
                "total": 1103.5,
            }

            for column, value in defaults_old.items():

                if column not in columns:
                    columns[column] = value

            columns.pop(
                "reference",
                None
            )

        return columns