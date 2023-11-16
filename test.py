from orm import Database, Table


class Teacher(Table):
    name = "TEXT"
    age = "INTEGER"


class Student(Table):
    name = "TEXT"
    age = "INTEGER"


db = Database("school.db")
db.sync()


# print(db.select_all(Teacher))
# db.insert(Teacher, {"name": "Peter", "age": "28"})
print(db.select_all(Teacher))
print(db.select_one(Teacher, name="Peter"))
