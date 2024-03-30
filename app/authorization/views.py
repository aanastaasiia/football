from django.shortcuts import render
from django.http import HttpResponse
import sqlite3
from django.core.management.utils import get_random_secret_key

from django.conf import settings
import jwt
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


conn = sqlite3.connect('football.db', check_same_thread=False)
cursor = conn.cursor()
#подключение базы данных
cursor.execute("""CREATE TABLE IF NOT EXISTS Users( 
    username TEXT PRIMARY KEY,
    password TEXT,
    key TEXT,
    icon BLOB);
""")
def db_table_val(username: str, password: str, key: str, icon: bytes = None):
    cursor.execute('INSERT INTO Users (username, password, key, icon) VALUES (?, ?, ?, ?)', (username, password, key, icon))
    conn.commit()

@csrf_exempt
def reg(request):
    # username = str(request.POST.get("username"))
    # password = str(request.POST.get("password"))

    if request.method == 'POST':
        data = json.loads(request.body)
        payload = {
        "name": str(data.get('name')),
        "password":str(data.get('password'))
        }
        secret_key = str(get_random_secret_key)
        token = str(jwt.encode(payload, secret_key, algorithm='HS256'))
        icon = ''
        # a = cursor.execute("SELECT * FROM Users WHERE username = ?", (username))
        a = cursor.execute(f"SELECT * FROM Users WHERE username = '{payload['name']}'")
        rand = a.fetchone()
        if rand:
            return HttpResponse('такой пользователь уже есть')

        else:
            db_table_val(payload['name'], payload['password'], token, icon)
            response = JsonResponse({'response':'success'})
            response.set_cookie('jwt',token)
            response.status_code = 200
            return response
    else:
        return JsonResponse({'error':'only post'})


    # payload = {
    #     'name':username,
    #     'password': password
    # }
    
@csrf_exempt
def authorization(request):
    token = str(request.COOKIES.get('jwt'))
    a = cursor.execute(f"SELECT * FROM Users WHERE key = '{token}'")
    rand = a.fetchone()
    if rand:
        response = JsonResponse({'response':'have token'})
        response.status_code = 200
        return response  
    else:
        data = json.loads(request.body)
        payload = {
        "name": str(data.get('name')),
        "password": str(data.get('password'))
        }
        secret_key = str(get_random_secret_key)
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        i = cursor.execute(f"SELECT password FROM Users WHERE username = '{payload['name']}'")
        getpass = i.fetchone()
        if getpass and (payload['password'] == getpass[0]):
            cursor.execute("UPDATE Users SET key = %s WHERE username = %s", (token, payload['name']))
            conn.commit()
            response = JsonResponse({'response':'success'})
            response.set_cookie('jwt',token)
            response.status_code = 200
            return response
        else:
            response = JsonResponse({'error':'wrong password'})
            response.status_code = 400
            return response


def db_table2_val(tournir_name:str, admin:str, players:str, prize:str, place:str, total_tours:str):
    cursor.execute('INSERT INTO Tournirs (tournir_name, admin, players, prize, place, total_tours) VALUES (?, ?, ?, ?, ?, ?)', (tournir_name, admin, players, prize, place, total_tours))
    conn.commit()

@csrf_exempt
def maketournir(request):
    cursor.execute("""CREATE TABLE IF NOT EXISTS Tournirs( 
    tournir_id INTEGER PRIMARY KEY,
    tournir_name TEXT,
    admin TEXT,
    players TEXT,
    prize TEXT,
    place TEXT,
    total_tours TEXT);
    """)
    data = json.loads(request.body)
    payload = {
        "tournir_name":str(data.get('tournir_name')),
        "admin":str(data.get('admin')),
        "players":str(data.get('players')),
        "prize":str(data.get('prize')),
        "place":str(data.get('place')),
        "total_tours": str(data.get('total_tours'))
        }
    db_table2_val(payload["tournir_name"], payload["admin"], payload["players"], payload["prize"], payload["place"], payload["total_tours"])
    conn.commit()
    response = JsonResponse({'congrats':'game created'})
    response.status_code = 200
    return response

def endtour(request):
    pass
