from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    HRFlowable
)
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from datetime import datetime
import os


def generer_fiche_pdf(
    reparation,
    client,
    chemin_fichier
):

    os.makedirs(
        os.path.dirname(chemin_fichier),
        exist_ok=True
    )

    # =====================================================
    # DOCUMENT (MARGES OPTIMISÉES)
    # =====================================================

    doc = SimpleDocTemplate(
        chemin_fichier,
        pagesize=A4,
        rightMargin=12 * mm,
        leftMargin=12 * mm,
        topMargin=10 * mm,
        bottomMargin=10 * mm
    )

    styles = getSampleStyleSheet()

    # =====================================================
    # STYLES ÉPURÉS & MODERNES
    # =====================================================

    titre = ParagraphStyle(
        "Titre",
        parent=styles["Title"],
        fontSize=18,
        leading=22,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#0F172A"),
        fontName="Helvetica-Bold",
        spaceAfter=3
    )

    sous_titre = ParagraphStyle(
        "SousTitre",
        parent=styles["Normal"],
        fontSize=9,
        leading=11,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#64748B"),
        spaceAfter=10
    )

    section = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontSize=9.5,
        leading=12,
        textColor=colors.white,
        fontName="Helvetica-Bold",
        spaceBefore=0,
        spaceAfter=0
    )

    normal = ParagraphStyle(
        "NormalCustom",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1E293B")
    )

    label = ParagraphStyle(
        "Label",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#475569"),
        fontName="Helvetica-Bold"
    )

    valeur = ParagraphStyle(
        "Valeur",
        parent=styles["Normal"],
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0F172A")
    )

    # =====================================================
    # HELPERS
    # =====================================================

    def valeur_propre(value):
        if value is None or value == "":
            return " "
        return str(value)

    def section_title(text):
        table = Table(
            [[Paragraph(text.upper(), section)]],
            colWidths=[186 * mm]
        )
        table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#2563EB")),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        return table

    def info_table(rows):
        table = Table(
            rows,
            colWidths=[46 * mm, 140 * mm]
        )
        table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F8FAFC")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        return table

    # =====================================================
    # CONTENU
    # =====================================================

    elements = []

    # HEADER
    elements.append(
        Paragraph(
            "FICHE DE RÉCEPTION",
            titre
        )
    )

    elements.append(
        Paragraph(
            "Dossier de réparation informatique",
            sous_titre
        )
    )

    # DOSSIER
    numero = valeur_propre(
        getattr(
            reparation,
            "numero_dossier",
            None
        )
    )

    statut = valeur_propre(
        getattr(
            reparation,
            "statut",
            None
        )
    )

    date_creation = getattr(
        reparation,
        "date_creation",
        None
    )

    if date_creation:
        date_text = date_creation.strftime(
            "%d/%m/%Y %H:%M"
        )
    else:
        date_text = datetime.now().strftime(
            "%d/%m/%Y %H:%M"
        )

    elements.append(
        info_table([
            [
                Paragraph(
                    "<b>NUMÉRO DOSSIER</b>",
                    label
                ),
                Paragraph(
                    f"<b>{numero}</b>",
                    valeur
                )
            ],
            [
                Paragraph(
                    "DATE DE RÉCEPTION",
                    label
                ),
                Paragraph(
                    date_text,
                    valeur
                )
            ],
            [
                Paragraph(
                    "STATUT",
                    label
                ),
                Paragraph(
                    statut,
                    valeur
                )
            ]
        ])
    )

    elements.append(Spacer(1, 3 * mm))

    # CLIENT
    elements.append(
        section_title(
            "INFORMATIONS CLIENT"
        )
    )

    elements.append(
        info_table([
            [
                Paragraph(
                    "Nom complet",
                    label
                ),
                Paragraph(
                    valeur_propre(
                        getattr(
                            client,
                            "nom",
                            None
                        )
                    ),
                    valeur
                )
            ],
            [
                Paragraph(
                    "Téléphone",
                    label
                ),
                Paragraph(
                    valeur_propre(
                        getattr(
                            client,
                            "telephone",
                            None
                        )
                    ),
                    valeur
                )
            ]
        ])
    )

    elements.append(Spacer(1, 3 * mm))

    # MATÉRIEL
    elements.append(
        section_title(
            "INFORMATIONS DU MATÉRIEL"
        )
    )

    elements.append(
        info_table([
            [
                Paragraph(
                    "Type de matériel",
                    label
                ),
                Paragraph(
                    valeur_propre(
                        getattr(
                            reparation,
                            "type_materiel",
                            None
                        )
                    ),
                    valeur
                )
            ],
            [
                Paragraph(
                    "Système",
                    label
                ),
                Paragraph(
                    valeur_propre(
                        getattr(
                            reparation,
                            "systeme_exploitation",
                            None
                        )
                    ),
                    valeur
                )
            ],
            [
                Paragraph(
                    "Version Office",
                    label
                ),
                Paragraph(
                    valeur_propre(
                        getattr(
                            reparation,
                            "version_office",
                            None
                        )
                    ),
                    valeur
                )
            ],
            [
                Paragraph(
                    "Marque",
                    label
                ),
                Paragraph(
                    valeur_propre(
                        getattr(
                            reparation,
                            "marque",
                            None
                        )
                    ),
                    valeur
                )
            ],
            [
                Paragraph(
                    "Modèle",
                    label
                ),
                Paragraph(
                    valeur_propre(
                        getattr(
                            reparation,
                            "modele",
                            None
                        )
                    ),
                    valeur
                )
            ],
            [
                Paragraph(
                    "Numéro de série",
                    label
                ),
                Paragraph(
                    valeur_propre(
                        getattr(
                            reparation,
                            "numero_serie",
                            None
                        )
                    ),
                    valeur
                )
            ]
        ])
    )

    elements.append(Spacer(1, 3 * mm))

    # PROBLÈME
    elements.append(
        section_title(
            "DESCRIPTION DE LA DEMANDE"
        )
    )

    elements.append(
        info_table([
            [
                Paragraph(
                    "Origine",
                    label
                ),
                Paragraph(
                    valeur_propre(
                        getattr(
                            reparation,
                            "origine_probleme",
                            None
                        )
                    ),
                    valeur
                )
            ],
            [
                Paragraph(
                    "Intervention",
                    label
                ),
                Paragraph(
                    valeur_propre(
                        getattr(
                            reparation,
                            "intervention",
                            None
                        )
                    ),
                    valeur
                )
            ],
            [
                Paragraph(
                    "Problème constaté",
                    label
                ),
                Paragraph(
                    valeur_propre(
                        getattr(
                            reparation,
                            "probleme",
                            None
                        )
                    ),
                    valeur
                )
            ],
            [
                Paragraph(
                    "Pièces défectueuses",
                    label
                ),
                Paragraph(
                    valeur_propre(
                        getattr(
                            reparation,
                            "pieces_defectueuses",
                            None
                        )
                    ),
                    valeur
                )
            ],
            [
                Paragraph(
                    "Accessoires déposés",
                    label
                ),
                Paragraph(
                    valeur_propre(
                        getattr(
                            reparation,
                            "accessoires",
                            None
                        )
                    ),
                    valeur
                )
            ],
            [
                Paragraph(
                    "Remarques",
                    label
                ),
                Paragraph(
                    valeur_propre(
                        getattr(
                            reparation,
                            "remarques",
                            None
                        )
                    ),
                    valeur
                )
            ]
        ])
    )

    # URGENCE
    urgent = getattr(
        reparation,
        "urgent",
        False
    )

    elements.append(
        Spacer(
            1,
            3 * mm
        )
    )

    texte_urgence = "<font color='#DC2626'><b>URGENTE ⚠️</b></font>" if urgent else "Normale"
    couleur_fond_urgence = colors.HexColor("#FEF2F2") if urgent else colors.HexColor("#F8FAFC")

    urgence_table = Table(
        [[
            Paragraph(
                "<b>PRIORITÉ :</b>",
                label
            ),
            Paragraph(
                texte_urgence,
                valeur
            )
        ]],
        colWidths=[46 * mm, 140 * mm]
    )

    urgence_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                couleur_fond_urgence
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor("#CBD5E1")
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                6
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5
            )
        ])
    )

    elements.append(
        urgence_table
    )

    # FOOTER
    elements.append(
        Spacer(
            1,
            4 * mm
        )
    )

    elements.append(
        HRFlowable(
            width="100%",
            thickness=0.5,
            color=colors.HexColor("#CBD5E1")
        )
    )

    elements.append(
        Spacer(
            1,
            2 * mm
        )
    )

    elements.append(
        Paragraph(
            "Merci de conserver cette fiche pour le suivi de votre réparation.",
            sous_titre
        )
    )

    # QR CODE
    qr_path = getattr(
        reparation,
        "qr_code",
        None
    )

    if qr_path and os.path.exists(qr_path):
        qr = Image(
            qr_path,
            width=28 * mm,
            height=28 * mm
        )
        qr.hAlign = "RIGHT"
        elements.append(qr)

    # GÉNÉRATION
    doc.build(elements)
    