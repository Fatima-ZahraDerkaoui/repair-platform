import re


class ArticleParser:
    """Parse les lignes produites par LineBuilder en articles structurés."""

    def __init__(self, tolerance=0.05):
        self.tolerance = tolerance

        self.reference_pattern = re.compile(
            r"^[A-Z0-9._/\\-]+$",
            re.IGNORECASE
        )

        self.footer_markers = [
            "TOTAL HT",
            "TOTAL H T",
            "TOTAL H.T",
            "TOTAL TVA",
            "TOTAL T.V.A",
            "TOTAL TTC",
            "TOTAL T.T.C",
            "NET A PAYER",
            "NET À PAYER",
            "NET A PAYE",
            "A PAYER",
            "À PAYER",
            "SOUS TOTAL",
            "SOUS-TOTAL",
            "MODE DE REGLEMENT",
            "MODE DE RÈGLEMENT",
            "ARRETEE LA PRESENTE FACTURE",
            "ARRÊTÉE LA PRÉSENTE FACTURE",
            "TOTAL GENERAL",
            "TOTAL GENERAL TTC",
            "TOTAL GENERAL HT",
        ]

        self.footer_text_markers = [
            "SIEGE SOCIAL",
            "SIEGE SOCIAl",
            "SLÈGE SOCIAL",
            "SLEGO SOCIAL",
            "TELEPHONE",
            "TEL:",
            "TEL :",
            "FAX",
            "RIB",
            "ICE:",
            "ICE :",
            "I.F.",
            "IF:",
            "IF :",
            "R.C.",
            "RC:",
            "RC :",
            "PATENTE",
            "C.N.S.S.",
            "CNSS",
            "CAPITAL DE",
            "MAGASINIER",
            "NOS MARCHANDISES",
            "GARANTIE",
            "RETOUR AVEC",
        ]

        self.address_markers = [
            "RUE DE",
            "RUE ",
            "BD ",
            "BD.",
            "BOULEVARD",
            "AVENUE",
            "AV.",
            "KAMARIAT",
            "KISSARIA",
            "LOTISSEMENT",
            "QUARTIER",
            "DERB",
            "RESIDENCE",
            "RESIDENCE ",
        ]

        self.quantity_columns = {
            "QTE",
            "QUANTITE",
            "QUANT",
            "QT",
            "Q",
            "QTY",
        }

        self.unit_price_columns = {
            "PU",
            "PUTTC",
            "PUHT",
            "PRIX",
            "PRIXUNITAIRE",
            "PRIXUNITAIRETTC",
            "PRIXUNITAIREHT",
            "UNITPRICE",
            "UNITPRICEHT",
            "UNITPRICETTC",
        }

        self.tva_columns = {
            "TVA",
            "TAUX",
            "TAUXTVA",
        }

        self.total_columns = {
            "TOTAL",
            "TOTALTTC",
            "TOTALHT",
            "MONTANT",
            "MONTANTTTC",
            "MONTANTHT",
            "NETAPAYER",
            "TOTALAMOUNT",
            "TOT",
            "TOTAT",
            "TOTALTC",
            "TOTALTT",
            "PRIXTOTAL",
            "PRIXTOTALTTC",
            "VALEUR",
            "VALEURTTC",
        }

    @staticmethod
    def normalize_text(text):
        if text is None:
            return ""

        text = str(text)

        text = text.replace("\n", " ")
        text = text.replace("\r", " ")
        text = text.replace("\t", " ")

        replacements = str.maketrans({
            "É": "E",
            "È": "E",
            "Ê": "E",
            "Ë": "E",
            "À": "A",
            "Â": "A",
            "Ç": "C",
            "Ù": "U",
            "Û": "U",
            "Ü": "U",
            "Ô": "O",
            "Ö": "O",
            "Î": "I",
            "Ï": "I",
            "é": "e",
            "è": "e",
            "ê": "e",
            "ë": "e",
            "à": "a",
            "â": "a",
            "ç": "c",
            "ù": "u",
            "û": "u",
            "ü": "u",
            "ô": "o",
            "ö": "o",
            "î": "i",
            "ï": "i",
        })

        text = text.translate(replacements)
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    def normalize_column(self, column):
        if not column:
            return ""

        column = self.normalize_text(column).upper()

        column = column.replace("MONANT", "MONTANT")
        column = column.replace("MONTAT", "MONTANT")
        column = column.replace("TOTAl", "TOTAL")

        return re.sub(r"[^A-Z0-9]", "", column)

    def is_quantity_column(self, column):
        return self.normalize_column(column) in self.quantity_columns

    def is_unit_price_column(self, column):
        return self.normalize_column(column) in self.unit_price_columns

    def is_tva_column(self, column):
        return self.normalize_column(column) in self.tva_columns

    def is_total_column(self, column):
        return self.normalize_column(column) in self.total_columns

    @staticmethod
    def remove_duplicate_words(text):
        words = text.split()
        result = []

        for word in words:
            if not result or result[-1].upper() != word.upper():
                result.append(word)

        return " ".join(result)

    def is_footer_text(self, text):
        text = self.normalize_text(text)

        if not text:
            return False

        upper = text.upper()

        for marker in self.footer_markers:
            if marker in upper:
                return True

        for marker in self.footer_text_markers:
            if marker in upper:
                return True

        return False

    def is_supplier_noise(self, text):
        text = self.normalize_text(text)

        if not text:
            return False

        upper = text.upper()

        if re.search(r"\b0[5-7]\d{8}\b", upper):
            return True

        if re.search(r"\+212\s*[5-7]\d{8}", upper):
            return True

        if re.search(
            r"\b(?:ICE|1CE)\s*[:\-]?\s*\d{10,20}\b",
            upper
        ):
            return True

        if re.search(
            r"\bRIB\s*[:\-]?\s*[0-9\s]{10,40}",
            upper
        ):
            return True

        if re.search(
            r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
            upper
        ):
            return True

        for marker in self.address_markers:
            if marker in upper and re.search(r"\d", upper):
                return True

        administrative = [
            "SIEGE SOCIAL",
            "SLEGO SOCIAL",
            "SLÈGE SOCIAL",
            "TELEPHONE",
            "FAX",
            "CAPITAL",
            "PATENTE",
            "CNSS",
            "SARL",
            "R.C.",
            "RC:",
            "IF:",
            "I.F.",
        ]

        for marker in administrative:
            if marker in upper:
                return True

        return False

    def clean_designation(self, designation):
        designation = self.normalize_text(designation)

        if not designation:
            return ""

        designation = designation.replace(" ,", ",")
        designation = designation.replace(" .", ".")
        designation = designation.replace("( ", "(")
        designation = designation.replace(" )", ")")

        designation = re.sub(
            r"^[\s\\\-=:;.,_]+",
            "",
            designation
        )

        designation = re.sub(r"\s{2,}", " ", designation)

        return designation.strip()

    def is_pure_numeric_value(self, text):
        if not text:
            return False

        text = self.normalize_text(text)

        cleaned = (
            text
            .replace("DHS", "")
            .replace("DH", "")
            .replace("MAD", "")
            .replace("%", "")
            .strip()
        )

        return bool(
            re.fullmatch(
                r"[-+]?\d+(?:[.,]\d+)?",
                cleaned
            )
        )

    def add_designation_text(
        self,
        designation_parts,
        text,
        reference=""
    ):
        text = self.normalize_text(text)

        if not text:
            return

        if self.is_footer_text(text):
            return

        if self.is_supplier_noise(text):
            return

        if reference and text.upper() == reference.upper():
            return

        if self.is_pure_numeric_value(text):
            return

        extracted_ref = self.extract_reference_from_text(text)

        if extracted_ref:
            escaped_ref = re.escape(extracted_ref)

            text = re.sub(
                rf"^{escaped_ref}\s*[-=:]?\s*",
                "",
                text,
                count=1,
                flags=re.IGNORECASE
            )

            text = self.normalize_text(text)

        if text:
            designation_parts.append(text)

    def to_float(self, text):
        if text is None:
            return None

        text = self.normalize_text(text).upper()

        text = (
            text
            .replace("DHS", "")
            .replace("DH", "")
            .replace("MAD", "")
            .replace("%", "")
            .strip()
        )

        if not text:
            return None

        if re.fullmatch(r"\d+:\d{1,2}", text):
            text = text.replace(":", ".")

        text = text.replace(" ", "")

        if "," in text and "." in text:
            if text.rfind(",") > text.rfind("."):
                text = text.replace(".", "").replace(",", ".")
            else:
                text = text.replace(",", "")
        else:
            text = text.replace(",", ".")

        try:
            return float(text)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def is_valid_quantity(value):
        return value is not None and 0 < value < 10000

    @staticmethod
    def is_valid_price(value):
        return value is not None and value >= 0

    @staticmethod
    def is_valid_tva(value):
        return value is not None and 0 <= value <= 100

    def is_reference(self, text):
        if not text:
            return False

        text = self.normalize_text(text)
        text = text.replace("=", "").replace(":", "").strip()

        if not text or len(text.split()) > 1:
            return False

        compact = text.replace(" ", "")

        if re.fullmatch(r"\d+(?:[.,]\d+)?", compact):
            return False

        if not re.fullmatch(
            r"[A-Z0-9._/\\-]+",
            compact,
            re.IGNORECASE
        ):
            return False

        if not re.search(r"[A-Z]", compact, re.IGNORECASE):
            return False

        if not re.search(r"\d", compact):
            return False

        if len(compact) < 4 or len(compact) > 50:
            return False

        return True

    def extract_reference_from_text(self, text):
        text = self.normalize_text(text)

        if not text:
            return ""

        if self.is_reference(text):
            return text.upper()

        patterns = [
            r"^([A-Z]{2,}-[A-Z0-9]+)(?:[-=: ]+)(.+)$",
            r"^([A-Z][0-9]+-[0-9A-Z]+)(?:[-=: ]+)(.+)$",
            r"^([A-Z]{3,}[0-9]+[A-Z0-9]*)(?:[-=: ]+)(.+)$",
        ]

        for pattern in patterns:
            match = re.match(
                pattern,
                text,
                re.IGNORECASE
            )

            if not match:
                continue

            reference = match.group(1).upper()

            if self.is_reference(reference):
                return reference

        return ""

    def split_reference(self, text):
        text = self.normalize_text(text)

        if not text:
            return "", ""

        patterns = [
            r"^([A-Z]{2,}-[A-Z0-9]+)(?:[-=:]+)(.+)$",
            r"^([A-Z][0-9]+-[0-9A-Z]+)(?:[-=:]+)(.+)$",
            r"^([A-Z]{3,}[0-9]+[A-Z0-9]*)(?:[-=:]+)(.+)$",
        ]

        for pattern in patterns:
            match = re.match(
                pattern,
                text,
                re.IGNORECASE
            )

            if not match:
                continue

            reference = match.group(1).upper()

            if self.is_reference(reference):
                return (
                    reference,
                    self.clean_designation(match.group(2))
                )

        first = text.split()[0].strip("=:")
        
        if self.is_reference(first):
            remaining = text[len(first):]

            return (
                first.upper(),
                self.clean_designation(remaining)
            )

        return "", self.clean_designation(text)

    def get_explicit_reference(self, ligne):
        for cellule in ligne:
            if not isinstance(cellule, dict):
                continue

            column = self.normalize_column(
                cellule.get("column", "")
            )

            if column == "REFERENCE":
                text = self.normalize_text(
                    cellule.get("text", "")
                )

                if self.is_reference(text):
                    return text.upper()

            detected = cellule.get("detected_reference")

            if detected:
                detected = self.normalize_text(detected)

                if self.is_reference(detected):
                    return detected.upper()

        return ""

    @staticmethod
    def normalize_linebuilder_group(group):
        if not isinstance(group, dict):
            return group, ""

        elements = group.get("elements", [])

        forced_reference = (
            group.get("reference") or ""
        )

        return (
            elements,
            str(forced_reference).strip().upper()
        )

    def get_cell_x(self, cellule):
        if not isinstance(cellule, dict):
            return 0.0

        if cellule.get("x") is not None:
            try:
                return float(cellule.get("x"))
            except (ValueError, TypeError):
                pass

        box = cellule.get("box", [0, 0, 0, 0])

        if isinstance(box, (list, tuple)) and len(box) >= 4:
            try:
                return (float(box[0]) + float(box[2])) / 2
            except (ValueError, TypeError):
                return 0.0

        return 0.0

    def extract_amount_from_cell(self, cellule):
        if not isinstance(cellule, dict):
            return None

        text = self.normalize_text(
            cellule.get("text", "")
        )

        if not text:
            return None

        value = self.to_float(text)

        if value is not None:
            return value

        matches = re.findall(
            r"\d+(?:[.,]\d{1,2})?",
            text
        )

        if not matches:
            return None

        values = []

        for match in matches:
            try:
                value = float(match.replace(",", "."))

                if value >= 0:
                    values.append(value)
            except ValueError:
                continue

        return values[-1] if values else None

    def get_numeric_value(self, cellule):
        if not isinstance(cellule, dict):
            return None

        texte = self.normalize_text(
            cellule.get("text", "")
        )

        return self.to_float(texte)

    def is_plausible_line_total(
        self,
        total,
        quantity,
        unit_price,
        tva=None
    ):
        if total is None:
            return False

        if quantity is None or unit_price is None:
            return True

        if quantity <= 0 or unit_price < 0:
            return False

        expected_ht = quantity * unit_price

        if abs(total - expected_ht) <= self.tolerance:
            return True

        if tva is not None:
            expected_ttc = expected_ht * (1 + tva / 100)

            if abs(total - expected_ttc) <= self.tolerance:
                return True

        return False

    def find_line_total(
        self,
        ligne,
        quantity=None,
        unit_price=None,
        tva=None,
        existing_total=None
    ):
        candidates = []

        if (
            existing_total is not None
            and self.is_valid_price(existing_total)
            and self.is_plausible_line_total(
                existing_total,
                quantity,
                unit_price,
                tva
            )
        ):
            return round(existing_total, 2)

        for cellule in ligne:
            if not isinstance(cellule, dict):
                continue

            column = cellule.get("column", "")

            if not self.is_total_column(column):
                continue

            value = self.extract_amount_from_cell(cellule)

            if value is None or not self.is_valid_price(value):
                continue

            score = 100

            if self.is_plausible_line_total(
                value,
                quantity,
                unit_price,
                tva
            ):
                score += 100
            else:
                score -= 80

            candidates.append({
                "value": value,
                "score": score,
                "x": self.get_cell_x(cellule)
            })

        for cellule in ligne:
            if not isinstance(cellule, dict):
                continue

            text = self.normalize_text(
                cellule.get("text", "")
            ).upper()

            if not text:
                continue

            if "TOTAL" not in text and "MONTANT" not in text:
                continue

            value = self.extract_amount_from_cell(cellule)

            if value is None:
                continue

            score = 90

            if self.is_plausible_line_total(
                value,
                quantity,
                unit_price,
                tva
            ):
                score += 100
            else:
                score -= 80

            candidates.append({
                "value": value,
                "score": score,
                "x": self.get_cell_x(cellule)
            })

        for cellule in ligne:
            if not isinstance(cellule, dict):
                continue

            text = self.normalize_text(
                cellule.get("text", "")
            )

            if not text:
                continue

            if not re.fullmatch(
                r"\s*\d+(?:[.,]\d+)?\s*",
                text
            ):
                continue

            value = self.to_float(text)

            if value is None:
                continue

            if (
                quantity is not None
                and abs(value - quantity) <= self.tolerance
            ):
                continue

            if (
                unit_price is not None
                and abs(value - unit_price) <= self.tolerance
            ):
                continue

            if (
                quantity is not None
                and unit_price is not None
                and not self.is_plausible_line_total(
                    value,
                    quantity,
                    unit_price,
                    tva
                )
            ):
                continue

            score = 10

            if self.is_plausible_line_total(
                value,
                quantity,
                unit_price,
                tva
            ):
                score += 100

            candidates.append({
                "value": value,
                "score": score,
                "x": self.get_cell_x(cellule)
            })

        if candidates:
            candidates.sort(
                key=lambda candidate: (
                    -candidate["score"],
                    -candidate["x"]
                )
            )

            best = candidates[0]

            if (
                quantity is not None
                and unit_price is not None
            ):
                if self.is_plausible_line_total(
                    best["value"],
                    quantity,
                    unit_price,
                    tva
                ):
                    return round(best["value"], 2)
            else:
                return round(best["value"], 2)

        if (
            quantity is not None
            and unit_price is not None
        ):
            return round(quantity * unit_price, 2)

        return None

    def recover_missing_numeric_fields(
        self,
        ligne,
        article
    ):
        numeric_candidates = []

        for cellule in ligne:
            if not isinstance(cellule, dict):
                continue

            texte = self.normalize_text(
                cellule.get("text", "")
            )

            if not texte:
                continue

            value = self.to_float(texte)

            if value is None:
                continue

            colonne = self.normalize_column(
                cellule.get("column", "")
            )

            numeric_candidates.append({
                "value": value,
                "column": colonne,
                "x": self.get_cell_x(cellule),
                "element": cellule
            })

        if article["quantite"] is None:
            quantity_candidates = []

            for candidate in numeric_candidates:
                value = candidate["value"]

                if not float(value).is_integer():
                    continue

                if not self.is_valid_quantity(value):
                    continue

                if self.is_quantity_column(candidate["column"]):
                    quantity_candidates.append(candidate)

            if quantity_candidates:
                quantity_candidates.sort(
                    key=lambda item: item["x"]
                )

                article["quantite"] = int(
                    quantity_candidates[0]["value"]
                )

        if article["prix_unitaire"] is None:
            price_candidates = []

            for candidate in numeric_candidates:
                value = candidate["value"]

                if not self.is_valid_price(value):
                    continue

                if self.is_unit_price_column(candidate["column"]):
                    price_candidates.append(candidate)

            if price_candidates:
                price_candidates.sort(
                    key=lambda item: item["x"]
                )

                article["prix_unitaire"] = (
                    price_candidates[0]["value"]
                )

        if article["tva"] is None:
            tva_candidates = []

            for candidate in numeric_candidates:
                value = candidate["value"]

                if not self.is_valid_tva(value):
                    continue

                if self.is_tva_column(candidate["column"]):
                    tva_candidates.append(candidate)

            if tva_candidates:
                tva_candidates.sort(
                    key=lambda item: item["x"]
                )

                article["tva"] = (
                    tva_candidates[0]["value"]
                )

        if article["total"] is None:
            total = self.find_line_total(
                ligne=ligne,
                quantity=article["quantite"],
                unit_price=article["prix_unitaire"],
                tva=article["tva"],
                existing_total=None
            )

            if total is not None:
                article["total"] = total

        if (
            article["quantite"] is None
            and article["prix_unitaire"] is not None
            and article["total"] is not None
        ):
            unit_price = article["prix_unitaire"]
            total = article["total"]

            if unit_price > 0:
                recovered_quantity = total / unit_price

                if (
                    recovered_quantity > 0
                    and recovered_quantity.is_integer()
                    and self.is_valid_quantity(
                        recovered_quantity
                    )
                ):
                    article["quantite"] = int(
                        recovered_quantity
                    )

        return article

    def remove_supplier_noise(self, text):
        if not text:
            return ""

        text = self.normalize_text(text)

        text = re.sub(
            r"\b(?:0[5-7]\d{8}|\+212[5-7]\d{8})\b",
            " ",
            text,
            flags=re.IGNORECASE
        )

        text = re.sub(
            r"\b0[5-7](?:\s*\d){8}\b",
            " ",
            text,
            flags=re.IGNORECASE
        )

        text = re.sub(
            r"\b(?:ICE|1CE)\s*[:\-]?\s*\d{10,20}\b",
            " ",
            text,
            flags=re.IGNORECASE
        )

        text = re.sub(
            r"\bRIB\s*[:\-]?\s*[0-9\s]{10,40}",
            " ",
            text,
            flags=re.IGNORECASE
        )

        text = re.sub(
            r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
            " ",
            text,
            flags=re.IGNORECASE
        )

        noise_patterns = [
            r"\bSIEGE\s+SOCIAL\b.*",
            r"\bSLEGO\s+SOCIAL\b.*",
            r"\bSLÈGE\s+SOCIAL\b.*",
            r"\bTELEPHONE\b.*",
            r"\bTEL\b\s*[:\-]?.*",
            r"\bFAX\b\s*[:\-]?.*",
            r"\bEMAIL\b\s*[:\-]?.*",
            r"\bE[- ]?MAIL\b\s*[:\-]?.*",
            r"\bSARL\b.*",
            r"\bRC\b\s*[:\-]?\s*\d+.*",
            r"\bPATENTE\b.*",
            r"\bC\.?N\.?S\.?S\.?\b.*",
        ]

        for pattern in noise_patterns:
            text = re.sub(
                pattern,
                " ",
                text,
                flags=re.IGNORECASE
            )

        return re.sub(r"\s+", " ", text).strip()

    def parse_line(self, ligne, forced_reference=""):
        article = {
            "reference": "",
            "designation": "",
            "quantite": None,
            "prix_unitaire": None,
            "tva": None,
            "total": None
        }

        if not ligne:
            return article

        designation_parts = []

        explicit_reference = (
            forced_reference
            or self.get_explicit_reference(ligne)
        )

        if explicit_reference:
            article["reference"] = explicit_reference.upper()

        for cellule in ligne:
            if not isinstance(cellule, dict):
                continue

            colonne = self.normalize_column(
                cellule.get("column", "")
            )

            texte = self.normalize_text(
                cellule.get("text", "")
            )

            if not texte:
                continue

            if self.is_footer_text(texte):
                continue

            if colonne == "REFERENCE":
                if self.is_reference(texte):
                    if not article["reference"]:
                        article["reference"] = texte.upper()
                    continue

                extracted_ref = self.extract_reference_from_text(texte)

                if extracted_ref:
                    if not article["reference"]:
                        article["reference"] = extracted_ref.upper()

                    self.add_designation_text(
                        designation_parts,
                        texte,
                        article["reference"]
                    )

                    continue

            if self.is_quantity_column(colonne):
                value = self.to_float(texte)

                if (
                    self.is_valid_quantity(value)
                    and article["quantite"] is None
                ):
                    article["quantite"] = (
                        int(value)
                        if value.is_integer()
                        else value
                    )

                continue

            if self.is_unit_price_column(colonne):
                value = self.to_float(texte)

                if (
                    self.is_valid_price(value)
                    and article["prix_unitaire"] is None
                ):
                    article["prix_unitaire"] = value

                continue

            if self.is_tva_column(colonne):
                value = self.to_float(texte)

                if (
                    self.is_valid_tva(value)
                    and article["tva"] is None
                ):
                    article["tva"] = value

                continue

            if self.is_total_column(colonne):
                value = self.extract_amount_from_cell(cellule)

                if (
                    self.is_valid_price(value)
                    and article["total"] is None
                ):
                    article["total"] = value

                continue

            if colonne in {
                "DESIGNATION",
                "DESCRIPTION",
                "ARTICLE",
                "LIBELLE",
                "LIBELLEARTICLE",
                "PRODUIT",
                "ITEM",
                "UNKNOWN",
                "",
            }:
                self.add_designation_text(
                    designation_parts,
                    texte,
                    article["reference"]
                )

                continue

            has_letters = bool(
                re.search(
                    r"[A-ZÀ-ÿ]",
                    texte,
                    re.IGNORECASE
                )
            )

            is_numeric = bool(
                re.fullmatch(
                    r"[\d\s,.:]+",
                    texte
                )
            )

            if has_letters and not is_numeric:
                self.add_designation_text(
                    designation_parts,
                    texte,
                    article["reference"]
                )

        designation = self.clean_designation(
            " ".join(designation_parts)
        )

        if not article["reference"]:
            for cellule in ligne:
                if not isinstance(cellule, dict):
                    continue

                texte_cellule = self.normalize_text(
                    cellule.get("text", "")
                )

                if not texte_cellule:
                    continue

                if self.is_reference(texte_cellule):
                    article["reference"] = texte_cellule.upper()
                    break

                extracted_ref = self.extract_reference_from_text(
                    texte_cellule
                )

                if extracted_ref:
                    article["reference"] = extracted_ref.upper()
                    break

        if not article["reference"]:
            ref, des = self.split_reference(designation)

            article["reference"] = ref

            if des:
                designation = des

        if article["reference"]:
            ref = re.escape(article["reference"])

            designation = re.sub(
                rf"^{ref}\s*[-=:]?\s*",
                "",
                designation,
                count=1,
                flags=re.IGNORECASE
            )

        article["designation"] = self.clean_designation(
            designation
        )

        if not article["reference"]:
            ref, des = self.split_reference(
                article["designation"]
            )

            article["reference"] = ref
            article["designation"] = des

        else:
            designation = article["designation"].strip()
            ref = re.escape(article["reference"])

            designation = re.sub(
                rf"^{ref}\s*[-=:]?\s*",
                "",
                designation,
                flags=re.IGNORECASE
            )

            article["designation"] = self.clean_designation(
                designation
            )

        article = self.recover_missing_numeric_fields(
            ligne,
            article
        )

        article["total"] = self.find_line_total(
            ligne=ligne,
            quantity=article["quantite"],
            unit_price=article["prix_unitaire"],
            tva=article["tva"],
            existing_total=article["total"]
        )

        article["designation"] = self.clean_designation(
            article["designation"]
        )

        return article

    def parse(self, lignes):
        articles = []

        for ligne in lignes or []:
            forced_reference = ""

            if isinstance(ligne, dict):
                (
                    ligne,
                    forced_reference
                ) = self.normalize_linebuilder_group(ligne)

            if not isinstance(ligne, list):
                continue

            article = self.parse_line(
                ligne,
                forced_reference=forced_reference
            )

            if (
                article["designation"]
                or article["reference"]
                or article["quantite"] is not None
                or article["prix_unitaire"] is not None
                or article["tva"] is not None
                or article["total"] is not None
            ):
                articles.append(article)

        return articles
    