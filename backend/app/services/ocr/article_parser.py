
import re

class ArticleParser:
    """
    Parse les lignes construites par LineBuilder afin de produire
    des articles propres.

    Responsabilités :
        - extraire référence
        - extraire désignation
        - extraire quantité
        - extraire prix unitaire
        - extraire TVA
        - extraire total ligne
        - récupérer certains champs explicitement classifiés
          mais non récupérés lors du premier passage
        - éliminer les textes footer / fournisseur évidents

    Architecture :

        OCR
          ↓
        ColumnDetector
          ↓
        LineBuilder
          ↓
        ArticleParser
          ↓
        FactureParser
          ↓
        InvoiceValidator
    """

    def __init__(self, tolerance=0.05):

        self.tolerance = tolerance

        # =========================================================
        # REFERENCE
        # =========================================================

        self.reference_pattern = re.compile(
            r"^[A-Z0-9._/\\-]+$",
            re.IGNORECASE
        )

        # =========================================================
        # FOOTER
        # =========================================================

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
            "MODE DE REGLEMENT",
            "ARRETEE LA PRESENTE FACTURE",
            "ARRÊTÉE LA PRÉSENTE FACTURE",
            "TOTAL GENERAL",
            "TOTAL GENERAL TTC",
            "TOTAL GENERAL HT",
        ]

        # =========================================================
        # FOURNISSEUR / INFORMATIONS ADMINISTRATIVES
        # =========================================================

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

        # =========================================================
        # BRUIT D'ADRESSE
        # =========================================================

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

        # =========================================================
        # COLONNES POSSIBLES
        # =========================================================

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

    # =============================================================
    # NORMALISATION TEXTE
    # =============================================================

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

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    # =============================================================
    # NORMALISATION COLONNE
    # =============================================================

    def normalize_column(self, column):

        if not column:
            return ""

        column = self.normalize_text(column).upper()

        # OCR fréquentes
        column = column.replace(
            "MONANT",
            "MONTANT"
        )

        column = column.replace(
            "MONTAT",
            "MONTANT"
        )

        column = column.replace(
            "TOTAl",
            "TOTAL"
        )

        # Supprimer ponctuation / espaces
        column = re.sub(
            r"[^A-Z0-9]",
            "",
            column
        )

        return column

    # =============================================================
    # TYPE DE COLONNE
    # =============================================================

    def is_quantity_column(self, column):

        normalized = self.normalize_column(column)

        return normalized in self.quantity_columns

    # -------------------------------------------------------------

    def is_unit_price_column(self, column):

        normalized = self.normalize_column(column)

        return normalized in self.unit_price_columns

    # -------------------------------------------------------------

    def is_tva_column(self, column):

        normalized = self.normalize_column(column)

        return normalized in self.tva_columns

    # -------------------------------------------------------------

    def is_total_column(self, column):

        normalized = self.normalize_column(column)

        return normalized in self.total_columns

    # =============================================================
    # DUPLICATES
    # =============================================================

    @staticmethod
    def remove_duplicate_words(text):

        words = text.split()

        result = []

        for word in words:

            if (
                not result
                or result[-1].upper() != word.upper()
            ):
                result.append(word)

        return " ".join(result)

    # =============================================================
    # FOOTER DETECTION
    # =============================================================

    def is_footer_text(self, text):

        text = self.normalize_text(text)

        if not text:
            return False

        upper = text.upper()

        # ---------------------------------------------------------
        # Marqueurs de footer
        # ---------------------------------------------------------

        for marker in self.footer_markers:

            if marker in upper:
                return True

        # ---------------------------------------------------------
        # Informations administratives
        # ---------------------------------------------------------

        for marker in self.footer_text_markers:

            if marker in upper:
                return True

        return False

    # =============================================================
    # FOURNISSEUR / ADRESSE
    # =============================================================

    def is_supplier_noise(self, text):

        text = self.normalize_text(text)

        if not text:
            return False

        upper = text.upper()

        # ---------------------------------------------------------
        # Téléphone
        # ---------------------------------------------------------

        if re.search(
            r"\b0[5-7]\d{8}\b",
            upper
        ):
            return True

        if re.search(
            r"\+212\s*[5-7]\d{8}",
            upper
        ):
            return True

        # ---------------------------------------------------------
        # ICE
        # ---------------------------------------------------------

        if re.search(
            r"\b(?:ICE|1CE)\s*[:\-]?\s*\d{10,20}\b",
            upper
        ):
            return True

        # ---------------------------------------------------------
        # RIB
        # ---------------------------------------------------------

        if re.search(
            r"\bRIB\s*[:\-]?\s*[0-9\s]{10,40}",
            upper
        ):
            return True

        # ---------------------------------------------------------
        # EMAIL
        # ---------------------------------------------------------

        if re.search(
            r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
            upper
        ):
            return True

        # ---------------------------------------------------------
        # Adresse
        # ---------------------------------------------------------

        for marker in self.address_markers:

            if marker in upper:

                # Une adresse contenant un numéro
                # est très probablement du bruit fournisseur.
                if re.search(
                    r"\d",
                    upper
                ):
                    return True

        # ---------------------------------------------------------
        # Mots administratifs
        # ---------------------------------------------------------

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

    # =============================================================
    # DESIGNATION
    # =============================================================
    def clean_designation(self, designation):

        designation = self.normalize_text(designation)

        if not designation:
            return ""

        designation = designation.replace(
            " ,",
            ","
        )

        designation = designation.replace(
            " .",
            "."
        )

        designation = designation.replace(
            "( ",
            "("
        )

        designation = designation.replace(
            " )",
            ")"
        )

        designation = re.sub(
            r"^[\s\\\-=:;.,_]+",
            "",
            designation
        )

        designation = re.sub(
            r"\s{2,}",
            " ",
            designation
        )

        return designation.strip()

    # =============================================================
    # PURE NUMERIC
    # =============================================================

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

    # =============================================================
    # ADD DESIGNATION
    # =============================================================

    def add_designation_text(
        self,
        designation_parts,
        text,
        reference=""
    ):
        """
        Ajoute une cellule à la désignation.

        Ne conserve pas :
            - footer
            - téléphone
            - adresse fournisseur évidente
            - référence seule
            - valeur purement numérique

        Conserve le reste.
        """

        text = self.normalize_text(text)

        if not text:
            return

        # ---------------------------------------------------------
        # Footer
        # ---------------------------------------------------------

        if self.is_footer_text(text):
            return

        # ---------------------------------------------------------
        # Bruit fournisseur
        # ---------------------------------------------------------

        if self.is_supplier_noise(text):
            return

        # ---------------------------------------------------------
        # Référence seule
        # ---------------------------------------------------------

        if (
            reference
            and text.upper() == reference.upper()
        ):
            return

        # ---------------------------------------------------------
        # Valeur numérique seule
        # ---------------------------------------------------------

        if self.is_pure_numeric_value(text):
            return

        # ---------------------------------------------------------
        # Référence + désignation
        # ---------------------------------------------------------

        extracted_ref = self.extract_reference_from_text(
            text
        )

        if extracted_ref:

            escaped_ref = re.escape(
                extracted_ref
            )

            text = re.sub(
                rf"^{escaped_ref}\s*[-=:]?\s*",
                "",
                text,
                count=1,
                flags=re.IGNORECASE
            )

            text = self.normalize_text(text)

        if not text:
            return

        designation_parts.append(text)

    # =============================================================
    # NUMBER
    # =============================================================

    def to_float(self, text):

        if text is None:
            return None

        text = self.normalize_text(
            text
        ).upper()

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

        # OCR : 20:00 → 20.00
        if re.fullmatch(
            r"\d+:\d{1,2}",
            text
        ):
            text = text.replace(
                ":",
                "."
            )

        text = text.replace(
            " ",
            ""
        )

        # ---------------------------------------------------------
        # 1.234,56
        # ---------------------------------------------------------

        if "," in text and "." in text:

            if text.rfind(",") > text.rfind("."):

                text = (
                    text
                    .replace(".", "")
                    .replace(",", ".")
                )

            else:

                text = text.replace(
                    ",",
                    ""
                )

        # ---------------------------------------------------------
        # 123,45
        # ---------------------------------------------------------

        else:

            text = text.replace(
                ",",
                "."
            )

        try:

            return float(text)

        except (
            ValueError,
            TypeError
        ):

            return None

    # =============================================================
    # VALIDATION NUMERIQUE
    # =============================================================

    @staticmethod
    def is_valid_quantity(value):

        return (
            value is not None
            and 0 < value < 10000
        )

    # -------------------------------------------------------------

    @staticmethod
    def is_valid_price(value):

        return (
            value is not None
            and value >= 0
        )

    # -------------------------------------------------------------

    @staticmethod
    def is_valid_tva(value):

        return (
            value is not None
            and 0 <= value <= 100
        )

    # =============================================================
    # REFERENCE
    # =============================================================

    def is_reference(self, text):

        if not text:
            return False

        text = self.normalize_text(text)

        text = (
            text
            .replace("=", "")
            .replace(":", "")
            .strip()
        )

        if not text:
            return False

        # Une référence ne doit normalement
        # pas contenir plusieurs mots.
        if len(text.split()) > 1:
            return False

        compact = text.replace(
            " ",
            ""
        )

        # Pas uniquement numérique
        if re.fullmatch(
            r"\d+(?:[.,]\d+)?",
            compact
        ):
            return False

        # Caractères autorisés
        if not re.fullmatch(
            r"[A-Z0-9._/\\-]+",
            compact,
            re.IGNORECASE
        ):
            return False

        # Au moins une lettre
        if not re.search(
            r"[A-Z]",
            compact,
            re.IGNORECASE
        ):
            return False

        # Au moins un chiffre
        if not re.search(
            r"\d",
            compact
        ):
            return False

        # Taille raisonnable
        if len(compact) < 4:
            return False

        if len(compact) > 50:
            return False

        return True

    # =============================================================
    # EXTRACTION REFERENCE
    # =============================================================

    def extract_reference_from_text(
        self,
        text
    ):

        text = self.normalize_text(text)

        if not text:
            return ""

        # ---------------------------------------------------------
        # Texte entièrement référence
        # ---------------------------------------------------------

        if self.is_reference(text):

            return text.upper()

        # ---------------------------------------------------------
        # Patterns
        # ---------------------------------------------------------

        patterns = [

            # HP-F6V25AE - ...
            r"^([A-Z]{2,}-[A-Z0-9]+)"
            r"(?:[-=: ]+)(.+)$",

            # A12-123 ...
            r"^([A-Z][0-9]+-[0-9A-Z]+)"
            r"(?:[-=: ]+)(.+)$",

            # EPST103BK ...
            r"^([A-Z]{3,}[0-9]+[A-Z0-9]*)"
            r"(?:[-=: ]+)(.+)$",
        ]

        for pattern in patterns:

            match = re.match(
                pattern,
                text,
                re.IGNORECASE
            )

            if not match:
                continue

            reference = (
                match.group(1)
                .upper()
            )

            if self.is_reference(
                reference
            ):

                return reference

        return ""

    # =============================================================
    # SPLIT REFERENCE / DESIGNATION
    # =============================================================

    def split_reference(self, text):

        text = self.normalize_text(text)

        if not text:
            return "", ""

        # ---------------------------------------------------------
        # Reference + separator
        # ---------------------------------------------------------

        patterns = [

            r"^([A-Z]{2,}-[A-Z0-9]+)"
            r"(?:[-=:]+)(.+)$",

            r"^([A-Z][0-9]+-[0-9A-Z]+)"
            r"(?:[-=:]+)(.+)$",

            r"^([A-Z]{3,}[0-9]+[A-Z0-9]*)"
            r"(?:[-=:]+)(.+)$",
        ]

        for pattern in patterns:

            match = re.match(
                pattern,
                text,
                re.IGNORECASE
            )

            if not match:
                continue

            reference = (
                match.group(1)
                .upper()
            )

            if self.is_reference(
                reference
            ):

                return (
                    reference,
                    self.clean_designation(
                        match.group(2)
                    )
                )

        # ---------------------------------------------------------
        # Référence premier token
        # ---------------------------------------------------------

        first = (
            text
            .split()[0]
            .strip("=:")
        )

        if self.is_reference(first):

            remaining = text[
                len(first):
            ]

            return (
                first.upper(),
                self.clean_designation(
                    remaining
                )
            )

        return (
            "",
            self.clean_designation(text)
        )

    # =============================================================
    # REFERENCE EXPLICITE LINEBUILDER
    # =============================================================

    def get_explicit_reference(
        self,
        ligne
    ):

        for cellule in ligne:

            if not isinstance(
                cellule,
                dict
            ):
                continue

            # -----------------------------------------------------
            # Colonne reference
            # -----------------------------------------------------

            if (
                self.normalize_column(
                    cellule.get(
                        "column",
                        ""
                    )
                )
                == "REFERENCE"
            ):

                text = self.normalize_text(
                    cellule.get(
                        "text",
                        ""
                    )
                )

                if self.is_reference(
                    text
                ):

                    return text.upper()

            # -----------------------------------------------------
            # detected_reference
            # -----------------------------------------------------

            detected = cellule.get(
                "detected_reference"
            )

            if detected:

                detected = self.normalize_text(
                    detected
                )

                if self.is_reference(
                    detected
                ):

                    return detected.upper()

        return ""

    # =============================================================
    # NORMALIZE LINEBUILDER GROUP
    # =============================================================

    @staticmethod
    def normalize_linebuilder_group(
        group
    ):

        if not isinstance(
            group,
            dict
        ):
            return group, ""

        elements = group.get(
            "elements",
            []
        )

        forced_reference = (
            group.get(
                "reference"
            )
            or ""
        )

        return (
            elements,
            str(
                forced_reference
            ).strip().upper()
        )

    # =============================================================
    # CELL X
    # =============================================================

    def get_cell_x(self, cellule):

        if not isinstance(
            cellule,
            dict
        ):
            return 0.0

        if cellule.get("x") is not None:

            try:

                return float(
                    cellule.get("x")
                )

            except (
                ValueError,
                TypeError
            ):

                pass

        box = cellule.get(
            "box",
            [0, 0, 0, 0]
        )

        if (
            isinstance(
                box,
                (list, tuple)
            )
            and len(box) >= 4
        ):

            try:

                return (
                    float(box[0])
                    + float(box[2])
                ) / 2

            except (
                ValueError,
                TypeError
            ):

                return 0.0

        return 0.0

    # =============================================================
    # EXTRACT AMOUNT
    # =============================================================

    def extract_amount_from_cell(
        self,
        cellule
    ):
        """
        Extrait un montant depuis une cellule.

        Exemples :

            600.00
            600,00
            MONTANT 600
            TOTAL TTC 600
        """

        if not isinstance(
            cellule,
            dict
        ):
            return None

        text = self.normalize_text(
            cellule.get(
                "text",
                ""
            )
        )

        if not text:
            return None

        # ---------------------------------------------------------
        # Direct
        # ---------------------------------------------------------

        value = self.to_float(text)

        if value is not None:

            return value

        # ---------------------------------------------------------
        # Recherche nombres
        # ---------------------------------------------------------

        matches = re.findall(
            r"\d+(?:[.,]\d{1,2})?",
            text
        )

        if not matches:
            return None

        values = []

        for match in matches:

            try:

                value = float(
                    match.replace(
                        ",",
                        "."
                    )
                )

                if value >= 0:
                    values.append(value)

            except ValueError:

                continue

        if not values:
            return None

        return values[-1]

    # =============================================================
    # GET NUMERIC VALUE
    # =============================================================

    def get_numeric_value(
        self,
        cellule
    ):

        if not isinstance(
            cellule,
            dict
        ):
            return None

        texte = self.normalize_text(
            cellule.get(
                "text",
                ""
            )
        )

        return self.to_float(
            texte
        )

    # =============================================================
    # PLAUSIBLE LINE TOTAL
    # =============================================================

    def is_plausible_line_total(
        self,
        total,
        quantity,
        unit_price,
        tva=None
    ):
        """
        Vérifie si le total correspond à :

            QTE × PU

        ou :

            QTE × PU × (1 + TVA)
        """

        if total is None:
            return False

        if quantity is None or unit_price is None:

            return True

        if quantity <= 0:
            return False

        if unit_price < 0:
            return False

        expected_ht = (
            quantity
            * unit_price
        )

        # ---------------------------------------------------------
        # HT
        # ---------------------------------------------------------

        if abs(
            total - expected_ht
        ) <= self.tolerance:

            return True

        # ---------------------------------------------------------
        # TTC
        # ---------------------------------------------------------

        if tva is not None:

            expected_ttc = (
                expected_ht
                * (1 + tva / 100)
            )

            if abs(
                total - expected_ttc
            ) <= self.tolerance:

                return True

        return False

    # =============================================================
    # FIND LINE TOTAL
    # =============================================================

    def find_line_total(
        self,
        ligne,
        quantity=None,
        unit_price=None,
        tva=None,
        existing_total=None
    ):
        """
        Détermine le meilleur total de ligne.

        Priorité :

        1. total déjà détecté et cohérent
        2. colonne TOTAL explicite
        3. cellule contenant TOTAL/MONTANT
        4. cellule numérique cohérente
        5. QTE × PU
        """

        candidates = []

        # =========================================================
        # 1. TOTAL EXISTANT
        # =========================================================

        if (
            existing_total is not None
            and self.is_valid_price(
                existing_total
            )
        ):

            if self.is_plausible_line_total(
                existing_total,
                quantity,
                unit_price,
                tva
            ):

                return round(
                    existing_total,
                    2
                )

        # =========================================================
        # 2. COLONNE TOTAL
        # =========================================================

        for cellule in ligne:

            if not isinstance(
                cellule,
                dict
            ):
                continue

            column = cellule.get(
                "column",
                ""
            )

            if not self.is_total_column(
                column
            ):
                continue

            value = self.extract_amount_from_cell(
                cellule
            )

            if value is None:
                continue

            if not self.is_valid_price(
                value
            ):
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

                "x": self.get_cell_x(
                    cellule
                )
            })

        # =========================================================
        # 3. TEXTE CONTENANT TOTAL / MONTANT
        # =========================================================

        for cellule in ligne:

            if not isinstance(
                cellule,
                dict
            ):
                continue

            text = self.normalize_text(
                cellule.get(
                    "text",
                    ""
                )
            ).upper()

            if not text:
                continue

            if (
                "TOTAL" not in text
                and "MONTANT" not in text
            ):
                continue

            value = self.extract_amount_from_cell(
                cellule
            )

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

                "x": self.get_cell_x(
                    cellule
                )
            })

        # =========================================================
        # 4. CELLULES NUMERIQUES
        # =========================================================

        for cellule in ligne:

            if not isinstance(
                cellule,
                dict
            ):
                continue

            text = self.normalize_text(
                cellule.get(
                    "text",
                    ""
                )
            )

            if not text:
                continue

            # uniquement nombre
            if not re.fullmatch(
                r"\s*\d+(?:[.,]\d+)?\s*",
                text
            ):
                continue

            value = self.to_float(
                text
            )

            if value is None:
                continue

            # Ne pas reprendre quantité
            if (
                quantity is not None
                and abs(
                    value - quantity
                ) <= self.tolerance
            ):
                continue

            # Ne pas reprendre PU
            if (
                unit_price is not None
                and abs(
                    value - unit_price
                ) <= self.tolerance
            ):
                continue

            # Si QTE + PU connus,
            # un candidat incohérent est rejeté.
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

                "x": self.get_cell_x(
                    cellule
                )
            })

        # =========================================================
        # 5. MEILLEUR CANDIDAT
        # =========================================================

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

                    return round(
                        best["value"],
                        2
                    )

            else:

                return round(
                    best["value"],
                    2
                )

        # =========================================================
        # 6. FALLBACK QTE × PU
        # =========================================================

        if (
            quantity is not None
            and unit_price is not None
        ):

            return round(
                quantity * unit_price,
                2
            )

        return None

    # =============================================================
    # RECOVER MISSING NUMERIC FIELDS
    # =============================================================

    def recover_missing_numeric_fields(
        self,
        ligne,
        article
    ):
        """
        Récupère les champs numériques manquants.

        Priorité :
            1. récupérer les valeurs explicitement classifiées
            2. récupérer le total
            3. si quantité absente et PU + total connus,
            calculer quantité = total / PU
        """

        numeric_candidates = []

        for cellule in ligne:

            if not isinstance(
                cellule,
                dict
            ):
                continue

            texte = self.normalize_text(
                cellule.get(
                    "text",
                    ""
                )
            )

            if not texte:
                continue

            value = self.to_float(
                texte
            )

            if value is None:
                continue

            colonne = self.normalize_column(
                cellule.get(
                    "column",
                    ""
                )
            )

            x = self.get_cell_x(
                cellule
            )

            numeric_candidates.append({
                "value": value,
                "column": colonne,
                "x": x,
                "element": cellule
            })

        # =========================================================
        # QUANTITE EXPLICITE
        # =========================================================

        if article["quantite"] is None:

            quantity_candidates = []

            for candidate in numeric_candidates:

                value = candidate["value"]

                if not float(value).is_integer():
                    continue

                if not self.is_valid_quantity(
                    value
                ):
                    continue

                if self.is_quantity_column(
                    candidate["column"]
                ):
                    quantity_candidates.append(
                        candidate
                    )

            if quantity_candidates:

                quantity_candidates.sort(
                    key=lambda item: item["x"]
                )

                article["quantite"] = int(
                    quantity_candidates[0]["value"]
                )

        # =========================================================
        # PRIX UNITAIRE
        # =========================================================

        if article["prix_unitaire"] is None:

            price_candidates = []

            for candidate in numeric_candidates:

                value = candidate["value"]

                if not self.is_valid_price(
                    value
                ):
                    continue

                if self.is_unit_price_column(
                    candidate["column"]
                ):
                    price_candidates.append(
                        candidate
                    )

            if price_candidates:

                price_candidates.sort(
                    key=lambda item: item["x"]
                )

                article["prix_unitaire"] = (
                    price_candidates[0]["value"]
                )

        # =========================================================
        # TVA
        # =========================================================

        if article["tva"] is None:

            tva_candidates = []

            for candidate in numeric_candidates:

                value = candidate["value"]

                if not self.is_valid_tva(
                    value
                ):
                    continue

                if self.is_tva_column(
                    candidate["column"]
                ):
                    tva_candidates.append(
                        candidate
                    )

            if tva_candidates:

                tva_candidates.sort(
                    key=lambda item: item["x"]
                )

                article["tva"] = (
                    tva_candidates[0]["value"]
                )

        # =========================================================
        # TOTAL
        # =========================================================

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

        # =========================================================
        # RECUPERATION QUANTITE
        # TOTAL / PU
        # =========================================================

        if (
            article["quantite"] is None
            and article["prix_unitaire"] is not None
            and article["total"] is not None
        ):

            unit_price = article["prix_unitaire"]
            total = article["total"]

            if unit_price > 0:

                recovered_quantity = (
                    total / unit_price
                )

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

    # =============================================================
    # REMOVE SUPPLIER NOISE
    # =============================================================

    def remove_supplier_noise(
        self,
        text
    ):

        if not text:
            return ""

        text = self.normalize_text(
            text
        )

        # ---------------------------------------------------------
        # TELEPHONES
        # ---------------------------------------------------------

        text = re.sub(
            r"\b(?:0[5-7]\d{8}|\+212[5-7]\d{8})\b",
            " ",
            text,
            flags=re.IGNORECASE
        )

        # OCR téléphone avec espaces
        text = re.sub(
            r"\b0[5-7](?:\s*\d){8}\b",
            " ",
            text,
            flags=re.IGNORECASE
        )

        # ---------------------------------------------------------
        # ICE
        # ---------------------------------------------------------

        text = re.sub(
            r"\b(?:ICE|1CE)\s*[:\-]?\s*\d{10,20}\b",
            " ",
            text,
            flags=re.IGNORECASE
        )

        # ---------------------------------------------------------
        # RIB
        # ---------------------------------------------------------

        text = re.sub(
            r"\bRIB\s*[:\-]?\s*[0-9\s]{10,40}",
            " ",
            text,
            flags=re.IGNORECASE
        )

        # ---------------------------------------------------------
        # EMAIL
        # ---------------------------------------------------------

        text = re.sub(
            r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
            " ",
            text,
            flags=re.IGNORECASE
        )

        # ---------------------------------------------------------
        # FOOTER
        # ---------------------------------------------------------

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

        text = re.sub(
            r"\s+",
            " ",
            text
        ).strip()

        return text

    # =============================================================
    # PARSE ONE LINE
    # =============================================================

    def parse_line(
        self,
        ligne,
        forced_reference=""
    ):
        """
        Parse une seule ligne LineBuilder.
        """

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

        # =========================================================
        # REFERENCE LINEBUILDER
        # =========================================================

        explicit_reference = (
            forced_reference
            or self.get_explicit_reference(
                ligne
            )
        )

        if explicit_reference:

            article["reference"] = (
                explicit_reference.upper()
            )

        # =========================================================
        # PARSE CELLULES
        # =========================================================

        for cellule in ligne:

            if not isinstance(
                cellule,
                dict
            ):
                continue

            colonne_raw = cellule.get(
                "column",
                ""
            )

            colonne = self.normalize_column(
                colonne_raw
            )

            texte = self.normalize_text(
                cellule.get(
                    "text",
                    ""
                )
            )

            if not texte:
                continue

            # -----------------------------------------------------
            # FOOTER
            # -----------------------------------------------------

            if self.is_footer_text(
                texte
            ):
                continue

            # -----------------------------------------------------
            # REFERENCE
            # -----------------------------------------------------

            if colonne == "REFERENCE":

                # ---------------------------------------------------------
                # Référence seule
                # ---------------------------------------------------------

                if self.is_reference(texte):

                    if not article["reference"]:
                        article["reference"] = texte.upper()

                    continue

                # ---------------------------------------------------------
                # Référence + désignation dans la même cellule
                # Exemple :
                # HP-W2072A -Toner HP 117A LASER POUR 150/178/179A YELLOW
                # ---------------------------------------------------------

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

            # -----------------------------------------------------
            # QUANTITY
            # -----------------------------------------------------

            if self.is_quantity_column(
                colonne
            ):

                value = self.to_float(
                    texte
                )

                if (
                    self.is_valid_quantity(
                        value
                    )
                    and article["quantite"] is None
                ):

                    if value.is_integer():

                        article["quantite"] = int(
                            value
                        )

                    else:

                        article["quantite"] = value

                continue

            # -----------------------------------------------------
            # UNIT PRICE
            # -----------------------------------------------------

            if self.is_unit_price_column(
                colonne
            ):

                value = self.to_float(
                    texte
                )

                if (
                    self.is_valid_price(
                        value
                    )
                    and article["prix_unitaire"] is None
                ):

                    article["prix_unitaire"] = value

                continue

            # -----------------------------------------------------
            # TVA
            # -----------------------------------------------------

            if self.is_tva_column(
                colonne
            ):

                value = self.to_float(
                    texte
                )

                if (
                    self.is_valid_tva(
                        value
                    )
                    and article["tva"] is None
                ):

                    article["tva"] = value

                continue

            # -----------------------------------------------------
            # TOTAL
            # -----------------------------------------------------

            if self.is_total_column(
                colonne
            ):

                value = self.extract_amount_from_cell(
                    cellule
                )

                if (
                    self.is_valid_price(
                        value
                    )
                    and article["total"] is None
                ):

                    article["total"] = value

                continue

            # -----------------------------------------------------
            # DESIGNATION
            # -----------------------------------------------------

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

            # -----------------------------------------------------
            # FALLBACK
            # -----------------------------------------------------

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

            if (
                has_letters
                and not is_numeric
            ):

                self.add_designation_text(
                    designation_parts,
                    texte,
                    article["reference"]
                )

        # ========================================================
        # BUILD DESIGNATION
        # ========================================================

        designation = " ".join(
            designation_parts
        )

        designation = self.clean_designation(
            designation
        )

        # ========================================================
        # REFERENCE ABSENTE
        # ========================================================

        if not article["reference"]:

            # ----------------------------------------------------
            # 1. Chercher une référence dans les cellules originales
            # ----------------------------------------------------

            for cellule in ligne:

                if not isinstance(cellule, dict):
                    continue

                texte_cellule = self.normalize_text(
                    cellule.get("text", "")
                )

                if not texte_cellule:
                    continue

                # Cas :
                # HP-F6V24AE
                if self.is_reference(texte_cellule):

                    article["reference"] = (
                        texte_cellule.upper()
                    )

                    break

                # Cas :
                # HP-F6V24AE CARTOUCHE HP 652 COULEUR
                extracted_ref = (
                    self.extract_reference_from_text(
                        texte_cellule
                    )
                )

                if extracted_ref:

                    article["reference"] = (
                        extracted_ref.upper()
                    )

                    break

        # --------------------------------------------------------
        # 2. Si toujours absente, chercher dans la désignation
        # --------------------------------------------------------

        if not article["reference"]:

            ref, des = self.split_reference(
                designation
            )

            article["reference"] = ref

            if des:
                designation = des

        # ========================================================
        # REMOVE REFERENCE FROM DESIGNATION
        # ========================================================

        if article["reference"]:

            ref = re.escape(
                article["reference"]
            )

            designation = re.sub(
                rf"^{ref}\s*[-=:]?\s*",
                "",
                designation,
                count=1,
                flags=re.IGNORECASE
            )

        # ========================================================
        # FINAL DESIGNATION
        # ========================================================

        article["designation"] = self.clean_designation(
            designation
        )

        # =========================================================
        # REFERENCE ABSENTE
        # =========================================================

        if not article["reference"]:

            ref, des = self.split_reference(
                designation
            )

            article["reference"] = ref

            article["designation"] = des

        else:

            designation = designation.strip()

            ref = re.escape(
                article["reference"]
            )

            designation = re.sub(
                rf"^{ref}\s*[-=:]?\s*",
                "",
                designation,
                flags=re.IGNORECASE
            )

            article["designation"] = (
                self.clean_designation(
                    designation
                )
            )

        # =========================================================
        # RECOVERY
        # =========================================================

        article = self.recover_missing_numeric_fields(
            ligne,
            article
        )

        # =========================================================
        # FINAL TOTAL
        # =========================================================

        article["total"] = self.find_line_total(
            ligne=ligne,
            quantity=article["quantite"],
            unit_price=article["prix_unitaire"],
            tva=article["tva"],
            existing_total=article["total"]
        )

        # =========================================================
        # FINAL CLEANING
        # =========================================================

        article["designation"] = self.clean_designation(
            article["designation"]
        )

        return article

    # =============================================================
    # PARSE ALL ARTICLES
    # =============================================================

    def parse(
        self,
        lignes
    ):

        articles = []

        for ligne in lignes or []:

            forced_reference = ""

            # -----------------------------------------------------
            # Groupe LineBuilder
            # -----------------------------------------------------

            if isinstance(
                ligne,
                dict
            ):

                (
                    ligne,
                    forced_reference
                ) = self.normalize_linebuilder_group(
                    ligne
                )

            # -----------------------------------------------------
            # Ligne invalide
            # -----------------------------------------------------

            if not isinstance(
                ligne,
                list
            ):
                continue

            article = self.parse_line(
                ligne,
                forced_reference=forced_reference
            )

            # -----------------------------------------------------
            # Article non vide
            # -----------------------------------------------------

            if (
                article["designation"]
                or article["reference"]
                or article["quantite"] is not None
                or article["prix_unitaire"] is not None
                or article["tva"] is not None
                or article["total"] is not None
            ):

                articles.append(
                    article
                )

        return articles

