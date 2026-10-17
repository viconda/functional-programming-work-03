"""Локальное приложение для реальных запусков Python и снимков их вывода."""

from datetime import datetime
from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import textwrap
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent


def execute(case: dict[str, object]) -> dict[str, object]:
    """Запустить команду и сохранить фактический вывод без редактирования."""
    args = [str(arg) for arg in case["args"]]
    command = [sys.executable, "-X", "utf8", *args]
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(ROOT / ".tools") + os.pathsep + str(ROOT)
    result = subprocess.run(command, cwd=ROOT, env=environment,
                            capture_output=True, text=True, encoding="utf-8",
                            timeout=180)
    data = {"id": case["id"], "title": case["title"], "command": command,
            "display_command": "python " + " ".join(args),
            "python": platform.python_version(),
            "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
            "exit_code": result.returncode, "stdout": result.stdout,
            "stderr": result.stderr}
    log_dir = ROOT / "evidence" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / f"{case['id']}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    (log_dir / f"{case['id']}.txt").write_text(
        result.stdout + result.stderr, encoding="utf-8")
    return data


class Viewer(BaseHTTPRequestHandler):
    """Показывать только локальные разрешённые учебные запуски."""

    def do_GET(self) -> None:
        query = parse_qs(urlparse(self.path).query)
        case_id = query.get("case", [""])[0]
        cases = json.loads((ROOT / "evidence_cases.json").read_text("utf-8"))
        case = next((item for item in cases if item["id"] == case_id), None)
        if case is None:
            self.send_error(404)
            return
        log = ROOT / "evidence" / "logs" / f"{case_id}.json"
        if query.get("run") == ["1"] or not log.exists():
            data = execute(case)
        else:
            data = json.loads(log.read_text("utf-8"))
        lines = []
        for line in (str(data["stdout"]) + str(data["stderr"])).splitlines():
            lines.extend(textwrap.wrap(line, width=98, replace_whitespace=False,
                                       drop_whitespace=False) or [""])
        page_size = 25
        pages = max(1, (len(lines) + page_size - 1) // page_size)
        part = max(1, min(int(query.get("part", ["1"])[0]), pages))
        text = "\n".join(lines[(part - 1) * page_size:part * page_size])
        status = "Завершено успешно" if data["exit_code"] == 0 else "Ошибка запуска"
        html = f'''<!doctype html><html lang="ru"><meta charset="utf-8">
<title>{escape(str(data['title']))}</title><style>
body{{margin:0;background:#fff;color:#171717;font:19px Arial,sans-serif}}
main{{padding:28px 34px;width:1032px;box-sizing:border-box}}
.brand{{font-size:16px;color:#555;margin-bottom:14px}}
h1{{font-size:25px;margin:0 0 12px;line-height:1.25}}
.cmd{{font:18px Consolas,monospace;padding:10px 0;overflow-wrap:anywhere}}
.meta{{font-size:15px;color:#484848;line-height:1.7}}
pre{{font:18px/1.35 Consolas,monospace;white-space:pre-wrap;margin:20px 0;
overflow-wrap:anywhere;min-height:120px}}
footer{{font-size:15px;color:#444;padding-top:12px;border-top:1px solid #bbb}}
</style><main data-pages="{pages}" data-exit-code="{data['exit_code']}">
<div class="brand">Работа 03 · Журнал фактического выполнения Python</div>
<h1>{escape(str(data['title']))}</h1>
<div class="cmd">{escape(str(data['display_command']))}</div>
<div class="meta">Python {data['python']} · {escape(str(data['timestamp']))}<br>
{status} · Код возврата {data['exit_code']} · Часть {part} из {pages}</div>
<pre>{escape(text)}</pre>
<footer>Вывод получен запуском программы из проекта Работа_03.
Полный журнал сохранён в evidence/logs/{escape(case_id)}.txt.</footer></main></html>'''
        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        """Не засорять консоль HTTP-журналом."""


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", 8763), Viewer).serve_forever()
