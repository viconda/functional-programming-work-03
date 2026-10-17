"""Пример 14. Структурное разделение неизменённых ветвей."""


def run() -> None:
    """Создать новую конфигурацию и проверить общую неизменяемую ветвь."""
    config_v1 = (("db", ("host", "localhost")), ("cache", ("ttl", 60)))
    db_part = config_v1[0]
    config_v2 = (db_part, ("cache", ("ttl", 120)))
    print(config_v2[0] is config_v1[0])
    print("Старая версия:", config_v1)
    print("Новая версия:", config_v2)
    assert config_v1[1][1][1] == 60 and config_v2[1][1][1] == 120
    assert config_v1 is not config_v2 and config_v1[0] is config_v2[0]
