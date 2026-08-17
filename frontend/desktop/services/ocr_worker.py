from PySide6.QtCore import QObject, Signal, Slot


class OCRWorker(QObject):

    finished = Signal(dict)
    error = Signal(str)
    progress = Signal(str)

    def __init__(self, image_path):

        super().__init__()

        self.image_path = image_path

    @Slot()
    def run(self):

        try:

            self.progress.emit(
                "Envoi de la facture au serveur..."
            )

            from services.backend_api import BackendAPI

            self.progress.emit(
                "Analyse OCR en cours..."
            )

            response = BackendAPI.analyser_facture_direct(
                self.image_path
            )

            self.progress.emit(
                "Analyse terminée."
            )

            # =====================================================
            # VERIFICATION REPONSE
            # =====================================================

            if not isinstance(response, dict):

                raise ValueError(
                    "Réponse API invalide."
                )

            resultat = response.get(
                "resultat"
            )

            if not isinstance(resultat, dict):

                raise ValueError(
                    "Champ 'resultat' absent ou invalide."
                )

            data = resultat.get(
                "data"
            )

            if not isinstance(data, dict):

                raise ValueError(
                    "Champ 'data' absent ou invalide."
                )

            # =====================================================
            # RESULTAT UNIQUE
            # =====================================================

            self.finished.emit(
                data
            )

        except Exception as e:

            self.error.emit(
                str(e)
            )
            