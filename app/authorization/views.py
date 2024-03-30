from django.shortcuts import render
from django.http import HttpResponse
import sqlite3
from django.core.management.utils import get_random_secret_key

from django.conf import settings
import jwt
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


conn = sqlite3.connect("football.db", check_same_thread=False)
cursor = conn.cursor()
# подключение базы данных
cursor.execute(
    """CREATE TABLE IF NOT EXISTS Users( 
    username TEXT PRIMARY KEY,
    password TEXT,
    key TEXT,
    icon BLOB,
    win_cnt INTEGER);
"""
)


def db_table_val(username: str, password: str, key: str, icon: bytes, win_cnt: int):
    cursor.execute(
        "INSERT INTO Users (username, password, key, icon, win_cnt) VALUES (?, ?, ?, ?, ?)",
        (username, password, key, icon, win_cnt),
    )
    conn.commit()


@csrf_exempt
def reg(request):

    if request.method == "POST":
        data = json.loads(request.body)
        payload = {"name": str(data.get("name")), "password": str(data.get("password"))}
        secret_key = str(get_random_secret_key)
        token = str(jwt.encode(payload, secret_key, algorithm="HS256"))
        icon = ""
        win_cnt = 0
        a = cursor.execute(f"SELECT * FROM Users WHERE username = '{payload['name']}'")
        rand = a.fetchone()
        if rand:
            response = JsonResponse({"error": "already exist"})
            response.status_code = 400
            return response


        else:
            db_table_val(payload["name"], payload["password"], token, icon, win_cnt)
            response = JsonResponse({"response": "success"})
            response.set_cookie("jwt", token, expires=3600, samesite="lax")
            response.status_code = 200
            return response
    else:
        response = JsonResponse({"error": "only post"})
        response.status_code = 400
        return response


@csrf_exempt
def authorization(request):
    token = str(request.COOKIES.get("jwt"))
    a = cursor.execute(f"SELECT * FROM Users WHERE key = '{token}'")
    rand = a.fetchone()
    if rand:
        response = JsonResponse({"response": "have token"})
        response.status_code = 200
        return response
    else:
        data = json.loads(request.body)
        payload = {"name": str(data.get("name")), "password": str(data.get("password"))}
        secret_key = str(get_random_secret_key)
        token = jwt.encode(payload, secret_key, algorithm="HS256")
        i = cursor.execute(
            f"SELECT password FROM Users WHERE username = '{payload['name']}'"
        )
        getpass = i.fetchone()
        if getpass and (payload["password"] == getpass[0]):
            cursor.execute(
                "UPDATE Users SET key = ? WHERE username = ?", (token, payload["name"])
            )
            conn.commit()
            response = JsonResponse({"response": "success"})
            response.set_cookie("jwt", token, expires=3600, samesite="lax")
            response.status_code = 200
            return response
        else:
            response = JsonResponse({"error": "wrong password"})
            response.status_code = 400
            return response


def db_table2_val(
    tournir_name: str,
    admin: str,
    players: str,
    prize: str,
    place: str,
    total_tours: str,
):
    cursor.execute(
        "INSERT INTO Tournirs (tournir_name, admin, players, prize, place, total_tours) VALUES (?, ?, ?, ?, ?, ?)",
        (tournir_name, admin, players, prize, place, total_tours),
    )
    conn.commit()


@csrf_exempt
def maketournir(request):
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS Tournirs( 
    tournir_id INTEGER PRIMARY KEY,
    tournir_name TEXT,
    admin TEXT,
    players TEXT,
    prize TEXT,
    place TEXT,
    total_tours TEXT);
    """
    )
    data = json.loads(request.body)
    payload = {
        "tournir_name": str(data.get("tournir_name")),
        "admin": str(data.get("admin")),
        "players": str(data.get("players")),
        "prize": str(data.get("prize")),
        "place": str(data.get("place")),
        "total_tours": str(data.get("total_tours")),
    }
    db_table2_val(
        payload["tournir_name"],
        payload["admin"],
        payload["players"],
        payload["prize"],
        payload["place"],
        payload["total_tours"],
    )
    conn.commit()
    response = JsonResponse([{"congrats": "game created"}])
    response.status_code = 200
    return response


@csrf_exempt
def endtour(request):
    data = json.loads(request.body)
    payload = {"winners": data.get("winners")}
    for i in payload["winners"]:
        c = cursor.execute(f"SELECT win_cnt FROM Users WHERE username = '{i}'")
        win_cnt = int(c.fetchone()[0]) + 1
        cursor.execute(f"UPDATE Users SET win_cnt = {win_cnt} WHERE username = '{i}'")
    conn.commit()
    return HttpResponse("колво побед увеличилось")


@csrf_exempt
def tournirs(request):
    response = JsonResponse({"tour":[{"id":1, "name": "эпичная битва", "status":"запланирован", "number":32, "date":"30.04.2024"},
                            {"id":2,"name": "фатальная схватка", "status":"запланирован", "number":16, "date":"15.04.2024"},
                            {"id":3,"name": "крутое сражение", "status":"завершенный", "number":16, "date":"30.03.2024"},
                            {"id":4,"name": "жесткий матч", "status":"завершенный", "number":8, "date":"25.03.2024"},
                            {"id":5,"name": "футбольная баталия", "status":"запланированный", "number":32, "date":"17.04.2024"},
                            {"id":6,"name": "роковой футбол", "status":"завершенный", "number":4, "date":"23.02.2024"},
                            {"id":7,"name": "смертельный бой", "status":"завершенный", "number":2, "date":"21.02.2024"},
                            {"id":8,"name": "спортивное столкновение", "status":"запланированный", "number":4, "date":"12.01.2024"} ]})
    response.status_code = 200
    return response


@csrf_exempt
def lasttournirs(request):
    response = JsonResponse({"id":1,"tour":[{"name": "эпичная битва", "status":"запланирован", "number":32, "date":"30.04.2024"},
                            {"id":2,"name": "фатальная схватка", "status":"запланирован", "number":16, "date":"15.04.2024"},
                            {"id":3,"name": "крутое сражение", "status":"завершенный", "number":16, "date":"30.03.2024"},]})
    response.status_code = 200
    return response