class RepairParser:

    def parse(self, ocr_results, checkbox_results):

        texts = []

        for item in ocr_results:

            if isinstance(item, dict):

                text = item.get("text", "")

            else:

                text = str(item)

            if text.strip():

                texts.append(text.strip())

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

        # OCR
        self.parse_text_fields(
            texts,
            data
        )

        # Cases cochées
        data["type_materiel"] = self.get_single_value(
            checkbox_results.get("type_materiel", [])
        )

        data["systeme_exploitation"] = self.get_single_value(
            checkbox_results.get("systeme_exploitation", [])
        )

        data["version_office"] = self.get_single_value(
            checkbox_results.get("office", [])
        )

        data["origine_probleme"] = self.get_single_value(
            checkbox_results.get("origine_probleme", [])
        )

        data["intervention"] = checkbox_results.get(
            "intervention",
            []
        )

        data["urgent"] = (
            "OUI" in checkbox_results.get("urgent", [])
        )

        data["resolu"] = (
            "OUI" in checkbox_results.get("resolu", [])
        )

        return data

    def get_single_value(self, values):

        if values:

            return values[0]

        return None