import re
from datetime import datetime


class RepairParser:

    def parse(self, ocr_results):

        # ==========================================
        # 1. EXTRACTION DES TEXTES OCR
        # ==========================================

        texts = []

        for item in ocr_results:

            if isinstance(item, dict):
                text = item.get("text", "")
            else:
                text = str(item)

            if text.strip():
                texts.append(text.strip())

        # ==========================================
        # 2. STRUCTURE DES DONNÉES
        # ==========================================

        data = {
            "date_reception": None,
            "nom": None,
            "telephone": None,
            "type_materiel": None,
            "mot_de_passe": None,
            "systeme_exploitation": None,
            "version_office": None,
            "origine_probleme": None,
            "intervention": [],
            "probleme": None,
            "pieces_defectueuses": None,
            "remarques": None,
            "urgent": False,
            "resolu": False
        }

        # ==========================================
        # 3. DATE
        # ==========================================

        for text in texts:

            match = re.search(
                r"Date\s*:\s*(\d{1,2})\s*/\s*(\d{1,2})\s*/\s*(\d{4})",
                text,
                re.IGNORECASE
            )

            if match:

                jour = int(match.group(1))
                mois = int(match.group(2))
                annee = int(match.group(3))

                try:

                    date_obj = datetime(
                        annee,
                        mois,
                        jour
                    )

                    data["date_reception"] = (
                        date_obj.strftime("%Y-%m-%d")
                    )

                except ValueError:

                    data["date_reception"] = None

                break

        # ==========================================
        # 4. NOM
        # ==========================================

        for index, text in enumerate(texts):

            if "Nom et prénom" in text:

                if index + 1 < len(texts):

                    data["nom"] = texts[index + 1]

                break

        # ==========================================
        # 5. TELEPHONE
        # ==========================================

        for index, text in enumerate(texts):

            if "Téléphone" in text:

                if index + 1 < len(texts):

                    telephone = texts[index + 1]

                    # Nettoyage éventuel
                    telephone = re.sub(
                        r"[^\d+ ]",
                        "",
                        telephone
                    ).strip()

                    data["telephone"] = telephone

                break

        # ==========================================
        # 6. MOT DE PASSE
        # ==========================================

        for index, text in enumerate(texts):

            if "Mot de passe" in text:

                if index + 1 < len(texts):

                    data["mot_de_passe"] = texts[index + 1]

                break

        # ==========================================
        # 7. TYPE DE MATÉRIEL
        # ==========================================

        types_materiel = [
            "PC",
            "PC Portable",
            "Imprimante",
            "Unité centrale"
        ]

        for text in texts:

            text_clean = text.strip()

            # Cas d'une case cochée
            if "☑" in text_clean:

                valeur = text_clean.replace("☑", "").strip()

                if valeur in types_materiel:

                    data["type_materiel"] = valeur

                    break

        # ==========================================
        # 8. SYSTÈME D'EXPLOITATION
        # ==========================================

        systemes = [

            "Windows 10",
            "Windows 11",
            "Linux"

        ]

        for text in texts:

            if text in systemes:

                data["systeme_exploitation"] = text

                break

        # ==========================================
        # 9. VERSION OFFICE
        # ==========================================

        versions_office = [

            "Office 2013",
            "Office 2024",
            "Microsoft 365"

        ]

        for text in texts:

            if text in versions_office:

                data["version_office"] = text

                break

        # ==========================================
        # 10. ORIGINE DU PROBLÈME
        # ==========================================

        origins = [

            "Matériel",
            "Logiciel",
            "Réseau",
            "Virus",
            "Mise à jour",
            "Inconnue"

        ]

        for text in texts:

            if text in origins:

                data["origine_probleme"] = text

                break

        # ==========================================
        # 11. INTERVENTIONS
        # ==========================================

        interventions = {

            "Réinstallation",
            "Récupération de données",
            "Configuration Boites Mails",
            "Désinstallation",
            "Nettoyage",
            "Configuration Réseau (wifi, CPL, ...)",
            "Dépannage",
            "Formatage C",
            "Mise à jour",
            "Sauvegarde",
            "Formatage D",
            "Suppression de virus"

        }

        for text in texts:

            if text in interventions:

                # Éviter les doublons
                if text not in data["intervention"]:

                    data["intervention"].append(text)

        # ==========================================
        # 12. PROBLÈME
        # ==========================================

        problem_index = None

        for index, text in enumerate(texts):

            if "PROBLÈME CONSTATÉ" in text.upper():

                problem_index = index

                break

        if problem_index is not None:

            if problem_index + 1 < len(texts):

                data["probleme"] = texts[problem_index + 1]

        # ==========================================
        # 13. PIÈCES DÉFECTUEUSES + REMARQUES
        # ==========================================

        pieces_index = None
        remarques_index = None

        for index, text in enumerate(texts):

            upper_text = text.upper()

            if "PIÈCES DÉFECTUEUSES" in upper_text:

                pieces_index = index

            if "REMARQUES SUPPLÉMENTAIRES" in upper_text:

                remarques_index = index


        # ------------------------------------------
        # PIÈCES DÉFECTUEUSES
        # ------------------------------------------

        if pieces_index is not None:

            # Si la valeur est après le titre
            # mais que le titre Remarques vient juste après,
            # on cherche après le titre Remarques

            if remarques_index == pieces_index + 1:

                if remarques_index + 1 < len(texts):

                    data["pieces_defectueuses"] = (
                        texts[remarques_index + 1]
                    )

            else:

                if pieces_index + 1 < len(texts):

                    data["pieces_defectueuses"] = (
                        texts[pieces_index + 1]
                    )


        # ------------------------------------------
        # REMARQUES
        # ------------------------------------------

        if remarques_index is not None:

            if remarques_index + 2 < len(texts):

                data["remarques"] = (
                    texts[remarques_index + 2]
                )

        # ==========================================
        # 15. URGENCE
        # ==========================================

        for index, text in enumerate(texts):

            if "URGENTE" in text.upper():

                # Vérifier les textes suivants
                for next_text in texts[index + 1:index + 4]:

                    next_text = next_text.upper().strip()

                    if "☑ OUI" in next_text:

                        data["urgent"] = True
                        break

                    elif "☑ NON" in next_text:

                        data["urgent"] = False
                        break

                break

        # ==========================================
        # 16. PROBLÈME RÉSOLU
        # ==========================================

        for index, text in enumerate(texts):

            if "PROBLÈME RÉSOLU" in text.upper():

                for next_text in texts[index + 1:index + 4]:

                    next_text = next_text.upper().strip()

                    if "☑ OUI" in next_text:

                        data["resolu"] = True
                        break

                    elif "☑ NON" in next_text:

                        data["resolu"] = False
                        break

                break

            return data