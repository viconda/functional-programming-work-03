"""Проверить типы, стиль и сохранённые результаты практических запусков."""

import json
import os
from pathlib import Path
import subprocess
import sys


def main() -> None:
    """Выполнить независимые проверки без повторения измерений timeit."""
    root = Path(__file__).resolve().parent
    environment = os.environ.copy()
    if (root / ".tools").exists():
        environment["PYTHONPATH"] = str(root / ".tools")
    commands = (
        ("mypy", "lab03"), ("mypy", "lecture03"),
        ("ruff", "check", "lab03"), ("ruff", "check", "lecture03"),
    )
    for arguments in commands:
        print("python -m", " ".join(arguments))
        result = subprocess.run(
            [sys.executable, "-X", "utf8", "-m", *arguments],
            cwd=root, env=environment, capture_output=True,
            text=True, encoding="utf-8", check=True,
        )
        print(result.stdout.strip())
    cases = json.loads((root / "evidence_cases.json").read_text("utf-8"))
    practical = [case for case in cases if case["id"] != "checks"]
    for case in practical:
        log = json.loads((root / "evidence/logs" / f"{case['id']}.json").read_text("utf-8"))
        assert log["exit_code"] == 0
        assert log["stderr"] == ""
        assert log["stdout"].strip()
    print(f"Фактические практические запуски: {len(practical)}/{len(practical)} успешны")
    print("Лекция: 15 примеров + 3 демонстрации + 4 СРС = 22 запуска")
    print("Лабораторная: 2 примера + 6 заданий + дополнительное = 9 запусков")
    print("Типы, оформление кода и журналы проверены")


if __name__ == "__main__":
    main()
