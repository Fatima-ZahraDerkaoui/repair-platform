from ocr.checkbox_detector import CheckboxDetector


detector = CheckboxDetector()


result = detector.detect(
    "fiche2.png"
)


print("\n===== CASES COCHÉES =====\n")


for section, values in result.items():

    print(
        f"{section}:"
    )

    for value in values:

        print(
            f"  ✓ {value}"
        )