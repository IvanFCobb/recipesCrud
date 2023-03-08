from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models import recipe
from flask import flash


class User:
    def __init__(self, data):
        self.id = data['id']
        self.fname = data['first_name']
        self.lname = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.recipes = []

    @classmethod
    def get_by_email(cls, email):
        query = "SELECT * FROM users WHERE email = '{}';".format(email)
        results = connectToMySQL('recipes').query_db(query)
        if len(results) < 1:
            return False
        return cls(results[0])

    @classmethod
    def get_by_id(cls, id):
        query = "SELECT * FROM users WHERE id = '{}';".format(id)
        results = connectToMySQL('recipes').query_db(query)
        return cls(results[0])

    @classmethod
    def save(cls, data):
        query = "INSERT INTO users ( first_name, last_name, email, password, created_at, updated_at) VALUES ( %(fname)s, %(lname)s, %(email)s, %(password)s, NOW() , NOW() );"
        return connectToMySQL('recipes').query_db(query, data)

    @classmethod
    def get_user_with_recipes(cls, data):
        print("about to query")
        query = "SELECT * FROM users LEFT JOIN recipes ON recipes.user_id = users.id WHERE users.id =%(id)s;"
        results = connectToMySQL('recipes').query_db(query, data)
        print("results-----------", results)
        user = cls(results[0])
        for row_from_db in results:
            recipe_data = {
                "id": row_from_db["recipes.id"],
                "name": row_from_db["name"],
                "over_under": row_from_db["over_under"],
                "description": row_from_db["description"],
                "instructions": row_from_db["instructions"],
                "date_cooked": row_from_db["date_cooked"],
                "user_id": row_from_db["user_id"],
                "created_at": row_from_db["recipes.created_at"],
                "updated_at": row_from_db["recipes.updated_at"]
            }
            user.recipes.append(recipe_data)
            print("done")
            print(recipe_data)
        print(user)
        return user
    
    @staticmethod
    def validate_email(data):
        query = "SELECT * from users WHERE email = %(email)s;"
        results = connectToMySQL('recipes').query_db(query, data)
        if len(results) >= 1:
            return True
        else:
            return False
