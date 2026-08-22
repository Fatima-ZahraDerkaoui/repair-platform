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
    # DOCUMENT
    # =====================================================

    doc = SimpleDocTemplate(

        chemin_fichier,

        pagesize=A4,

        rightMargin=15 * mm,

        leftMargin=15 * mm,

        topMargin=12 * mm,

        bottomMargin=12 * mm

    )

    styles = getSampleStyleSheet()

    # =====================================================
    # STYLES
    # =====================================================

    titre = ParagraphStyle(

        "Titre",

        parent=styles["Title"],

        fontSize=20,

        leading=24,

        alignment=TA_CENTER,

        textColor=colors.HexColor("#1F2937"),

        spaceAfter=5

    )

    sous_titre = ParagraphStyle(

        "SousTitre",

        parent=styles["Normal"],

        fontSize=9,

        alignment=TA_CENTER,

        textColor=colors.HexColor("#6B7280"),

        spaceAfter=12

    )

    section = ParagraphStyle(

        "Section",

        parent=styles["Heading2"],

        fontSize=11,

        leading=14,

        textColor=colors.white,

        spaceBefore=8,

        spaceAfter=5

    )

    normal = ParagraphStyle(

        "NormalCustom",

        parent=styles["Normal"],

        fontSize=9,

        leading=12,

        textColor=colors.HexColor("#374151")

    )

    label = ParagraphStyle(

        "Label",

        parent=styles["Normal"],

        fontSize=8,

        textColor=colors.HexColor("#6B7280")

    )

    valeur = ParagraphStyle(

        "Valeur",

        parent=styles["Normal"],

        fontSize=9,

        textColor=colors.HexColor("#111827")

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

            [[Paragraph(text, section)]],

            colWidths=[180 * mm]

        )

        table.setStyle(

            TableStyle([

                (

                    "BACKGROUND",

                    (0, 0),

                    (-1, -1),

                    colors.HexColor("#2563EB")

                ),

                (

                    "LEFTPADDING",

                    (0, 0),

                    (-1, -1),

                    8

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

                    2

                )

            ])

        )

        return table

    def info_table(rows):

        table = Table(

            rows,

            colWidths=[45 * mm, 135 * mm]

        )

        table.setStyle(

            TableStyle([

                (

                    "BACKGROUND",

                    (0, 0),

                    (0, -1),

                    colors.HexColor("#F3F4F6")

                ),

                (

                    "GRID",

                    (0, 0),

                    (-1, -1),

                    0.4,

                    colors.HexColor("#D1D5DB")

                ),

                (

                    "VALIGN",

                    (0, 0),

                    (-1, -1),

                    "TOP"

                ),

                (

                    "LEFTPADDING",

                    (0, 0),

                    (-1, -1),

                    7

                ),

                (

                    "RIGHTPADDING",

                    (0, 0),

                    (-1, -1),

                    7

                ),

                (

                    "TOPPADDING",

                    (0, 0),

                    (-1, -1),

                    6

                ),

                (

                    "BOTTOMPADDING",

                    (0, 0),

                    (-1, -1),

                    6

                )

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

            10

        )

    )

    urgence_table = Table(

        [[

            Paragraph(

                "<b>PRIORITÉ :</b>",

                normal

            ),

            Paragraph(

                "<b>URGENTE</b>" if urgent else "Normale",

                normal

            )

        ]],

        colWidths=[45 * mm, 135 * mm]

    )

    urgence_table.setStyle(

        TableStyle([

            (

                "BACKGROUND",

                (0, 0),

                (-1, -1),

                colors.HexColor("#FEF3C7")

                if urgent

                else colors.HexColor("#F3F4F6")

            ),

            (

                "BOX",

                (0, 0),

                (-1, -1),

                0.6,

                colors.HexColor("#D1D5DB")

            ),

            (

                "PADDING",

                (0, 0),

                (-1, -1),

                8

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

            15

        )

    )

    elements.append(

        HRFlowable(

            width="100%",

            thickness=0.8,

            color=colors.HexColor("#D1D5DB")

        )

    )

    elements.append(

        Spacer(

            1,

            5

        )

    )

    elements.append(

        Paragraph(

            "Merci de conserver cette fiche pour le suivi de votre réparation.",

            sous_titre

        )

    )

    # =====================================================
    # QR CODE
    # =====================================================

    qr_path = getattr(

        reparation,

        "qr_code",

        None

    )

    if qr_path and os.path.exists(qr_path):

        qr = Image(

            qr_path,

            width=32 * mm,

            height=32 * mm

        )

        qr.hAlign = "RIGHT"

        elements.append(qr)

    # =====================================================
    # GÉNÉRATION
    # =====================================================

    doc.build(elements)