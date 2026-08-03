import re

class ArticleParser:

    REFERENCES = (
        "HP",
        "EPST",
        "CANGI",
        "CAN",
        "BRO",
        "LEX",
        "OKI",
        "KYO",
        "RIC",
        "XER",
        "PAN",
        "SAM",
        "TOS"
    )

    # -------------------------------------------------------

    @staticmethod
    def to_float(value):

        value = value.replace(" ", "")
        value = value.replace(",", ".")

        try:
            return float(value)
        except:
            return None

    # -------------------------------------------------------

    @staticmethod
    def is_reference(text):

        text = text.upper().strip()

        return text.startswith(ArticleParser.REFERENCES)

    # -------------------------------------------------------

    @staticmethod
    def is_price(text):

        return re.fullmatch(
            r"\d+[,.]\d{2}",
            text.replace(" ", "")
        ) is not None

    # -------------------------------------------------------

    @staticmethod
    def is_quantity(text):

        return re.fullmatch(r"\d+", text) is not None

    # -------------------------------------------------------

    @staticmethod
    def is_tva(text):

        return "%" in text

    # -------------------------------------------------------
    @classmethod
    def parse_line(cls, ligne):

        ligne = sorted(
            ligne,
            key=lambda c: c["box"][0]
        )

        textes = [c["text"].strip() for c in ligne]

        reference = None
        designation = []

        tva = ""
        prix = None
        quantite = None
        total = None

        prix_list = []
        nombres_entiers = []

        # ----------------------------------------------------
        # Recherche des informations
        # ----------------------------------------------------

        for t in textes:

            if cls.is_tva(t):
                tva = t
                continue

            if cls.is_price(t):
                prix_list.append(t)
                continue

            if cls.is_quantity(t):
                nombres_entiers.append(int(t))
                continue

            # --------------------------------------------
            # Référence
            # --------------------------------------------

            if reference is None and cls.is_reference(t):

                # HP-F6V25AE-Cartouche HP 652 Black
                # EPST103BK - ....
                # CANGI490M-CARTOUCHE ....

                m = re.match(
                    r"^([A-Z0-9\-]+)\s*[-=]\s*(.*)$",
                    t,
                    re.IGNORECASE
                )

                if m:

                    reference = m.group(1).strip()

                    reste = m.group(2).strip()

                    if reste:
                        designation.append(reste)

                else:

                    morceaux = t.split(maxsplit=1)

                    reference = morceaux[0].strip()

                    if len(morceaux) > 1:

                        reste = morceaux[1]

                        # supprimer uniquement le premier tiret éventuel
                        reste = re.sub(r"^\-\s*", "", reste)

                        designation.append(reste.strip())

                continue

            # --------------------------------------------
            # Désignation
            # --------------------------------------------

            designation.append(t)

        # ----------------------------------------------------
        # Prix
        # ----------------------------------------------------

        if len(prix_list) >= 2:

            prix = cls.to_float(prix_list[0])
            total = cls.to_float(prix_list[-1])

        elif len(prix_list) == 1:

            prix = cls.to_float(prix_list[0])

        # ----------------------------------------------------
        # Quantité
        # ----------------------------------------------------

        candidats = [
            n for n in nombres_entiers
            if 1 <= n <= 100
        ]

        if candidats:
            quantite = candidats[-1]

        # ----------------------------------------------------
        # Nettoyage de la désignation
        # ----------------------------------------------------

        designation = cls.clean_designation(designation)

        if reference is None:
            return None

        return {

            "reference": reference,

            "designation": designation,

            "prix_unitaire": prix,

            "quantite": quantite,

            "tva": tva,

            "total": total

        }

    # -------------------------------------------------------
    @staticmethod
    def clean_designation(parts):

        # --------------------------------------------
        # Si on reçoit une liste -> texte
        # --------------------------------------------

        if isinstance(parts, list):
            designation = " ".join(parts)
        else:
            designation = parts

        designation = re.sub(r"\s+", " ", designation).strip()

        mots = []

        for p in designation.split():

            # bruit OCR
            if len(p) == 1 and not p.isalpha():
                continue

            # supprimer les faux nombres isolés
            if re.fullmatch(r"\d+", p):
                if len(p) <= 2:
                    continue

            mots.append(p)

        designation = " ".join(mots)

        # -------------------------------------------------
        # déplacer le modèle imprimante à la fin
        # -------------------------------------------------

        modele = re.search(
            r"(L\d+(?:/\w+)+(?:\s+\w+)?)",
            designation,
            re.IGNORECASE
        )

        if modele:

            modele_txt = modele.group(1)

            designation = designation.replace(
                modele_txt,
                ""
            ).strip()

            designation = f"{designation} {modele_txt}"

        # -------------------------------------------------
        # Corriger "103 L3150" -> "103 pour L3150"
        # -------------------------------------------------

        designation = re.sub(
            r"(103)\s+(L\d)",
            r"\1 pour \2",
            designation
        )

        # -------------------------------------------------
        # supprimer plusieurs "pour"
        # -------------------------------------------------

        designation = re.sub(
            r"(pour\s+)+",
            "pour ",
            designation,
            flags=re.IGNORECASE
        )

        # -------------------------------------------------
        # espaces
        # -------------------------------------------------

        designation = re.sub(
            r"\s+",
            " ",
            designation
        ).strip()

        return designation
    