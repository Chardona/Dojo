import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
import sqlite3

from xmltodict import parse
import csv

from app.models import User


def remove_parentheses(name: str, l_sign: str, r_sign: str):
    l_index = name.find(l_sign)
    r_index = name.rfind(r_sign)
    return name[0:l_index].strip() + name[r_index + 1:-1].strip() + name[-1] if name[-1] != ")" \
        else name[0:l_index].strip() + name[r_index + 1:-1].strip()


# xml
def get_first_and_last_name(path: str):
    with open(path) as f:
        content = f.read()
        raw_dict = parse(content)
        formatted_dict = raw_dict["user_list"]["user"]["users"]["user"]

        for element in formatted_dict:
            if element["last_name"] and element["first_name"]:
                if "(" in element["last_name"]:
                    element["last_name"] = remove_parentheses(element["last_name"], "(", ")")
                if "[" in element["last_name"]:
                    element["last_name"] = remove_parentheses(element["last_name"], "[", "]")
                if "(" in element["first_name"]:
                    element["first_name"] = remove_parentheses(element["first_name"], "(", ")")
                if "[" in element["first_name"]:
                    element["first_name"] = remove_parentheses(element["first_name"], "[", "]")
    return formatted_dict


# csv
def get_username_pwd_date(path: str):
    username_pwd_date = list(csv.DictReader(open(path, "r")))
    for element in username_pwd_date:
        if "(" in element["username"]:
            element["username"] = remove_parentheses(element["username"], "(", ")")
        if "[" in element["username"]:
            element["username"] = remove_parentheses(element["username"], "[", "]")
    return username_pwd_date


def names_intersection(names: list, username_pwd_date: list):
    for element in names:
        if element["first_name"] is None or element["last_name"] is None:
            names.remove(element)
        else:
            if element["first_name"].lower() and element["last_name"].lower() not in str(username_pwd_date).lower():
                names.remove(element)
    return names


def usernames_intersection(username_pwd_date: list, names: list):
    for el in username_pwd_date:
        for alias in el["username"].split('.'):
            if alias not in str(names) or len(el["username"].strip()) == 0:
                username_pwd_date.remove(el)
    return username_pwd_date


def update_names(names: list, usernames: list):
    for name in names:
        for username in usernames:
            if name["first_name"] and name["last_name"]:
                if name["first_name"] in username["username"] or name["last_name"] in username["username"]:
                    name.update(username)
    return names


def delete_redundant_names(names: list):
    for name in names:
        if len(name) < 7:
            names.remove(name)
    names.remove(names[-1])
    return names


def get_full_info():
    names = get_first_and_last_name("test_task.xml")
    username_pwd_date = get_username_pwd_date("test_task.csv")
    names = names_intersection(names, username_pwd_date)
    username_pwd_date = usernames_intersection(username_pwd_date, names)
    names = update_names(names, username_pwd_date)
    names = delete_redundant_names(names)

    return names


def insert_query(file_data: dict):

    sqlite3.paramstyle = "named"

    con = sqlite3.connect("db.sqlite3")

    cur = con.cursor()

    cur.execute("INSERT INTO app_user VALUES ("
                ":id , :password, :last_login, :is_superuser, :username, :first_name, :last_name, :email, "
                ":is_staff, :is_active, :avatar, :date_joined"" )",
                {"id": file_data["@id"], "password": file_data["password"], "username": file_data["username"],
                 "first_name": file_data["first_name"], "last_name": file_data["last_name"],
                 # incorrect date from file, replaced to a random one
                 # "avatar": file_data["avatar"], "date_joined": file_data["date_joined"],
                 "avatar": file_data["avatar"], "date_joined": "2022-10-10",
                 "email": "test@gmail.com", "is_staff": False, "is_active": False,
                 "is_superuser": False, "last_login": datetime.datetime.now()})

    con.commit()

    con.close()


def insert_data_to_bd():
    data = get_full_info()
    for datum in data:
        insert_query(datum)


def necessity_of_bd():
    con = sqlite3.connect("db.sqlite3")
    cur = con.cursor()
    cur.execute("SELECT username from app_user")
    if not len(cur.fetchall()):
        insert_data_to_bd()


necessity_of_bd()


class UserViewList(LoginRequiredMixin, generic.ListView):
    model = User
    queryset = User.objects.all()
    template_name = "user_list.html"



