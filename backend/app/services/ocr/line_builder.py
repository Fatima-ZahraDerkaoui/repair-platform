from collections import defaultdict
import re


class LineBuilder:

    def __init__(self, tolerance_y=3.0):

        self.tolerance_y = tolerance_y

        # ==========================================================
        # ENTÊTES
        # ==========================================================

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

        # ==========================================================
        # FIN DU TABLEAU
        # ==========================================================

        self.stop_words = [

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
        ]

        # ==========================================================
        # MOTS QUI NE DOIVENT JAMAIS ÊTRE DES REFERENCES
        # ==========================================================

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

        # ==========================================================
        # LONGUEUR MAXIMALE D'UNE REFERENCE
        # ==========================================================

        self.max_reference_length = 24

    # ==========================================================
    # NORMALISATION
    # ==========================================================

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

        text = re.sub(r"\s+", " ", text)

        return text.strip()

    # ==========================================================
    # COMPACT
    # ==========================================================

    def compact(self, text):

        text = self.normalize(text)

        return re.sub(
            r"[^A-Z0-9]",
            "",
            text
        )

    # ==========================================================
    # HEADER
    # ==========================================================

    def is_header(self, text):

        normalized = self.normalize(text)

        if normalized in self.headers:
            return True

        compact = self.compact(normalized)

        header_compacts = {

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

        return compact in header_compacts

    # ==========================================================
    # REFERENCE
    # ==========================================================
    def is_reference(self, text):

        if not text:
            return False

        text = self.normalize(text)

        if not text:
            return False

        # Une référence = une cellule
        if len(text.split()) > 1:
            return False

        # Longueur
        if len(text) > self.max_reference_length:
            return False

        # Pourcentage
        if "%" in text:
            return False

        # Nombre simple
        numeric_candidate = text.replace(",", ".")

        if re.fullmatch(
            r"\d+(?:\.\d+)?",
            numeric_candidate
        ):
            return False

        # Caractères autorisés
        if not re.fullmatch(
            r"[A-Z0-9][A-Z0-9._/\\-]*",
            text
        ):
            return False

        # ======================================================
        # BLACKLIST
        # ======================================================

        for prefix in self.reference_blacklist_prefixes:

            if text.startswith(prefix):
                return False

        forbidden = {
            "ARTICLE",
            "TOTAL",
            "REFERENCE",
            "DESIGNATION",
            "DESCRIPTION",
            "QUANTITE",
            "QTE",
            "TVA",
            "PRIX",
            "MONTANT",
            "CARTOUCHE",
            "TONER",
            "BLACK",
            "CYAN",
            "MAGENTA",
            "YELLOW",
        }

        if text in forbidden:
            return False

        # ======================================================
        # Une référence doit contenir au moins un chiffre
        # ======================================================

        if not re.search(r"\d", text):
            return False

        # ======================================================
        # Patterns
        # ======================================================

        patterns = [

            r"^[A-Z]{2,}-[A-Z0-9]+$",

            r"^[A-Z][0-9]+-[0-9A-Z]+$",

            r"^[A-Z]{3,}[0-9]+[A-Z0-9]*$",

            r"^[A-Z0-9]+/[A-Z0-9]+$",

            r"^[A-Z0-9]+_[A-Z0-9]+$",

            r"^[0-9]+-[A-Z0-9]+$",
        ]

        for pattern in patterns:

            if re.fullmatch(pattern, text):
                return True

        return False

    # ==========================================================
    # EXTRAIRE REFERENCE
    # ==========================================================

    def extract_reference_from_text(self, text):

        if not text:
            return None

        text = self.normalize(text)

        if not text:
            return None

        # ======================================================
        # CAS 1
        # REFERENCE SEULE
        # ======================================================

        if self.is_reference(text):
            return text

        # ======================================================
        # CAS 2
        # HP-F6V25AE-Cartouche...
        # HP-F6V25AE - Cartouche...
        # HP-F6V25AE : Cartouche...
        # ======================================================

        match = re.match(
            r"^([A-Z]{2,}-[A-Z0-9]+)"
            r"(?:[-=:]+|\s+-\s+|\s+)"
            r"(.+)$",
            text
        )

        if match:

            candidate = self.normalize(
                match.group(1)
            )

            if self.is_reference(candidate):

                return candidate

        # ======================================================
        # CAS 3
        # EPST103BK - ...
        # CANGI490M-CARTOUCHE...
        # ======================================================

        match = re.match(
            r"^([A-Z]{3,}[0-9]+[A-Z0-9]*)"
            r"(?:[-=:]+|\s+-\s+|\s+)"
            r"(.+)$",
            text
        )

        if match:

            candidate = self.normalize(
                match.group(1)
            )

            if self.is_reference(candidate):

                return candidate

        return None

    # ==========================================================
    # SUPPRIMER REFERENCE DU DEBUT DE LA DESIGNATION
    # ==========================================================

    def remove_reference_from_designation(
        self,
        text,
        reference
    ):

        if not text:
            return ""

        text = self.normalize(text)

        if not reference:
            return text

        reference = self.normalize(reference)

        # ------------------------------------------------------
        # Si le texte commence exactement par la référence
        # ------------------------------------------------------

        if not text.startswith(reference):
            return text

        remaining = text[len(reference):]

        # ------------------------------------------------------
        # Supprimer uniquement les séparateurs
        # ------------------------------------------------------

        remaining = re.sub(
            r"^\s*[-=:]+\s*",
            "",
            remaining
        )

        return remaining.strip()

    # ==========================================================
    # STOP
    # ==========================================================

    def is_stop(self, text):

        text = self.normalize(text)

        if not text:
            return False

        for word in self.stop_words:

            word = self.normalize(word)

            if word in text:
                return True

        return False

    # ==========================================================
    # GET Y
    # ==========================================================

    def get_y(self, element):

        if element.get("y") is not None:
            return float(element["y"])

        box = element.get(
            "box",
            [0, 0, 0, 0]
        )

        return (
            box[1] +
            box[3]
        ) / 2

    # ==========================================================
    # GET X
    # ==========================================================

    def get_x(self, element):

        if element.get("x") is not None:
            return float(element["x"])

        box = element.get(
            "box",
            [0, 0, 0, 0]
        )

        return (
            box[0] +
            box[2]
        ) / 2

    # ==========================================================
    # REFERENCE D'UNE LIGNE
    # ==========================================================

    def get_row_reference(self, row):

        # ======================================================
        # PRIORITE 1
        # COLONNE REFERENCE
        # ======================================================

        for element in row:

            if element.get("column") != "reference":
                continue

            text = self.normalize(
                element.get("text", "")
            )

            if self.is_reference(text):

                return text

        # ======================================================
        # PRIORITE 2
        # DESIGNATION
        #
        # Ancien format :
        # HP-F6V25AE-Cartouche HP...
        # ======================================================

        for element in row:

            column = element.get(
                "column",
                ""
            )

            # Dans l'ancien format la référence est
            # généralement dans designation.
            if column not in (
                "",
                "designation"
            ):
                continue

            text = self.normalize(
                element.get("text", "")
            )

            reference = (
                self.extract_reference_from_text(
                    text
                )
            )

            if reference:

                return reference

        return None

    # ==========================================================
    # DETECTER LES REFERENCES
    # ==========================================================

    def find_reference_elements(
        self,
        elements
    ):

        references = []

        # IMPORTANT :
        #
        # Ici on ne cherche PLUS une référence dans tous
        # les textes.
        #
        # Une référence explicite doit être dans :
        #
        #     column = reference
        #
        # Sinon un ancien format comme :
        #
        # HP-F6V25AE-Cartouche HP 652 Black
        #
        # serait considéré comme un article "new format"
        # et la désignation serait perdue.

        for element in elements:

            text = self.normalize(
                element.get("text", "")
            )

            if not text:
                continue

            if element.get("column") != "reference":
                continue

            if not self.is_reference(text):
                continue

            copy_element = element.copy()

            copy_element[
                "detected_reference"
            ] = text

            references.append(
                copy_element
            )

        return references

    # ==========================================================
    # TROUVER ARTICLE LE PLUS PROCHE
    # ==========================================================
    def find_best_article(
        self,
        element,
        articles
    ):

        if not articles:
            return None

        y = self.get_y(element)

        # ==================================================
        # 1. PRIORITE AUX INTERVALLES
        # ==================================================

        for article in articles:

            start_y = article.get(
                "start_y",
                article["reference_y"] - 3
            )

            end_y = article.get(
                "end_y",
                float("inf")
            )

            if start_y <= y < end_y:
                return article

        # ==================================================
        # 2. FALLBACK TRES STRICT
        # ==================================================

        candidates = [
            article
            for article in articles
            if article["reference_y"] <= y
        ]

        if not candidates:
            return None

        best = candidates[-1]

        distance = abs(
            y - best["reference_y"]
        )

        # Ne jamais envoyer un élément éloigné
        # arbitrairement vers le dernier article.
        if distance <= 35:
            return best

        return None

    # ==========================================================
    # NETTOYER ELEMENT DESIGNATION
    # ==========================================================

    def clean_article_elements(
        self,
        elements,
        reference
    ):

        cleaned = []

        for element in elements:

            element = element.copy()

            text = self.normalize(
                element.get("text", "")
            )

            column = element.get(
                "column",
                ""
            )

            # --------------------------------------------------
            # REFERENCE EXPLICITE
            # --------------------------------------------------

            if column == "reference":

                # Ne pas mettre la référence dans designation
                continue

            # --------------------------------------------------
            # DESIGNATION
            # --------------------------------------------------

            if column == "designation":

                text = (
                    self.remove_reference_from_designation(
                        text,
                        reference
                    )
                )

                # Si après suppression il ne reste rien,
                # on ne garde pas l'élément.
                if not text:
                    continue

                element["text"] = text

            cleaned.append(element)

        return cleaned

    # ==========================================================
    # SUPPRIMER DOUBLONS ELEMENTS
    # ==========================================================

    def deduplicate_elements(
        self,
        elements
    ):

        unique = []
        seen = set()

        for element in elements:

            key = (
                self.normalize(
                    element.get("text", "")
                ),
                round(
                    self.get_x(element),
                    1
                ),
                round(
                    self.get_y(element),
                    1
                ),
                element.get(
                    "column",
                    ""
                ),
            )

            if key in seen:
                continue

            seen.add(key)
            unique.append(element)

        return unique

        # ==========================================================
    # VERIFIER DESIGNATION NOUVEAU FORMAT
    # ==========================================================

    def is_valid_new_format_designation(
        self,
        element,
        article_elements
    ):
        """
        Vérifie qu'un élément classifié comme designation
        correspond réellement à une désignation.

        IMPORTANT :
        On ne modifie PAS l'ancien format.
        Cette validation est utilisée uniquement
        dans le nouveau format avec référence explicite.
        """

        if element.get("column") != "designation":
            return True

        text = self.normalize(
            element.get("text", "")
        )

        if not text:
            return False

        x = self.get_x(element)

        # ------------------------------------------------------
        # 1. Un seul caractère = généralement bruit OCR
        #
        # Exemple :
        # R
        # C
        # I
        # ------------------------------------------------------

        if len(text) == 1:
            return False

        # ------------------------------------------------------
        # 2. Trouver la position de la colonne QTE
        # ------------------------------------------------------

        qte_elements = [
            e for e in article_elements
            if e.get("column") == "qte"
        ]

        if qte_elements:

            qte_x = min(
                self.get_x(e)
                for e in qte_elements
            )

            # --------------------------------------------------
            # Une désignation doit être à gauche de QTE.
            #
            # Exemple faux :
            #
            # x=977 IIC
            # x=791 QTE
            #
            # IIC est donc rejeté.
            # --------------------------------------------------

            if x >= qte_x - 10:
                return False

        # ------------------------------------------------------
        # 3. Une désignation doit contenir au moins
        #    une lettre
        # ------------------------------------------------------

        if not re.search(
            r"[A-Z]",
            text
        ):
            return False

        return True

    # ==========================================================
    # NETTOYER DESIGNATIONS NOUVEAU FORMAT
    # ==========================================================

    def clean_new_format_designations(
        self,
        elements
    ):

        if not elements:
            return []

        # ------------------------------------------------------
        # Les colonnes numériques servent de référence
        # pour déterminer la vraie zone de désignation.
        # ------------------------------------------------------

        qte_elements = [
            e for e in elements
            if e.get("column") == "qte"
        ]

        qte_x = None

        if qte_elements:

            qte_x = min(
                self.get_x(e)
                for e in qte_elements
            )

        cleaned = []

        for element in elements:

            element = element.copy()

            column = element.get(
                "column",
                ""
            )

            text = self.normalize(
                element.get(
                    "text",
                    ""
                )
            )

            # --------------------------------------------------
            # Désignation
            # --------------------------------------------------

            if column == "designation":

                if not text:
                    continue

                # ----------------------------------------------
                # Rejeter les caractères isolés
                # ----------------------------------------------

                if len(text) == 1:
                    continue

                # ----------------------------------------------
                # Rejeter les éléments OCR qui se trouvent
                # dans les colonnes numériques.
                # ----------------------------------------------

                if qte_x is not None:

                    x = self.get_x(element)

                    if x >= qte_x - 10:
                        continue

                # ----------------------------------------------
                # Une désignation doit avoir au moins une lettre
                # ----------------------------------------------

                if not re.search(
                    r"[A-Z]",
                    text
                ):
                    continue

                element["text"] = text

            cleaned.append(element)

        return cleaned

    # ==========================================================
    # FUSIONNER LES ELEMENTS DE DESIGNATION
    # ==========================================================

    def merge_designation_elements(self, elements):

        if not elements:
            return elements

        designation_elements = [
            e for e in elements
            if e.get("column") == "designation"
        ]

        if len(designation_elements) <= 1:
            return elements

        # ------------------------------------------------------
        # Trier les morceaux par Y puis X
        # ------------------------------------------------------

        designation_elements.sort(
            key=lambda e: (
                self.get_y(e),
                self.get_x(e)
            )
        )

        # ------------------------------------------------------
        # Construire le texte complet
        # ------------------------------------------------------

        parts = []

        for element in designation_elements:

            text = self.normalize(
                element.get("text", "")
            )

            if text:
                parts.append(text)

        if not parts:
            return elements

        designation_complete = " ".join(parts)

        # ------------------------------------------------------
        # Garder le premier élément comme élément principal
        # ------------------------------------------------------

        first = designation_elements[0].copy()

        first["text"] = designation_complete

        # ------------------------------------------------------
        # Supprimer les anciens morceaux designation
        # ------------------------------------------------------

        result = []

        first_added = False

        for element in elements:

            if element.get("column") == "designation":

                if not first_added:

                    result.append(first)

                    first_added = True

                continue

            result.append(element)

        return result
    
    # ==========================================================
    # BUILD
    # ==========================================================

    def build(
        self,
        classified
    ):

        if not classified:
            return []

        # ======================================================
        # 1. NETTOYAGE
        # ======================================================

        elements = []

        for element in classified:

            text = self.normalize(
                element.get("text", "")
            )

            if not text:
                continue

            # Ignorer les headers
            if self.is_header(text):
                continue

            # Ignorer éléments sans position
            if (
                element.get("x") is None
                and element.get("box") is None
            ):
                continue

            element = element.copy()

            element["x"] = self.get_x(
                element
            )

            element["y"] = self.get_y(
                element
            )

            elements.append(
                element
            )

        if not elements:
            return []

        # ======================================================
        # 2. REFERENCES EXPLICITES
        # ======================================================

        reference_elements = (
            self.find_reference_elements(
                elements
            )
        )

        # ======================================================
        # 3. ANCIEN FORMAT
        #
        # Exemple :
        #
        # HP-F6V25AE-Cartouche HP 652 Black
        #
        # Pas de colonne reference explicite.
        # ======================================================

        if not reference_elements:

            return self.build_old_format(
                elements
            )

        # ======================================================
        # 4. NOUVEAU FORMAT
        # ======================================================

        reference_elements.sort(
            key=lambda e: self.get_y(e)
        )

        # ======================================================
        # 5. CREATION ARTICLES
        # ======================================================

        articles = []

        for ref_element in reference_elements:

            reference = ref_element.get(
                "detected_reference"
            )

            if not reference:

                reference = self.normalize(
                    ref_element.get(
                        "text",
                        ""
                    )
                )

            reference_y = self.get_y(
                ref_element
            )

            # --------------------------------------------------
            # Eviter seulement les doublons OCR très proches
            # --------------------------------------------------

            duplicate = False

            for article in articles:

                if (
                    article["reference"]
                    == reference
                    and
                    abs(
                        article["reference_y"]
                        -
                        reference_y
                    ) <= self.tolerance_y
                ):

                    duplicate = True
                    break

            if duplicate:
                continue

            article = {

                "reference":
                    reference,

                "reference_y":
                    reference_y,

                "elements":
                    [],
            }

            articles.append(
                article
            )

        # ======================================================
        # 6. DETECTER LA FIN DU TABLEAU
        # ======================================================

        stop_y = float("inf")

        for element in elements:

            text = self.normalize(
                element.get("text", "")
            )

            if not self.is_stop(text):
                continue

            y = self.get_y(element)

            if y < stop_y:
                stop_y = y


        # ======================================================
        # 7. INTERVALLES DES ARTICLES
        # ======================================================
        for i, article in enumerate(articles):

            current_y = article["reference_y"]

            # --------------------------------------------------
            # Début
            # --------------------------------------------------

            article["start_y"] = current_y - 3

            # --------------------------------------------------
            # Fin = référence suivante
            # --------------------------------------------------

            if i < len(articles) - 1:

                next_y = articles[i + 1]["reference_y"]

                article["end_y"] = next_y

            # --------------------------------------------------
            # Dernier article = fin du tableau
            # --------------------------------------------------

            else:

                article["end_y"] = stop_y

                # Aucun élément de fin détecté
                if article["end_y"] == float("inf"):

                    # On garde une limite raisonnable
                    article["end_y"] = (
                        article["reference_y"] + 80
                    )

        # ======================================================
        # 7. ASSIGNATION
        # ======================================================

        for element in elements:

            text = self.normalize(
                element.get(
                    "text",
                    ""
                )
            )

            y = self.get_y(
                element
            )

            # --------------------------------------------------
            # STOP
            # --------------------------------------------------

            if self.is_stop(text):

                if element.get("column") not in {
                    "designation",
                    "reference"
                }:
                    continue

            # --------------------------------------------------
            # NE PAS AJOUTER LES REFERENCES
            # --------------------------------------------------

            if (
                element.get("column")
                == "reference"
            ):

                continue

            # --------------------------------------------------
            # CHERCHER ARTICLE
            # --------------------------------------------------

            assigned = False

            for article in articles:

                if not (
                    y >= article["start_y"]
                    and
                    y < article["end_y"]
                ):
                    continue

                # ==================================================
                # PROTECTION NOUVEAU FORMAT
                # ==================================================
                #
                # Si OCR dit "designation", on vérifie que
                # l'élément est réellement dans la zone gauche
                # du tableau.
                #
                # Exemple :
                #
                # IIC
                # x = 977
                #
                # QTE
                # x = 791
                #
                # => IIC ne peut pas être une designation.
                # ==================================================

                if element.get("column") == "designation":

                    qte_x_values = [
                        self.get_x(e)
                        for e in article["elements"]
                        if e.get("column") == "qte"
                    ]

                    if qte_x_values:

                        qte_x = min(
                            qte_x_values
                        )

                        if self.get_x(element) >= qte_x - 10:

                            # Ne pas assigner
                            # cet élément à l'article.
                            assigned = True
                            break

                    # ----------------------------------------------
                    # Une lettre isolée n'est pas une désignation
                    # ----------------------------------------------

                    if len(text) <= 1:

                        assigned = True
                        break

                # --------------------------------------------------
                # ELEMENT NORMAL
                # --------------------------------------------------

                article[
                    "elements"
                ].append(
                    element
                )

                assigned = True

                break

            # --------------------------------------------------
            # FALLBACK
            # --------------------------------------------------

            if not assigned:

                # --------------------------------------------------
                # Ne jamais réinjecter un faux designation
                # dans le fallback.
                # --------------------------------------------------

                if (
                    element.get("column")
                    == "designation"
                ):

                    qte_x_values = []

                    for article in articles:

                        for e in article["elements"]:

                            if (
                                e.get("column")
                                == "qte"
                            ):

                                qte_x_values.append(
                                    self.get_x(e)
                                )

                    if qte_x_values:

                        qte_x = min(
                            qte_x_values
                        )

                        if self.get_x(element) >= qte_x - 10:

                            continue

                    if len(text) <= 1:

                        continue

                best = (
                    self.find_best_article(
                        element,
                        articles
                    )
                )

                if best:

                    distance = abs(
                        y - best["reference_y"]
                    )

                    if distance <= max(
                        35,
                        self.tolerance_y * 2
                    ):

                        best["elements"].append(
                            element
                        )

        # ======================================================
        # 8. RESULTAT FINAL
        # ======================================================

        result = []

        for article in articles:

            elements_article = (
                self.deduplicate_elements(
                    article["elements"]
                )
            )

            # --------------------------------------------------
            # Nettoyage désignation / référence
            # --------------------------------------------------

            elements_article = (
                self.clean_article_elements(
                    elements_article,
                    article["reference"]
                )
            )

            # --------------------------------------------------
            # NOUVEAU FORMAT :
            # supprimer les faux éléments designation
            #
            # Exemple :
            # IIC x=977 -> supprimé
            # R   x=718 -> supprimé
            #
            # mais :
            # TONER MINOLTA... x=494 -> conservé
            # TN 324/512 NOIR CET x=430 -> conservé
            # --------------------------------------------------

            elements_article = (
                self.clean_new_format_designations(
                    elements_article
                )
            )
            elements_article = (
                self.merge_designation_elements(
                    elements_article
                )
            )

            # --------------------------------------------------
            # Trier Y puis X
            # --------------------------------------------------

            elements_article.sort(
                key=lambda e: (
                    self.get_y(e),
                    self.get_x(e)
                )
            )

            result.append({

                "reference":
                    article["reference"],

                "reference_y":
                    article["reference_y"],

                "elements":
                    elements_article,
            })

        return result
    # ==========================================================
    # BUILD ANCIEN FORMAT
    # ==========================================================

    def build_old_format(
        self,
        elements
    ):

        if not elements:
            return []

        # ======================================================
        # 1. REGROUPEMENT PAR Y
        # ======================================================

        rows = defaultdict(list)

        for element in elements:

            y = self.get_y(
                element
            )

            key = round(
                y / self.tolerance_y
            )

            rows[key].append(
                element
            )

        # ======================================================
        # 2. TRI
        # ======================================================

        grouped = []

        for _, row in sorted(
            rows.items()
        ):

            row.sort(
                key=lambda e:
                self.get_x(e)
            )

            grouped.append(
                row
            )

        # ======================================================
        # 3. CONSTRUCTION
        # ======================================================

        articles = []

        article = None

        for row in grouped:

            if not row:
                continue

            # --------------------------------------------------
            # Texte global
            # --------------------------------------------------

            text = " ".join(

                self.normalize(
                    e.get(
                        "text",
                        ""
                    )
                )

                for e in row
            )

            # --------------------------------------------------
            # FIN TABLEAU
            # --------------------------------------------------

            if self.is_stop(text):

                if article is not None:

                    articles.append(
                        article
                    )

                    article = None

                break

            # --------------------------------------------------
            # REFERENCE
            # --------------------------------------------------

            reference = (
                self.get_row_reference(
                    row
                )
            )

            # --------------------------------------------------
            # NOUVEL ARTICLE
            # --------------------------------------------------

            if reference:

                # ----------------------------------------------
                # Sauvegarder précédent
                # ----------------------------------------------

                if article is not None:

                    articles.append(
                        article
                    )

                # ----------------------------------------------
                # Trouver Y exact
                # ----------------------------------------------

                reference_y = (
                    self.get_y(
                        row[0]
                    )
                )

                reference_element = None

                for element in row:

                    extracted = (
                        self.extract_reference_from_text(
                            element.get(
                                "text",
                                ""
                            )
                        )
                    )

                    if extracted == reference:

                        reference_y = (
                            self.get_y(
                                element
                            )
                        )

                        reference_element = (
                            element
                        )

                        break

                # ----------------------------------------------
                # IMPORTANT
                #
                # On conserve la désignation.
                # On ne supprime PAS l'élément contenant
                # la référence.
                # Le nettoyage se fera après.
                # ----------------------------------------------

                article = {

                    "reference":
                        reference,

                    "reference_y":
                        reference_y,

                    "elements":
                        row.copy(),
                }

                continue

            # --------------------------------------------------
            # CONTINUATION
            # --------------------------------------------------

            if article is not None:

                article[
                    "elements"
                ].extend(
                    row
                )

        # ======================================================
        # 4. DERNIER ARTICLE
        # ======================================================

        if article is not None:

            articles.append(
                article
            )

        # ======================================================
        # 5. NETTOYAGE
        # ======================================================

        result = []

        for article in articles:

            reference = (
                article["reference"]
            )

            elements_article = (
                self.deduplicate_elements(
                    article["elements"]
                )
            )

            # --------------------------------------------------
            # IMPORTANT :
            # garder la désignation mais retirer
            # seulement la référence du début.
            # --------------------------------------------------

            elements_article = (
                self.clean_article_elements(
                    elements_article,
                    reference
                )
            )

            elements_article.sort(
                key=lambda e: (
                    self.get_y(e),
                    self.get_x(e)
                )
            )

            result.append({

                "reference":
                    reference,

                "reference_y":
                    article[
                        "reference_y"
                    ],

                "elements":
                    elements_article,
            })

        return result

    # ==========================================================
    # FORMAT ARTICLE
    # ==========================================================

    def format_article(
        self,
        elements
    ):

        if not elements:

            return {

                "reference":
                    None,

                "elements":
                    [],
            }

        reference = (
            self.get_row_reference(
                elements
            )
        )

        elements = (
            self.clean_article_elements(
                elements,
                reference
            )
        )

        return {

            "reference":
                reference,

            "elements":
                elements,
        }
    