from app.services.ocr.line_builder import LineBuilder

builder = LineBuilder()

tests = [

    "HP-F6V25AE",
    "CF283A",
    "TN-3478",
    "106R03480",
    "C13T00S44A",
    "GI490BK",
    "B3P23A",

    "Cartouche HP",
    "TOTAL",
    "20%",
    "110.00",
    "2",
    "TVA"

]

for t in tests:
    print(f"{t:20} -> {builder.is_reference(t)}")