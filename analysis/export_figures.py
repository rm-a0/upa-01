"""Export the PNG figures embedded in the EDA notebook to docs/figures."""

import base64
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOTEBOOK = ROOT / "analysis" / "eda.ipynb"
OUTPUT_DIR = ROOT / "docs" / "figures"

FIGURES = [
    "fig1_price_distribution.png",
    "fig2_price_brand_box.png",
    "fig3_price_lumens_scatter.png",
    "fig4_materials_bar.png",
    "fig5_price_brand_violin.png",
    "fig6_numeric_boxplots.png",
    "fig7_correlation_numeric.png",
]


def main() -> None:
    """Read image outputs in notebook order and write them to docs/figures."""
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    images = [
        output["data"]["image/png"]
        for cell in notebook["cells"]
        for output in cell.get("outputs", [])
        if "image/png" in output.get("data", {})
    ]
    if len(images) != len(FIGURES):
        raise SystemExit(
            f"Expected {len(FIGURES)} figures in {NOTEBOOK}, found {len(images)}"
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, image in zip(FIGURES, images, strict=True):
        (OUTPUT_DIR / name).write_bytes(base64.b64decode(image))
        print(f"Wrote {OUTPUT_DIR / name}")


if __name__ == "__main__":
    main()
