"""Запуск: python -m lecture03 ex01; python -m lecture03 --all."""

import argparse
import contextlib
import importlib
import io
import json
from pathlib import Path

CASES = [
    *(f"ex{i:02d}" for i in range(1, 16)),
    "extra_strings",
    "extra_copy",
    "extra_pitfalls",
    "srs1",
    "srs2",
    "srs3",
    "srs4",
]
OUTPUTS = Path(__file__).resolve().parent / "outputs"


def execute(case: str) -> str:
    """Выполнить один практический пункт с проверками и вернуть его вывод."""
    module = importlib.import_module(f"lecture03.cases.{case}")
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        print(f"Лекция 3 | {case} | {module.__doc__}")
        module.run()
        print("ПРОВЕРКИ: УСПЕШНО")
    result = buffer.getvalue()
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    (OUTPUTS / f"{case}.txt").write_text(result, encoding="utf-8")
    return result


def main() -> None:
    """Разобрать командную строку и сохранить фактические результаты запусков."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", nargs="?", choices=CASES)
    parser.add_argument("--all", action="store_true", help="запустить все 22 пункта")
    args = parser.parse_args()
    if args.all:
        results = {}
        for case in CASES:
            output = execute(case)
            results[case] = {"status": "passed", "output": output}
            print(output, end="\n")
        (OUTPUTS / "results.json").write_text(
            json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"ИТОГО: {len(results)}/{len(CASES)} пунктов успешно.")
    elif args.case:
        print(execute(args.case), end="")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
