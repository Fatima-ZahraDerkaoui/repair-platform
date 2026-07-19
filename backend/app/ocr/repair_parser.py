import re
from typing import Any


class RepairParser:

    def parse(self, texts: list[str]) -> dict[str, Any]:

        # Nettoyage
        texts = [
            text.strip()
            for text in texts
            if text and text.strip()
        ]

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

        # -----------------------------
        # DATE
        # -----------------------------

        for text in texts:

            match = re.search(
                r"Date\s*:\s*(\d{1,2}\s*/\s*\d{1,2}\s*/\s*\d{4})",
                text,
                re.IGNORECASE
            )

            if match:

                data["date_reception"] = (
                    match.group(1)
                )

                break

        # -----------------------------
        # NOM
        # -----------------------------

        for index, text in enumerate(texts):

            if "Nom et prénom" in text:

                if index + 1 < len(texts):

                    data["nom"] = texts[index + 1]

                break

        # -----------------------------
        # TELEPHONE
        # -----------------------------

        for index, text in enumerate(texts):

            if "Téléphone" in text:

                if index + 1 < len(texts):

                    telephone = texts[index + 1]

                    data["telephone"] = (
                        telephone
                    )

                break

        # -----------------------------
        # MOT DE PASSE
        # -----------------------------

        for index, text in enumerate(texts):

            if "Mot de passe" in text:

                if index + 1 < len(texts):

                    data["mot_de_passe"] = (
                        texts[index + 1]
                    )

                break

        # -----------------------------
        # TYPE DE MATERIEL
        # -----------------------------

        material_types = [

            "PC",

            "PC Portable",

            "Unité centrale",

            "Imprimante"

        ]

        for text in texts:

            clean_text = text.lower()

            if "☑ pc portable" in clean_text:

                data["type_materiel"] = (
                    "PC Portable"
                )

                break

            elif "☑ pc" in clean_text:

                data["type_materiel"] = "PC"

                break

            elif "☑ unité centrale" in clean_text:

                data["type_materiel"] = (
                    "Unité centrale"
                )

                break

            elif "☑ imprimante" in clean_text:

                data["type_materiel"] = (
                    "Imprimante"
                )

                break

        # -----------------------------
        # SYSTEME EXPLOITATION
        # -----------------------------

        operating_systems = [

            "Windows 10",

            "Windows 11",

            "Linux"

        ]

        for text in texts:

            for system in operating_systems:

                if system.lower() in text.lower():

                    data["systeme_exploitation"] = system

                    break

            if data["systeme_exploitation"]:

                break

        # -----------------------------
        # OFFICE
        # -----------------------------

        office_versions = [

            "Office 2013",

            "Office 2024",

            "Microsoft 365"

        ]

        for text in texts:

            for office in office_versions:

                if office.lower() in text.lower():

                    data["version_office"] = office

                    break

            if data["version_office"]:

                break

        # -----------------------------
        # ORIGINE PROBLEME
        # -----------------------------

        origins = [

            "Matériel",

            "Logiciel",

            "Réseau",

            "Virus",

            "Mise à jour",

            "Inconnue"

        ]

        for text in texts:

            for origin in origins:

                if origin.lower() in text.lower():

                    data["origine_probleme"] = origin

                    break

            if data["origine_probleme"]:

                break

        # -----------------------------
        # INTERVENTIONS
        # -----------------------------

        interventions = [

            "Réinstallation",

            "Récupération de données",

            "Configuration Boites Mails",

            "Désinstallation",

            "Nettoyage",

            "Configuration Réseau",

            "Dépannage",

            "Formatage C",

            "Mise à jour",

            "Sauvegarde",

            "Formatage D",

            "Suppression de virus"

        ]

        for text in texts:

            for intervention in interventions:

                if intervention.lower() in text.lower():

                    data["intervention"].append(
                        intervention
                    )

        # -----------------------------
        # PROBLEME
        # -----------------------------

        for index, text in enumerate(texts):

            if "PROBLÈME CONSTATÉ" in text:

                if index + 1 < len(texts):

                    data["probleme"] = (
                        texts[index + 1]
                    )

                break

        # -----------------------------
        # PIECES DEFECTUEUSES
        # -----------------------------

        for index, text in enumerate(texts):

            if "PIÈCES DÉFECTUEUSES" in text:

                if index + 1 < len(texts):

                    data["pieces_defectueuses"] = (

                        texts[index + 1]

                    )

                break

        # -----------------------------
        # REMARQUES
        # -----------------------------

        for index, text in enumerate(texts):

            if "REMARQUES SUPPLÉMENTAIRES" in text:

                if index + 1 < len(texts):

                    data["remarques"] = (

                        texts[index + 1]

                    )

                break

        # -----------------------------
        # URGENT
        # -----------------------------

        for text in texts:

            if "URGENTE" in text.upper():

                data["urgent"] = True

                break

        return data