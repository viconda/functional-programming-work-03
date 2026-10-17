"""СРС 1. Анализ явно заданного набора только разрешёнными средствами."""


def run() -> None:
    """Выполнить три запроса для шести студентов двух известных групп."""
    students = [
        ("Алимов", "CS-23-1", 86),
        ("Ким", "CS-23-1", 92),
        ("Петрова", "CS-23-1", 78),
        ("Садыков", "CS-23-2", 91),
        ("Иванова", "CS-23-2", 88),
        ("Нурланов", "CS-23-2", 75),
    ]
    mean = (lambda a, b, c, d, e, f: (a + b + c + d + e + f) / 6)(
        students[0][2],
        students[1][2],
        students[2][2],
        students[3][2],
        students[4][2],
        students[5][2],
    )
    best_a = max(filter(lambda s: s[1] == "CS-23-1", students), key=lambda s: s[2])
    best_b = max(filter(lambda s: s[1] == "CS-23-2", students), key=lambda s: s[2])
    above_mean = sorted(
        filter(lambda s: s[2] > mean, students), key=lambda s: s[2], reverse=True
    )
    ordered = sorted(students, key=lambda s: (s[1], -s[2]))
    worst = min(students, key=lambda s: s[2])
    print("Вход:", students[:3])
    print("     ", students[3:])
    print("Общий средний балл:", mean)
    print("Лучший CS-23-1:", best_a)
    print("Лучший CS-23-2:", best_b)
    print("Выше среднего:", above_mean[:2])
    print("               ", above_mean[2:])
    print("Сортировка:", ordered[:3])
    print("           ", ordered[3:])
    print("Минимальный балл:", worst)
    assert mean == 85.0
    assert best_a == ("Ким", "CS-23-1", 92)
    assert best_b == ("Садыков", "CS-23-2", 91)
    assert above_mean == [students[1], students[3], students[4], students[0]]
    assert ordered == [
        students[1],
        students[0],
        students[2],
        students[3],
        students[4],
        students[5],
    ]
    print("Расчёты: sorted, filter, max, min, lambda; без sum, len и циклов.")
