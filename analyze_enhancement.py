from pathlib import Path
import pandas as pd


PROJECT_DIR = Path(
    r"C:\Users\tanuj\OneDrive\Documents\AIM002_Member1_Starter_Implementation"
)

CSV_PATH = (
    PROJECT_DIR
    / "data"
    / "enhancement_results"
    / "enhancement_summary.csv"
)


def main():

    print("=" * 70)
    print("AIM002 - ENHANCEMENT ANALYSIS")
    print("=" * 70)

    if not CSV_PATH.exists():
        print("ERROR: Summary CSV not found:")
        print(CSV_PATH)
        print()
        print("First run:")
        print("python enhance_real_datasets.py")
        return

    df = pd.read_csv(CSV_PATH)

    print(f"Rows in summary: {len(df)}")
    print()

    # ---------------------------------------------------------
    # Basic information
    # ---------------------------------------------------------

    print("DATASET DISTRIBUTION")
    print("-" * 70)

    print(df["dataset"].value_counts())

    print()

    # ---------------------------------------------------------
    # Enhancement methods
    # ---------------------------------------------------------

    print("ENHANCEMENT METHODS")
    print("-" * 70)

    print(df["method"].value_counts())

    print()

    # ---------------------------------------------------------
    # Statistics by method
    # ---------------------------------------------------------

    summary = (
        df.groupby("method")
        .agg(
            images=("relative_image", "nunique"),
            average_mean_intensity=(
                "mean_intensity",
                "mean"
            ),
            average_std_intensity=(
                "std_intensity",
                "mean"
            ),
            average_processing_time_ms=(
                "processing_time_ms",
                "mean"
            ),
        )
        .reset_index()
    )

    summary = summary.sort_values("method")

    print("STATISTICS BY ENHANCEMENT METHOD")
    print("-" * 70)

    print(
        summary.to_string(
            index=False,
            float_format=lambda x: f"{x:.3f}"
        )
    )

    print()

    # ---------------------------------------------------------
    # Save analysis
    # ---------------------------------------------------------

    output_path = (
        PROJECT_DIR
        / "data"
        / "enhancement_results"
        / "enhancement_analysis.csv"
    )

    summary.to_csv(
        output_path,
        index=False
    )

    print("=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)

    print("Saved:")
    print(output_path)


if __name__ == "__main__":
    main()