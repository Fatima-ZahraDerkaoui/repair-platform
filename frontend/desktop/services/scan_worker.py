import time

from PySide6.QtCore import QObject, Signal

from services.backend_api import BackendAPI


class ScanWorker(QObject):

    finished = Signal(dict)
    error = Signal(str)
    progress = Signal(str)

    def __init__(
        self,
        session_id,
        parent=None
    ):

        super().__init__(parent)

        self.session_id = session_id

        self.running = True

    # =========================================================
    # RUN
    # =========================================================

    def run(self):

        try:

            self.progress.emit(
                "En attente de la facture envoyée depuis le téléphone..."
            )

            while self.running:

                status = BackendAPI.get_session_status(
                    self.session_id
                )

                etat = status.get(
                    "status",
                    ""
                ).upper()

                # -------------------------------------------------
                # ATTENTE
                # -------------------------------------------------

                if etat == "WAITING":

                    self.progress.emit(
                        "En attente de la facture..."
                    )

                # -------------------------------------------------
                # OCR EN COURS
                # -------------------------------------------------

                elif etat == "PROCESSING":

                    self.progress.emit(
                        "Facture reçue. Analyse OCR en cours..."
                    )

                # -------------------------------------------------
                # TERMINE
                # -------------------------------------------------

                elif etat == "READY":

                    self.progress.emit(
                        "Analyse terminée. Récupération du résultat..."
                    )

                    resultat = (
                        BackendAPI.get_facture_result(
                            self.session_id
                        )
                    )

                    self.finished.emit(
                        resultat
                    )

                    return

                # -------------------------------------------------
                # ERREUR
                # -------------------------------------------------

                elif etat == "ERROR":

                    self.error.emit(
                        "Le serveur a rencontré une erreur "
                        "pendant l'analyse OCR."
                    )

                    return

                # -------------------------------------------------
                # ETAT INCONNU
                # -------------------------------------------------

                else:

                    self.progress.emit(
                        f"État de la session : {etat}"
                    )

                time.sleep(2)

        except Exception as e:

            self.error.emit(
                str(e)
            )

    # =========================================================
    # STOP
    # =========================================================

    def stop(self):

        self.running = False