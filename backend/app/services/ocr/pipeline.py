from app.services.ocr.facture_ocr_service import FactureOCRService


class OCRPipeline:

    def __init__(self):

        # =====================================================
        # SERVICE OCR FACTURE
        # =====================================================

        self.facture_ocr_service = FactureOCRService()

    # =========================================================
    # PIPELINE PRINCIPAL
    # =========================================================

    def process(self, image_path):

        print("=" * 80)
        print("OCR PIPELINE")
        print("=" * 80)

        print(
            "IMAGE PATH :",
            image_path
        )

        print(
            "TYPE IMAGE PATH :",
            type(image_path)
        )

        # =====================================================
        # UTILISER LE MEME PIPELINE QUE LE TEST
        # =====================================================

        data = self.facture_ocr_service.analyser(
            image_path
        )

        # =====================================================
        # RESULTAT FINAL
        # =====================================================

        return {
            "data": data
        }


# =============================================================
# INSTANCE GLOBALE
# =============================================================

pipeline = OCRPipeline()