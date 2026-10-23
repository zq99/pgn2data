"""Rebuild sample CSV outputs from the PGNs in this folder."""

from pathlib import Path

from converter.pgn_data import PGNData


def rebuild_samples() -> None:
    samples_folder = Path(__file__).resolve().parent
    pgn_files = sorted(samples_folder.glob("*.pgn"))

    if not pgn_files:
        print("No PGN files found; existing CSV files left unchanged.")
        return

    for csv_file in samples_folder.glob("*.csv"):
        csv_file.unlink()
        print(f"Deleted: {csv_file.name}")

    for pgn_file in pgn_files:
        output_name = samples_folder / pgn_file.stem

        result = PGNData(
            pgn=str(pgn_file),
            file_name=str(output_name),
        ).export(collapse=False)

        if not result.is_complete:
            raise RuntimeError(f"Failed to rebuild samples for {pgn_file.name}")

        print(f"Rebuilt: {pgn_file.name}")


if __name__ == "__main__":
    rebuild_samples()