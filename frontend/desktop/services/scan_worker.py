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

        super().__init__(
            parent
        )

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

            # =================================================
            # BOUCLE D'ATTENTE
            # =================================================

            while self.running:

                try:

                    status = BackendAPI.get_session_status(
                        self.session_id
                    )

                except Exception as e:

                    # Une erreur réseau temporaire ne doit
                    # PAS arrêter le scan immédiatement.

                    self.progress.emit(
                        "Connexion au serveur..."
                    )

                    print(
                        "[SCAN] Erreur temporaire statut :",
                        e
                    )

                    time.sleep(3)

                    continue

                if not isinstance(
                    status,
                    dict
                ):

                    raise ValueError(
                        "Réponse invalide du serveur."
                    )

                etat = str(
                    status.get(
                        "status",
                        ""
                    )
                ).upper()

                # =============================================
                # WAITING
                # =============================================

                if etat == "WAITING":

                    self.progress.emit(
                        "En attente de la facture..."
                    )

                # =============================================
                # PROCESSING
                # =============================================

                elif etat == "PROCESSING":

                    self.progress.emit(
                        "Facture reçue. Analyse OCR en cours..."
                    )

                # =============================================
                # READY
                # =============================================

                elif etat == "READY":

                    self.progress.emit(
                        "Analyse terminée. Récupération du résultat..."
                    )

                    try:

                        resultat = (
                            BackendAPI.get_facture_result(
                                self.session_id
                            )
                        )

                    except Exception as e:

                        self.error.emit(
                            f"Impossible de récupérer le résultat OCR : {e}"
                        )

                        return

                    if not isinstance(
                        resultat,
                        dict
                    ):

                        raise ValueError(
                            "Résultat OCR invalide."
                        )

                    self.finished.emit(
                        resultat
                    )

                    return

                # =============================================
                # ERROR
                # =============================================

                elif etat == "ERROR":

                    # IMPORTANT :
                    # Le backend retourne actuellement HTTP 500
                    # pour /result lorsque status == ERROR.
                    #
                    # On récupère donc directement le message
                    # via la réponse HTTP dans BackendAPI.
                    #
                    # Pour le moment, message générique.

                    self.error.emit(
                        "Le scan de la facture a échoué. "
                        "Vérifiez les logs du serveur OCR."
                    )

                    return

                # =============================================
                # SESSION INCONNUE / AUTRE
                # =============================================

                else:

                    self.progress.emit(
                        f"État de la session : {etat}"
                    )

                # =================================================
                # ATTENTE
                # =================================================

                time.sleep(
                    2
                )

        except Exception as e:

            print(
                "[SCAN] ERREUR WORKER :",
                e
            )

            self.error.emit(
                str(e)
            )

    # =========================================================
    # STOP
    # =========================================================

    def stop(self):

        self.running = False