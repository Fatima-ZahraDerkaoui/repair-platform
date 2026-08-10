from collections import defaultdict
import re


class LineBuilder:
    """Builds invoice articles from classified OCR cells.

    Two modes are supported automatically:
      NEW: explicit reference column -> article boundaries are reference Y's.
      OLD: no reference column -> rows are grouped by Y and references are
           extracted from the designation text.
    """

    def __init__(self, tolerance_y=15):
        self.tolerance_y = tolerance_y
        self.headers = {
            "DESIGNATION", "DÉSIGNATION", "DESCRIPTION", "REFERENCE", "RÉFÉRENCE",
            "REF", "RÉF", "ARTICLE", "TVA", "TAUX", "PU", "P.U", "P.U.",
            "P.U.TTC", "P.U TTC", "P.U HT", "PU TTC", "PU HT", "PRIX",
            "PRIX UNITAIRE", "PRIX UNITAIRE TTC", "QTE", "QTÉ", "QUANTITE",
            "QUANTITÉ", "TOTAL", "TOTAL TTC", "MONTANT", "MONTANT TTC", "REMISE",
        }
        self.stop_words = [
            "TOTAL HT", "TOTAL H.T", "TOTAL H T", "TOTAL TVA", "TOTAL T.V.A",
            "TOTAL TTC", "TOTAL T.T.C", "NET A PAYER", "NET À PAYER", "NET A PAYE",
            "A PAYER", "À PAYER", "SOUS TOTAL", "SOUS-TOTAL", "SOUS TOTAL HT",
            "SOUS TOTAL TTC", "ARRETEE LA PRESENTE FACTURE",
            "ARRÊTÉE LA PRÉSENTE FACTURE", "MODE DE REGLEMENT", "MODE DE RÈGLEMENT",
        ]

    @staticmethod
    def normalize(text):
        if text is None:
            return ""
        text = str(text).upper().strip()
        replacements = str.maketrans({
            "É": "E", "È": "E", "Ê": "E", "Ë": "E", "À": "A", "Â": "A",
            "Ç": "C", "Ù": "U", "Û": "U", "Ô": "O", "Ö": "O", "Î": "I", "Ï": "I",
        })
        text = text.translate(replacements)
        return re.sub(r"\s+", " ", text).strip()

    def compact(self, text):
        return re.sub(r"[^A-Z0-9]", "", self.normalize(text))

    def is_header(self, text):
        normalized = self.normalize(text)
        if normalized in self.headers:
            return True
        return self.compact(normalized) in {
            "REFERENCE", "REF", "DESIGNATION", "DESCRIPTION", "ARTICLE", "QUANTITE", "QTE",
            "TVA", "TAUX", "PU", "PUTTC", "PUHT", "PRIX", "PRIXUNITAIRE",
            "PRIXUNITAIRETTC", "TOTAL", "TOTALTTC", "MONTANT", "MONTANTTTC",
        }

    def is_reference(self, text):
        text = self.normalize(text)
        if not text or len(text.split()) > 1 or "%" in text:
            return False
        compact = re.sub(r"\s+", "", text)
        if re.fullmatch(r"\d+(?:[.,]\d+)?", compact):
            return False
        if not re.fullmatch(r"[A-Z0-9][A-Z0-9._/\\-]*", compact):
            return False
        if not re.search(r"\d", compact):
            return False
        # Reference must contain letters and digits; this prevents prices.
        if not re.search(r"[A-Z]", compact):
            return False
        patterns = [
            r"^[A-Z]{2,}-[A-Z0-9]+$",
            r"^[A-Z]{2,}-[0-9A-Z]+$",
            r"^[A-Z][0-9]+-[0-9A-Z]+$",
            r"^[A-Z]{3,}[0-9]+[A-Z0-9]*$",
            r"^[A-Z0-9]+[/\\_][A-Z0-9]+$",
        ]
        return any(re.fullmatch(p, compact) for p in patterns)

    def extract_reference_from_text(self, text):
        text = self.normalize(text)
        if not text:
            return None
        if self.is_reference(text):
            return text

        # Reference followed by a hyphen and designation.
        patterns = [
            r"^([A-Z]{2,}-[A-Z0-9]+)(?:[-=: ]+)(.+)$",
            r"^([A-Z]{3,}[0-9]+[A-Z0-9]*)(?:[-=: ]+)(.+)$",
        ]
        for pattern in patterns:
            match = re.match(pattern, text)
            if match and self.is_reference(match.group(1)):
                return match.group(1)
        return None

    def is_stop(self, text):

        text = self.normalize(text)

        if not text:
            return False

        compact = self.compact(text)

        stop_patterns = [
            "TOTALHT",
            "TOTALTVA",
            "TOTALTTC",
            "NETAPAYER",
            "SOUS TOTAL",
            "SOUS-TOTAL",
            "ARRETEE LA PRESENTE FACTURE",
            "ARRETEELAPRESENTEFACTURE",
            "MODE DE REGLEMENT",
            "MODEDEREGLEMENT",
        ]

        for stop in stop_patterns:

            stop_compact = self.compact(
                stop
            )

            # Cas exact ou début de ligne
            if compact == stop_compact:
                return True

            if compact.startswith(
                stop_compact
            ):
                return True

        return False

    @staticmethod
    def get_y(element):
        if element.get("y") is not None:
            return float(element["y"])
        box = element.get("box", [0, 0, 0, 0])
        return (box[1] + box[3]) / 2.0

    @staticmethod
    def get_x(element):
        if element.get("x") is not None:
            return float(element["x"])
        box = element.get("box", [0, 0, 0, 0])
        return (box[0] + box[2]) / 2.0

    def get_row_reference(self, row):
        for element in row:
            if element.get("column") == "reference":
                text = self.normalize(element.get("text", ""))
                if self.is_reference(text):
                    return text
        for element in row:
            reference = self.extract_reference_from_text(element.get("text", ""))
            if reference:
                return reference
        return None

    # ==========================================================
    # DETECTER LE TYPE DE FACTURE
    # ==========================================================

    def has_explicit_reference_column(self, elements):
        """
        True uniquement lorsqu'une vraie colonne 'reference'
        existe dans les éléments classifiés.

        Nouveau format :
            reference | designation | qte | pu | total

        Ancien format :
            HP-F6V25AE-Cartouche HP 652 Black
        """

        for element in elements:

            column = element.get("column", "")

            if column != "reference":
                continue

            text = self.normalize(
                element.get("text", "")
            )

            if self.is_reference(text):
                return True

        return False

    # ==========================================================
    # DETECTER LES REFERENCES
    # ==========================================================

    def find_reference_elements(
        self,
        elements,
        explicit_reference_mode=False
    ):
        """
        Détecte les références.

        IMPORTANT :
        - Nouveau format :
        uniquement la colonne 'reference'.
        - Ancien format :
        cette fonction n'est normalement pas utilisée ;
        build_old_format() s'en charge.
        """

        references = []

        for element in elements:

            text = self.normalize(
                element.get("text", "")
            )

            if not text:
                continue

            # ======================================================
            # NOUVEAU FORMAT
            # ======================================================

            if explicit_reference_mode:

                if element.get("column") != "reference":
                    continue

                if not self.is_reference(text):
                    continue

                copy_element = element.copy()

                copy_element["detected_reference"] = text

                references.append(
                    copy_element
                )

        return references

    def find_best_article(self, element, articles):
        if not articles:
            return None
        y = self.get_y(element)
        return min(articles, key=lambda a: abs(y - a["reference_y"]))


    def build(self, classified):
        """
        Construit les articles à partir des éléments OCR classifiés.

        Supporte les deux formats :

        FORMAT NOUVEAU :
            Référence | Désignation | Quantité | PU | Total

        FORMAT ANCIEN :
            Désignation | TVA | PU | Qté | Total

        Corrections :
        - fusion des références OCR proches
        - affectation par Y
        - arrêt réel avant le pied de facture
        - protection du dernier article contre les coordonnées
        fournisseur / RIB / téléphone / email / mentions légales
        """

        if not classified:
            return []

        # ==========================================================
        # 1. NETTOYAGE
        # ==========================================================

        elements = []

        for element in classified:

            text = self.normalize(element.get("text", ""))

            if not text:
                continue

            if self.is_header(text):
                continue

            if (
                element.get("x") is None
                and element.get("box") is None
            ):
                continue

            element = element.copy()

            element["x"] = self.get_x(element)
            element["y"] = self.get_y(element)

            elements.append(element)

        if not elements:
            return []

        # ======================================================
        # 2. DETECTER LE TYPE DE FACTURE
        # ======================================================

        explicit_reference_mode = (
            self.has_explicit_reference_column(
                elements
            )
        )

        # ======================================================
        # 3. ANCIEN FORMAT
        # ======================================================

        if not explicit_reference_mode:

            return self.build_old_format(
                elements
            )

        # ======================================================
        # 4. NOUVEAU FORMAT
        # ======================================================

        reference_elements = (
            self.find_reference_elements(
                elements,
                explicit_reference_mode=True
            )
        )

        if not reference_elements:
            return []

        # ==========================================================
        # 5. FUSION REFERENCES DUPLIQUEES
        # ==========================================================

        merged_references = []

        REFERENCE_Y_TOLERANCE = 18

        for ref_element in reference_elements:

            text = ref_element.get("detected_reference")

            if not text:
                text = self.normalize(
                    ref_element.get("text", "")
                )

            text = self.normalize(text)

            if not text:
                continue

            y = self.get_y(ref_element)

            duplicate = None

            for existing in merged_references:

                existing_y = existing["reference_y"]
                existing_ref = existing["reference"]

                # Même référence
                if existing_ref == text:
                    duplicate = existing
                    break

                # Même ligne OCR
                if abs(existing_y - y) <= REFERENCE_Y_TOLERANCE:
                    duplicate = existing
                    break

            if duplicate is not None:

                old_score = duplicate.get("score", 0)
                new_score = ref_element.get("score", 0)

                if new_score > old_score:

                    duplicate["reference"] = text
                    duplicate["reference_element"] = ref_element
                    duplicate["score"] = new_score

                continue

            merged_references.append({
                "reference": text,
                "reference_y": y,
                "reference_element": ref_element,
                "score": ref_element.get("score", 0),
            })

        if not merged_references:
            return self.build_old_format(elements)

        merged_references.sort(
            key=lambda article: article["reference_y"]
        )

        # ==========================================================
        # 6. CREATION ARTICLES
        # ==========================================================

        articles = []

        for article in merged_references:

            articles.append({
                "reference": article["reference"],
                "reference_y": article["reference_y"],
                "elements": [],
            })

        # ==========================================================
        # 7. DETECTION DU DEBUT DU PIED DE FACTURE
        # ==========================================================

        # Mots/expressions qui annoncent généralement le pied
        # de facture.
        footer_markers = [
            "SIEGE SOCIAL",
            "SIEGE SOC",
            "SLEGO SOCIAL",
            "SLEGO SOCLAL",
            "ADRESSE",
            "TEL",
            "TELEPHONE",
            "FAX",
            "EMAIL",
            "E-MAIL",
            "RIB",
            "ICE",
            "I.C.E",
            "I.F",
            "IF",
            "R.C",
            "RC",
            "PATENTE",
            "C.N.S.S",
            "CNSS",
            "SARL",
            "SARL AU CAPITAL",
            "CAPITAL DE",
            "MODE DE REGLEMENT",
            "MODE DE REGLEMENT",
            "NOS MARCHANDISES",
            "NE SERONT NI RENDUES",
            "NE SERONT NI ECHANGEES",
            "GARANTIE",
            "MAGASINIER",
            "ARRÊTEE LA PRESENTE FACTURE",
            "ARRETEE LA PRESENTE FACTURE",
            "NET A PAYER",
            "NET A PAYE",
            "TOTAL HT",
            "TOTAL H T",
            "TOTAL TVA",
            "TOTAL TTC",
        ]

        def looks_like_footer(text):
            normalized = self.normalize(text)

            if not normalized:
                return False

            # Stop classique
            if self.is_stop(normalized):
                return True

            # Recherche de marqueurs
            for marker in footer_markers:
                if marker in normalized:
                    return True

            # Email
            if "@" in normalized:
                return True

            # RIB très long
            if "RIB" in normalized and len(normalized) > 15:
                return True

            # ICE / CNSS / RC / IF avec beaucoup de chiffres
            compact = self.compact(normalized)

            if (
                ("ICE" in compact or "CNSS" in compact or "PATENTE" in compact)
                and sum(c.isdigit() for c in compact) >= 5
            ):
                return True

            return False

        # ==========================================================
        # 8. CALCUL DU Y DE FIN DU TABLEAU
        # ==========================================================

        footer_y = None

        # On cherche les éléments qui ressemblent clairement
        # au pied de facture.
        for element in sorted(
            elements,
            key=lambda e: self.get_y(e)
        ):

            text = self.normalize(
                element.get("text", "")
            )

            if looks_like_footer(text):

                y = self.get_y(element)

                # On ne prend le marqueur que s'il est situé
                # après au moins une référence.
                if y >= articles[0]["reference_y"]:

                    footer_y = y
                    break

        # ======================================================
        # INTERVALLES Y
        # ======================================================

        for i, article in enumerate(articles):

            current_y = article["reference_y"]

            if i < len(articles) - 1:
                next_y = articles[
                    i + 1
                ]["reference_y"]
            else:
                next_y = float("inf")

            article["start_y"] = current_y - 10

            if next_y != float("inf"):
                article["end_y"] = next_y - 3
            else:
                article["end_y"] = float("inf")
        

        # ==========================================================
        # 10. ASSIGNATION DES ELEMENTS
        # ==========================================================

        for element in elements:

            text = self.normalize(
                element.get("text", "")
            )

            if not text:
                continue

            y = self.get_y(element)

            # ------------------------------------------------------
            # STOP GLOBAL
            # ------------------------------------------------------

            if footer_y is not None and y >= footer_y:
                continue

            if self.is_stop(text):
                continue

            if looks_like_footer(text):
                continue

            # ------------------------------------------------------
            # IGNORER LA REFERENCE ELLE-MEME
            # ------------------------------------------------------

            is_reference_element = False

            for article in articles:

                reference = article["reference"]

                if (
                    text == reference
                    and abs(
                        y - article["reference_y"]
                    ) <= REFERENCE_Y_TOLERANCE
                ):
                    is_reference_element = True
                    break

            if is_reference_element:
                continue

            # ------------------------------------------------------
            # ASSIGNATION PAR INTERVALLE
            # ------------------------------------------------------

            assigned = False

            for article in articles:

                if (
                    y >= article["start_y"]
                    and y < article["end_y"]
                ):

                    article["elements"].append(element)

                    assigned = True
                    break

            # ------------------------------------------------------
            # FALLBACK PROXIMITE
            # ------------------------------------------------------

            if not assigned:

                best_article = self.find_best_article(
                    element,
                    articles
                )

                if best_article:

                    distance = abs(
                        y - best_article["reference_y"]
                    )

                    # IMPORTANT :
                    # ne jamais rattacher un élément
                    # situé après le pied
                    if (
                        footer_y is None
                        or y < footer_y
                    ):

                        if distance <= 100:

                            best_article["elements"].append(
                                element
                            )

        # ==========================================================
        # 11. RESULTAT FINAL
        # ==========================================================

        result = []

        for article in articles:

            elements_article = article["elements"].copy()

            # ------------------------------------------------------
            # Suppression doublons OCR
            # ------------------------------------------------------

            unique = []

            seen = set()

            for element in elements_article:

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
                    element.get("column")
                )

                if key in seen:
                    continue

                seen.add(key)
                unique.append(element)

            # ------------------------------------------------------
            # TRI
            # ------------------------------------------------------

            unique.sort(
                key=lambda e: (
                    self.get_y(e),
                    self.get_x(e)
                )
            )

            result.append({
                "reference": article["reference"],
                "reference_y": article["reference_y"],
                "elements": unique,
            })

            if article["reference"] == "HP-W2072A":

                print("\n" + "=" * 100)
                print("DEBUG DERNIER ARTICLE : HP-W2072A")
                print("=" * 100)

                for e in unique:
                    print(
                        f"Y={self.get_y(e):8.1f} | "
                        f"X={self.get_x(e):8.1f} | "
                        f"COL={str(e.get('column')):20} | "
                        f"TEXT={e.get('text', '')}"
                    )

                print("=" * 100)

        return result

    def build_old_format(self, elements):
        rows = defaultdict(list)
        for element in elements:
            rows[round(self.get_y(element) / self.tolerance_y)].append(element)

        grouped = []
        for _, row in sorted(rows.items()):
            row.sort(key=self.get_x)
            grouped.append(row)

        articles = []
        current = None
        for row in grouped:
            if not row:
                continue
            text = " ".join(self.normalize(e.get("text", "")) for e in row)
            if self.is_stop(text):
                if current is not None:
                    articles.append(current)
                break

            reference = self.get_old_format_reference(
                row
            )

            if reference:
                if current is not None:
                    articles.append(current)
                ref_y = next(
                    (self.get_y(e) for e in row
                     if (e.get("detected_reference") or self.extract_reference_from_text(e.get("text", ""))) == reference),
                    self.get_y(row[0]),
                )
                current = {
                    "reference": reference,
                    "reference_y": ref_y,
                    "elements": list(row),
                }
            elif current is not None:
                current["elements"].extend(row)

        if current is not None:
            articles.append(current)

        for article in articles:
            unique = []
            seen = set()
            for element in article["elements"]:
                key = (
                    element.get("text", ""),
                    round(self.get_x(element), 2),
                    round(self.get_y(element), 2),
                    element.get("column", ""),
                )
                if key not in seen:
                    seen.add(key)
                    unique.append(element)
            unique.sort(key=lambda e: (self.get_y(e), self.get_x(e)))
            article["elements"] = unique
        return articles

    def format_article(self, elements):
        if not elements:
            return {"reference": None, "elements": []}
        return {"reference": self.get_row_reference(elements), "elements": elements}

    def get_element_x(self, element):

        if element.get("x") is not None:
            try:
                return float(element["x"])
            except (ValueError, TypeError):
                pass

        box = element.get("box")

        if box and len(box) >= 4:
            try:
                return (
                    float(box[0]) +
                    float(box[2])
                ) / 2
            except (ValueError, TypeError):
                pass

        return None

    def get_element_y(self, element):

        if element.get("y") is not None:
            try:
                return float(element["y"])
            except (ValueError, TypeError):
                pass

        box = element.get("box")

        if box and len(box) >= 4:
            try:
                return (
                    float(box[1]) +
                    float(box[3])
                ) / 2
            except (ValueError, TypeError):
                pass

        return None

    def find_total_in_line(
        self,
        ligne,
        current_quantity=None,
        current_unit_price=None
    ):
        """
        Recherche robuste du total article.

        Priorité :

        1. colonne total explicite
        2. montant / montant TTC
        3. colonne inconnue mais positionnée après le PU
        4. aucune valeur
        """

        candidates = []

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

            if not self.is_valid_price(value):
                continue

            colonne = cellule.get(
                "column",
                ""
            )

            # ----------------------------------------------------
            # PRIORITE MAXIMALE :
            # colonne explicitement TOTAL / MONTANT
            # ----------------------------------------------------

            if self.is_total_column(colonne):

                candidates.append({
                    "value": value,
                    "priority": 100,
                    "x": self.get_element_x(cellule),
                    "element": cellule,
                })

        if candidates:

            candidates.sort(
                key=lambda item: -item["priority"]
            )

            return candidates[0]["value"]

        return None

    def has_explicit_reference_column(self, elements):
        """
        Détermine si le document possède une vraie colonne
        'reference'.
        """

        for element in elements:
            if element.get("column") == "reference":
                text = self.normalize(
                    element.get("text", "")
                )

                if self.is_reference(text):
                    return True

        return False

    def is_numeric_column(self, element):
        column = element.get("column", "")

        return column in {
            "tva",
            "pu",
            "qte",
            "total"
        }

    def is_designation_element(
        self,
        element,
        article,
        explicit_reference_mode=False
    ):
        text = self.normalize(
            element.get("text", "")
        )

        if not text:
            return False

        column = element.get("column", "")

        # Les vraies références ne sont jamais
        # des morceaux de désignation
        if column == "reference":
            return False

        # Ne jamais reprendre la référence seule
        if text == article["reference"]:
            return False

        # Les colonnes numériques ne sont pas
        # des désignations
        if self.is_numeric_column(element):
            return False

        # Dans les deux formats, une cellule déjà
        # identifiée comme designation est valide
        if column == "designation":
            return True

        # ----------------------------------------------------------
        # Tolérance pour les lignes de continuation
        # ----------------------------------------------------------

        x = self.get_x(element)
        y = self.get_y(element)

        ref_y = article["reference_y"]

        # Une continuation doit rester proche verticalement
        if y >= ref_y and y - ref_y <= 120:

            # Zone gauche du tableau
            # Les nombres sont généralement beaucoup plus à droite.
            if x < 750:
                return True

        return False

    def extract_designation_from_elements(
        self,
        ligne,
        reference=""
    ):
        parts = []

        for cellule in ligne:

            texte = self.normalize_text(
                cellule.get("text", "")
            )

            if not texte:
                continue

            colonne = cellule.get(
                "column",
                ""
            )

            # --------------------------------------------------
            # Ne jamais prendre la référence seule
            # --------------------------------------------------

            if reference and texte.upper() == reference.upper():
                continue

            # --------------------------------------------------
            # Colonnes numériques
            # --------------------------------------------------

            if colonne in {
                "tva",
                "pu",
                "qte",
                "total"
            }:
                continue

            # --------------------------------------------------
            # Référence explicite
            # --------------------------------------------------

            if colonne == "reference":
                continue

            # --------------------------------------------------
            # Désignation
            # --------------------------------------------------

            if colonne == "designation":
                parts.append(
                    texte
                )
                continue

            # --------------------------------------------------
            # Tolérance pour les lignes de continuation
            # --------------------------------------------------

            x = cellule.get("x")

            if x is not None and x < 750:
                parts.append(
                    texte
                )

        return self.clean_designation(
            " ".join(parts)
        )

    def is_inside_article_table(self, element):
        """
        Vérifie que l'élément se trouve dans la zone
        normale du tableau des articles.
        """

        y = self.get_y(element)
        x = self.get_x(element)

        # Les factures testées ont leurs articles
        # dans la partie centrale du document.
        #
        # On ne garde pas les éléments très éloignés
        # du tableau.

        if y < 500:
            return False

        return True

    def get_old_format_reference(self, row):
        """
        Détecte une référence uniquement lorsqu'elle apparaît
        au début / dans la zone gauche de la ligne.

        Exemple valide :
            HP-F6V25AE-Cartouche HP 652 Black

        Exemple invalide :
            TAMBOURRICOHAFICIO1515CET
        """

        if not row:
            return None

        # Trier par X
        sorted_row = sorted(
            row,
            key=lambda e: self.get_x(e)
        )

        for element in sorted_row:

            text = self.normalize(
                element.get("text", "")
            )

            if not text:
                continue

            x = self.get_x(element)

            # Une référence d'ancien format doit être
            # dans la zone gauche du tableau.
            if x > 750:
                continue

            reference = (
                self.extract_reference_from_text(
                    text
                )
            )

            if reference:
                return reference

        return None