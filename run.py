import sys
import time
import json
import requests
from bs4 import BeautifulSoup


def get_prev_update_time(contestType: str):
    assert contestType in ("algo", "heuristic")
    try:
        with open(f"{contestType}.json", "r", encoding="utf-8") as f:
            res: str = json.load(f)["last_update_time"]
        return res
    except Exception:
        return ""


def get_rankings(contestType: str, sleep_time=3):
    assert contestType in ("algo", "heuristic")
    prev_update_time = get_prev_update_time(contestType)
    page = 1
    time.sleep(sleep_time)
    response = requests.get(f"https://atcoder.jp/ranking/all?contestType={contestType}&page={page}")
    if response.status_code != requests.codes.ok:
        print(
            f"{response.status_code=} in requests.get(https://atcoder.jp/ranking/all?contestType={contestType}&page={page})",
            sys.stderr,
        )
        return {"success": False, "last_update_time": prev_update_time, "data": {}, "spans": {}}
    soup = BeautifulSoup(response.text, "html.parser")
    tm = soup.select_one("time")
    assert tm is not None
    last_update_time = str(tm.string)
    if last_update_time == prev_update_time:
        return {"success": False, "last_update_time": prev_update_time, "data": {}, "spans": {}}

    data: dict[str, int] = {}
    spans: dict[str, str] = {}
    while True:
        print(page)
        table = soup.select("table")[1].tbody
        if table is None:
            break
        rows = table.select("tr")
        if len(rows) == 0:
            break
        for i in range(len(rows)):
            span = rows[i].select("td")[1].select_one("span")
            assert span is not None
            name = span.string
            assert name is not None
            rating = rows[i].select("td")[3].string
            assert rating is not None
            data[name] = int(rating)
            if "color:" in str(span):
                spans[name] = str(span)

        page += 1
        time.sleep(sleep_time)
        response = requests.get(f"https://atcoder.jp/ranking/all?contestType={contestType}&page={page}")
        if response.status_code != requests.codes.ok:
            print(
                f"{response.status_code=} in requests.get(https://atcoder.jp/ranking/all?contestType={contestType}&page={page})",
                sys.stderr,
            )
            break
        soup = BeautifulSoup(response.text, "html.parser")
    return {"success": True, "last_update_time": last_update_time, "data": data, "spans": spans}


result = get_rankings("heuristic")
if result["success"]:
    with open(f"heuristic.json", "w", encoding="utf-8") as f:
        json.dump(result, f)
    with open(f"heuristic_indent.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
