from collections import defaultdict
import re


class LineBuilder:

    def __init__(self, tolerance_y=3.0):
        self.tolerance_y = tolerance_y
        self.max_reference_length = 24

        self.headers = {
            "DESIGNATION",
            "DÉSIGNATION",
            "REFERENCE",
            "RÉFÉRENCE",
            "REF",
            "RÉF",
            "ARTICLE",
            "TVA",
            "PU",
            "P.U",
            "P.U.",
            "P.U.TTC",
            "P.U TTC",
            "P.U HT",
            "PU TTC",
            "PU HT",
            "PRIX",
            "PRIX UNITAIRE",
            "PRIX UNITAIRE TTC",
            "QTE",
            "QTÉ",
            "QUANTITE",
            "QUANTITÉ",
            "TOTAL",
            "TOTAL TTC",
            "MONTANT",
            "MONTANT TTC",
            "REMISE",
        }

        self.stop_words = {
            "TOTAL HT",
            "TOTAL H.T",
            "TOTAL H T",
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
            "SOUS TOTAL HT",
            "SOUS TOTAL TTC",
            "ARRETEE LA PRESENTE FACTURE",
            "ARRÊTÉE LA PRÉSENTE FACTURE",
            "MODE DE REGLEMENT",
            "MODE DE RÈGLEMENT",
        }

        self.reference_blacklist_prefixes = (
            "FAX",
            "TEL",
            "TELEPHONE",
            "ICE",
            "IF",
            "RC",
            "CNSS",
            "RIB",
            "PATENTE",
        )

        self.forbidden_references = {
            "ARTICLE",
            "TOTAL",
            "REFERENCE",
            "REF",
            "DESIGNATION",
            "DESCRIPTION",
            "QUANTITE",
            "QTE",
            "TVA",
            "PRIX",
            "PU",
            "PUTTC",
            "PUHT",
            "MONTANT",
            "REMISE",
            "CARTOUCHE",
            "TONER",
            "BLACK",
            "CYAN",
            "MAGENTA",
            "YELLOW",
        }

        self.reference_patterns = (
            r"^[A-Z]{2,}-[A-Z0-9]+$",
            r"^[A-Z]+[0-9]+[A-Z0-9]*$",
            r"^[A-Z]{3,}[0-9]+[A-Z0-9]*$",
            r"^[A-Z0-9]+/[A-Z0-9]+$",
            r"^[A-Z0-9]+-[A-Z0-9]+$",
            r"^[A-Z0-9]+_[A-Z0-9]+$",
            r"^[0-9]+-[A-Z0-9]+$",
            r"^[A-Z0-9]+\.[A-Z0-9]+$",
        )

    # ------------------------------------------------------------------
    # Normalisation
    # ------------------------------------------------------------------

    def normalize(self, text):
        if text is None:
            return ""

        text = str(text).upper().strip()

        replacements = {
            "É": "E",
            "È": "E",
            "Ê": "E",
            "Ë": "E",
            "À": "A",
            "Â": "A",
            "Ç": "C",
            "Ù": "U",
            "Û": "U",
            "Ô": "O",
            "Ö": "O",
            "Î": "I",
            "Ï": "I",
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        return re.sub(r"\s+", " ", text).strip()

    def compact(self, text):
        return re.sub(r"[^A-Z0-9]", "", self.normalize(text))

    # ------------------------------------------------------------------
    # Headers et fin de tableau
    # ------------------------------------------------------------------

    def is_header(self, text):
        normalized = self.normalize(text)

        if normalized in self.headers:
            return True

        return self.compact(normalized) in {
            "REFERENCE",
            "REF",
            "DESIGNATION",
            "DESCRIPTION",
            "ARTICLE",
            "QUANTITE",
            "QTE",
            "TVA",
            "PU",
            "PUTTC",
            "PUHT",
            "PRIX",
            "PRIXUNITAIRE",
            "PRIXUNITAIRETTC",
            "TOTAL",
            "TOTALTTC",
            "MONTANT",
            "MONTANTTTC",
        }

    def is_stop(self, text):
        text = self.normalize(text)

        if not text:
            return False

        if text in {
            self.normalize(word)
            for word in self.stop_words
        }:
            return True

        compact = self.compact(text)

        if compact in {
            "TOTALHT",
            "TOTALHTT",
            "TOTALTVA",
            "TOTALTTC",
            "NETAPAYER",
            "NETAPAYE",
            "APAYER",
            "SOUSTOTAL",
            "SOUSTOTALHT",
            "SOUSTOTALTTC",
            "ARRETEELAPRESENTEFACTURE",
            "MODEDEREGLEMENT",
        }:
            return True

        if re.search(
            r"\bTOTAL\s+(?:H\s*\.?\s*T|T\s*\.?\s*C|TVA)\b",
            text,
        ):
            return True

        if re.search(r"\bNET\s+A\s+PAYER\b", text):
            return True

        if re.search(r"\bSOUS[-\s]+TOTAL\b", text):
            return True

        return False

    # ------------------------------------------------------------------
    # Géométrie
    # ------------------------------------------------------------------

    def get_y(self, element):
        if element.get("y") is not None:
            return float(element["y"])

        box = element.get("box", [0, 0, 0, 0])

        return (box[1] + box[3]) / 2

    def get_x(self, element):
        if element.get("x") is not None:
            return float(element["x"])

        box = element.get("box", [0, 0, 0, 0])

        return (box[0] + box[2]) / 2

    def get_global_column_x(self, elements, column):
        values = [
            self.get_x(element)
            for element in elements
            if element.get("column") == column
        ]

        if not values:
            return None

        return sum(values) / len(values)

    def get_numeric_boundaries(self, elements):
        return {
            "qte": self.get_global_column_x(elements, "qte"),
            "pu": self.get_global_column_x(elements, "pu"),
            "total": self.get_global_column_x(elements, "total"),
        }

    # ------------------------------------------------------------------
    # Références
    # ------------------------------------------------------------------

    def is_reference(self, text):
        if not text:
            return False

        text = self.normalize(text)

        if not text or len(text.split()) > 1:
            return False

        if len(text) > self.max_reference_length:
            return False

        if "%" in text:
            return False

        if not re.fullmatch(r"[A-Z0-9][A-Z0-9._/\\-]*", text):
            return False

        if any(
            text.startswith(prefix)
            for prefix in self.reference_blacklist_prefixes
        ):
            return False

        if text in self.forbidden_references:
            return False

        if not re.search(r"\d", text):
            return False

        if re.fullmatch(r"\d+(?:[.,]\d+)?", text):
            return False

        if re.fullmatch(r"\d+[.,]\d{1,4}", text):
            return False

        return any(
            re.fullmatch(pattern, text)
            for pattern in self.reference_patterns
        )

    def extract_reference_from_text(self, text):
        if not text:
            return None

        text = self.normalize(text)

        if not text:
            return None

        if self.is_reference(text):
            return text

        patterns = (
            r"^([A-Z]{2,}-[A-Z0-9]+)\s*(?:[-=:])\s*(.+)$",
            r"^([A-Z]+[0-9]+[A-Z0-9]*)\s*(?:[-=:])\s*(.+)$",
            r"^([A-Z]{3,}[0-9]+[A-Z0-9]*)\s+(.+)$",
        )

        for pattern in patterns:
            match = re.match(pattern, text)

            if not match:
                continue

            candidate = self.normalize(match.group(1))

            if self.is_reference(candidate):
                return candidate

        first_token = re.sub(
            r"^[^\w]+|[^\w]+$",
            "",
            text.split()[0],
        )

        if self.is_reference(first_token):
            return first_token

        return None

    def remove_reference_from_designation(self, text, reference):
        text = self.normalize(text)

        if not text or not reference:
            return text

        reference = self.normalize(reference)

        if not text.startswith(reference):
            return text

        remaining = text[len(reference):]

        remaining = re.sub(
            r"^\s*[-=:]+\s*",
            "",
            remaining,
        )

        return remaining.strip()

    def get_row_reference(self, row):
        for element in row:
            if element.get("column") != "reference":
                continue

            text = self.normalize(element.get("text", ""))

            if self.is_reference(text):
                return text

        for element in row:
            column = element.get("column", "")

            if column not in {"", "designation"}:
                continue

            reference = self.extract_reference_from_text(
                element.get("text", "")
            )

            if reference:
                return reference

        return None

    def find_reference_elements(self, elements):
        references = []

        for element in elements:
            if element.get("column") != "reference":
                continue

            text = self.normalize(element.get("text", ""))

            if not self.is_reference(text):
                continue

            reference_element = element.copy()
            reference_element["detected_reference"] = text

            references.append(reference_element)

        return references

    # ------------------------------------------------------------------
    # Nettoyage des éléments
    # ------------------------------------------------------------------

    def deduplicate_elements(self, elements):
        unique = []
        seen = set()

        for element in elements:
            key = (
                self.normalize(element.get("text", "")),
                round(self.get_x(element), 1),
                round(self.get_y(element), 1),
                element.get("column", ""),
            )

            if key in seen:
                continue

            seen.add(key)
            unique.append(element)

        return unique

    def clean_article_elements(self, elements, reference):
        cleaned = []

        for element in elements:
            element = element.copy()

            column = element.get("column", "")
            text = self.normalize(element.get("text", ""))

            if column == "reference":
                continue

            if column == "designation":
                text = self.remove_reference_from_designation(
                    text,
                    reference,
                )

                if not text:
                    continue

                element["text"] = text

            cleaned.append(element)

        return cleaned

    # ------------------------------------------------------------------
    # Désignations du nouveau format
    # ------------------------------------------------------------------

    def is_valid_new_format_designation(
        self,
        element,
        article_elements,
        boundaries=None,
    ):
        if element.get("column") != "designation":
            return True

        text = self.normalize(element.get("text", ""))

        if not text or len(text) <= 1:
            return False

        if not re.search(r"[A-Z]", text):
            return False

        if boundaries:
            qte_x = boundaries.get("qte")

            if qte_x is not None:
                if self.get_x(element) >= qte_x - 10:
                    return False

        return True

    def clean_new_format_designations(self, elements):
        if not elements:
            return []

        qte_elements = [
            element
            for element in elements
            if element.get("column") == "qte"
        ]

        qte_x = None

        if qte_elements:
            qte_x = min(
                self.get_x(element)
                for element in qte_elements
            )

        cleaned = []

        for element in elements:
            element = element.copy()

            column = element.get("column", "")
            text = self.normalize(element.get("text", ""))

            if column == "designation":
                if not text or len(text) <= 1:
                    continue

                if qte_x is not None:
                    if self.get_x(element) >= qte_x - 10:
                        continue

                if not re.search(r"[A-Z]", text):
                    continue

                element["text"] = text

            cleaned.append(element)

        return cleaned

    def merge_designation_elements(self, elements):
        if not elements:
            return elements

        designation_elements = [
            element
            for element in elements
            if element.get("column") == "designation"
        ]

        if len(designation_elements) <= 1:
            return elements

        designation_elements.sort(
            key=lambda element: (
                self.get_y(element),
                self.get_x(element),
            )
        )

        parts = [
            self.normalize(element.get("text", ""))
            for element in designation_elements
        ]

        parts = [part for part in parts if part]

        if not parts:
            return elements

        merged = designation_elements[0].copy()
        merged["text"] = " ".join(parts)

        result = []
        inserted = False

        for element in elements:
            if element.get("column") != "designation":
                result.append(element)
                continue

            if not inserted:
                result.append(merged)
                inserted = True

        return result

    # ------------------------------------------------------------------
    # Association des éléments aux articles
    # ------------------------------------------------------------------

    def find_best_article(self, element, articles):
        if not articles:
            return None

        y = self.get_y(element)

        for article in articles:
            start_y = article.get(
                "start_y",
                article["reference_y"] - 3,
            )

            end_y = article.get(
                "end_y",
                float("inf"),
            )

            if start_y <= y < end_y:
                return article

        candidates = [
            article
            for article in articles
            if article["reference_y"] <= y
        ]

        if not candidates:
            return None

        best = candidates[-1]

        if abs(y - best["reference_y"]) <= 35:
            return best

        return None

    # ------------------------------------------------------------------
    # Construction principale
    # ------------------------------------------------------------------

    def build(self, classified):
        if not classified:
            return []

        elements = []

        for source in classified:
            text = self.normalize(source.get("text", ""))

            if not text:
                continue

            if self.is_header(text):
                continue

            if (
                source.get("x") is None
                and source.get("box") is None
            ):
                continue

            element = source.copy()
            element["x"] = self.get_x(element)
            element["y"] = self.get_y(element)

            elements.append(element)

        if not elements:
            return []

        boundaries = self.get_numeric_boundaries(elements)

        reference_elements = self.find_reference_elements(elements)

        if not reference_elements:
            return self.build_old_format(elements)

        reference_elements.sort(
            key=self.get_y
        )

        articles = []

        for ref_element in reference_elements:
            reference = ref_element.get("detected_reference")

            if not reference:
                reference = self.normalize(
                    ref_element.get("text", "")
                )

            reference_y = self.get_y(ref_element)

            duplicate = any(
                article["reference"] == reference
                and abs(
                    article["reference_y"] - reference_y
                ) <= self.tolerance_y
                for article in articles
            )

            if duplicate:
                continue

            articles.append({
                "reference": reference,
                "reference_y": reference_y,
                "elements": [],
            })

        if not articles:
            return self.build_old_format(elements)

        stop_y = float("inf")

        for element in elements:
            if not self.is_stop(
                element.get("text", "")
            ):
                continue

            stop_y = min(
                stop_y,
                self.get_y(element),
            )

        for index, article in enumerate(articles):
            article["start_y"] = (
                article["reference_y"] - 3
            )

            if index < len(articles) - 1:
                article["end_y"] = (
                    articles[index + 1]["reference_y"]
                )
            else:
                article["end_y"] = stop_y

                if stop_y == float("inf"):
                    article["end_y"] = (
                        article["reference_y"] + 80
                    )

        for element in elements:
            text = self.normalize(
                element.get("text", "")
            )

            if self.is_stop(text):
                if element.get("column") not in {
                    "designation",
                    "reference",
                }:
                    continue

            if element.get("column") == "reference":
                continue

            y = self.get_y(element)
            assigned = False

            for article in articles:
                if not (
                    article["start_y"]
                    <= y
                    < article["end_y"]
                ):
                    continue

                if element.get("column") == "designation":
                    if not self.is_valid_new_format_designation(
                        element,
                        article["elements"],
                        boundaries,
                    ):
                        continue

                article["elements"].append(element)
                assigned = True
                break

            if assigned:
                continue

            if element.get("column") == "designation":
                if not self.is_valid_new_format_designation(
                    element,
                    [],
                    boundaries,
                ):
                    continue

            best = self.find_best_article(
                element,
                articles,
            )

            if not best:
                continue

            if abs(
                y - best["reference_y"]
            ) <= max(
                35,
                self.tolerance_y * 2,
            ):
                best["elements"].append(element)

        result = []

        for article in articles:
            elements_article = self.deduplicate_elements(
                article["elements"]
            )

            elements_article = self.clean_article_elements(
                elements_article,
                article["reference"],
            )

            elements_article = self.clean_new_format_designations(
                elements_article
            )

            elements_article = self.merge_designation_elements(
                elements_article
            )

            elements_article.sort(
                key=lambda element: (
                    self.get_y(element),
                    self.get_x(element),
                )
            )

            result.append({
                "reference": article["reference"],
                "reference_y": article["reference_y"],
                "elements": elements_article,
            })

        return result

    # ------------------------------------------------------------------
    # Construction ancien format
    # ------------------------------------------------------------------

    def build_old_format(self, elements):
        if not elements:
            return []

        rows = defaultdict(list)

        for element in elements:
            y = self.get_y(element)
            key = round(y / self.tolerance_y)
            rows[key].append(element)

        grouped = []

        for _, row in sorted(rows.items()):
            row.sort(key=self.get_x)
            grouped.append(row)

        articles = []
        current_article = None

        for row in grouped:
            if not row:
                continue

            text = " ".join(
                self.normalize(
                    element.get("text", "")
                )
                for element in row
            )

            if self.is_stop(text):
                if current_article is not None:
                    articles.append(current_article)
                    current_article = None
                break

            reference = self.get_row_reference(row)

            if reference:
                if current_article is not None:
                    articles.append(current_article)

                reference_y = self.get_y(row[0])

                for element in row:
                    extracted = self.extract_reference_from_text(
                        element.get("text", "")
                    )

                    if extracted == reference:
                        reference_y = self.get_y(element)
                        break

                current_article = {
                    "reference": reference,
                    "reference_y": reference_y,
                    "elements": row.copy(),
                }

                continue

            if current_article is not None:
                current_article["elements"].extend(row)

        if current_article is not None:
            articles.append(current_article)

        result = []

        for article in articles:
            reference = article["reference"]

            elements_article = self.deduplicate_elements(
                article["elements"]
            )

            elements_article = self.clean_article_elements(
                elements_article,
                reference,
            )

            elements_article.sort(
                key=lambda element: (
                    self.get_y(element),
                    self.get_x(element),
                )
            )

            result.append({
                "reference": reference,
                "reference_y": article["reference_y"],
                "elements": elements_article,
            })

        return result

    # ------------------------------------------------------------------
    # Format d'un article
    # ------------------------------------------------------------------

    def format_article(self, elements):
        if not elements:
            return {
                "reference": None,
                "elements": [],
            }

        reference = self.get_row_reference(elements)

        elements = self.clean_article_elements(
            elements,
            reference,
        )

        return {
            "reference": reference,
            "elements": elements,
        }
    