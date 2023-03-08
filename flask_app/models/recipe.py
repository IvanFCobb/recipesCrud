from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
import re
from flask_app.models import user

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')


class Recipe:
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.over_under = data['over_under']
        self.description = data['description']
        self.instructions = data['instructions']
        self.date_cooked = data['date_cooked']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.creator = None

    @classmethod
    def get_all(cls):
        query = "SELECT * FROM recipes;"
        results = connectToMySQL('recipes').query_db(query)
        recipes = []
        for recipe in results:
            recipes.append(cls(recipe))
        return recipes
    
    @classmethod
    def get_all_recipes_with_creator(cls):
        query = "SELECT * FROM recipes JOIN users ON recipes.user_id = users.id;"
        results = connectToMySQL('recipes').query_db(query)
        all_recipes = []
        for row in results:
            one_recipe = cls(row)
            one_recipes_creator_info = {
                "id": row['users.id'], 
                "first_name": row['first_name'],
                "last_name": row['last_name'],
                "email": row['email'],
                "password": row['password'],
                "created_at": row['users.created_at'],
                "updated_at": row['users.updated_at']
            }
            creator = user.User(one_recipes_creator_info)
            one_recipe.creator = creator
            all_recipes.append(one_recipe)
        return all_recipes


    @classmethod
    def get_by_email(cls, email):
        query = "SELECT * FROM recipes WHERE email = '{}';".format(email)
        results = connectToMySQL('recipes').query_db(query)
        if len(results) < 1:
            return False
        return cls(results[0])

    @classmethod
    def get_by_id_with_creator(cls, id):
        query = "SELECT recipes.id, name, over_under, description, instructions, DATE_FORMAT(date_cooked, '%M %D, %Y') as date_cooked, recipes.created_at, recipes.updated_at, recipes.user_id, first_name FROM recipes JOIN users ON recipes.user_id = users.id WHERE recipes.id = '{}';".format(id)
        results = connectToMySQL('recipes').query_db(query)
        recipe = cls(results[0])
        recipe.creator = results[0]["first_name"]
        print(recipe.creator)
        return recipe
    
    @classmethod
    def get_by_id(cls, id):
        query = "SELECT * FROM recipes WHERE id = '{}';".format(id)
        results = connectToMySQL('recipes').query_db(query)
        return cls(results[0])
    
    @classmethod
    def save(cls, data):
        query = "INSERT INTO recipes ( name, description, instructions, date_cooked, over_under, user_id, updated_at) VALUES ( %(name)s, %(description)s, %(instructions)s, %(date_cooked)s, %(over_under)s, %(user_id)s, NOW());"
        return connectToMySQL('recipes').query_db(query, data)
    
    @classmethod
    def edit(cls, data):
        print("updating recipe...")
        query = "UPDATE recipes SET name = %(name)s, description = %(description)s, instructions = %(instructions)s, date_cooked = %(date_cooked)s, over_under = %(over_under)s, updated_at = now() WHERE (id = {});".format(
            data["id"])
        return connectToMySQL('recipes').query_db(query, data)
    
    @classmethod
    def delete(cls, num):
        query = "DELETE FROM recipes WHERE (id = {});".format(
            num)
        return connectToMySQL('recipes').query_db(query)
