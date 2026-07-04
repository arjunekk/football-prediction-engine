from pathlib import Path


def main():
    project_root = Path(__file__).resolve().parents[2]

    print("=" * 50)
    print("FIFA World Cup Prediction Project")
    print("=" * 50)
    print(f"Project Root : {project_root}")
    print(f"Current File : {Path(__file__).name}")
    print("Environment  : Ready ✅")


if __name__ == "__main__":
    main()