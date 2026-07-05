"""
===============================================================================
 train.py  --  One-command training entry point
===============================================================================
Runs the complete ML pipeline end-to-end and saves all artefacts to models/.

Usage:
    python train.py
===============================================================================
"""

from src.model_training import train_and_select


def main() -> None:
    print("=" * 70)
    print(" Intelligent Skill Profiling — Model Training Pipeline")
    print("=" * 70)
    result = train_and_select(verbose=True)

    print("\n" + "-" * 70)
    print(" Model comparison (sorted by cross-validation F1)")
    print("-" * 70)
    rows = sorted(result["results"].items(),
                  key=lambda kv: kv[1]["cv_f1_mean"], reverse=True)
    header = f"{'Model':<22}{'Accuracy':>10}{'Precision':>11}{'Recall':>9}{'F1':>8}{'CV-F1':>9}"
    print(header)
    print("-" * len(header))
    for name, r in rows:
        star = "  *" if name == result["best_name"] else ""
        print(f"{name:<22}{r['accuracy']:>10.3f}{r['precision']:>11.3f}"
              f"{r['recall']:>9.3f}{r['f1']:>8.3f}{r['cv_f1_mean']:>9.3f}{star}")
    print("-" * len(header))
    print(f" Best model selected: {result['best_name']}")
    print("=" * 70)


if __name__ == "__main__":
    main()
