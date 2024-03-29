from django.shortcuts import render
from django.http import HttpResponse
import sqlite3
from django.core.management.utils import get_random_secret_key

from django.conf import settings
import jwt
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# class JWTMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         jwt_token = request.COOKIES.get('jwt')

#         if jwt_token:
#             try:
#                 payload = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=['HS256'])
#                 request.user = Users.objects.get(id=payload['user_id'])
#             except jwt.ExpiredSignatureError:
#                 pass
#             except jwt.InvalidTokenError:
#                 pass

#         response = self.get_response(request)
#         return response












conn = sqlite3.connect('db.sqlite3', check_same_thread=False)
cursor = conn.cursor()
#подключение базы данных
cursor.execute("""CREATE TABLE IF NOT EXISTS Users( 
    id INTEGER PRIMARY KEY,
    username TEXT,
    password TEXT,
    admin TEXT,
    key TEXT);
""")
def db_table_val(username: str, password: str, admin: str, key: str):
    cursor.execute('INSERT INTO Users (username, password, admin, key) VALUES (?, ?, ?, ?)', (username, password, admin, key))
    conn.commit()

@csrf_exempt
def reg(request):
    # username = str(request.POST.get("username"))
    # password = str(request.POST.get("password"))
    admin = 'false'

    if request.method == 'POST':
        data = json.loads(request.body)
        payload = {
        "name":data.get('name'),
        "password":data.get('password')
        }
        secret_key = str(get_random_secret_key)
        token = jwt.encode(payload, secret_key, algorithm='HS256')

        # a = cursor.execute("SELECT * FROM Users WHERE username = ?", (username))
        a = cursor.execute(f"SELECT * FROM Users WHERE username = '{payload['name']}'")
        rand = a.fetchone()
        if rand:
            return HttpResponse('такой пользователь уже есть')

        else:
            db_table_val(payload['name'], payload['password'], admin, token)
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
    token = request.COOKIES.get('jwt')
    a = cursor.execute(f"SELECT * FROM Users WHERE key = '{token}'")
    rand = a.fetchone()
    if rand:
        response = JsonResponse({'response':'success'})
        response.status_code = 200
        return response
        
    if not token:
        data = json.loads(request.body)
        payload = {
        "name":data.get('name'),
        "password":data.get('password')
        }
        secret_key = str(get_random_secret_key)
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        i = cursor.execute("SELECT password FROM Users WHERE username = ?", (payload['name'],))
        getpass = i.fetchone()
        if payload['password'] == getpass:
            cursor.execute(f'UPDATE Users SET key = {token} WHERE username = {payload["name"]}')
            response = JsonResponse({'response':'success'})
            response.set_cookie('jwt',token)
            response.status_code = 200
            return response
        else:
            response = JsonResponse({'error':'wrong password'})
            response.status_code = 400
            return response

   