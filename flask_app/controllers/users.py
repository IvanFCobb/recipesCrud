from flask_app.models.user import User
from flask_app.models.recipe import Recipe
from flask_app import app
from flask import render_template, redirect, request, session, flash
from flask_bcrypt import Bcrypt
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
bcrypt = Bcrypt(app)


@app.route('/', methods=['get'])
def register_login():
    return render_template("index.html")

@app.route('/recipes/new', methods=['get'])
def create_recipe_view():
    if 'user_id' not in session:
        return redirect ("/")
    user = User.get_by_id(session['user_id'])
    return render_template("new_recipe.html", user=user)


@app.route('/recipes', methods=['get'])
def recipes():
    if 'user_id' not in session:
        return redirect ("/")
    user = User.get_by_id(session['user_id'])
    recipes = Recipe.get_all_recipes_with_creator()
    return render_template("show_recipes.html", user=user, recipes=recipes)

    
@app.route('/recipes/<int:num>', methods=['get'])
def one_recipe(num):
    if 'user_id' not in session:
        return redirect ("/")
    user = User.get_by_id(session['user_id'])
    recipe = Recipe.get_by_id_with_creator(num)
    return render_template("show_one_recipe.html", user=user, recipe=recipe)

@app.route('/recipes/edit/<int:num>', methods=['get'])
def one_recipe_edit(num):
    if 'user_id' not in session:
        return redirect ("/")
    user = User.get_by_id(session['user_id'])
    recipe = Recipe.get_by_id(num)
    print(recipe.date_cooked)
    return render_template("edit_recipe.html", user=user, recipe=recipe)

@app.route('/recipes/delete/<int:num>', methods=['get'])
def one_recipe_delete(num):
    if 'user_id' not in session:
        return redirect ("/")
    Recipe.delete(num)
    return redirect("/recipes")



@app.route('/login', methods=['POST'])
def login():
    data = {"email": request.form["email"]}
    user_in_db = User.get_by_email(data["email"])
    if not user_in_db:
        flash("Invalid Email/Password", "login")
        return redirect("/")
    if not bcrypt.check_password_hash(user_in_db.password, request.form['password']):
        flash("Invalid Email/Password", "login")
        return redirect('/')
    session['user_id'] = user_in_db.id
    return redirect("/recipes")


@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect("/")

@app.route('/create_user', methods=["POST"])
def register():       
    if User.is_valid_user(request.form):
        pw_hash = bcrypt.generate_password_hash(request.form['password'])
        data = {
        "fname": request.form['fname'],
        "lname": request.form['lname'],
        "email": request.form['email'],
        "password": pw_hash,
        }
        user_id = User.save(data)
        session['user_id'] = user_id
        return redirect("/recipes")
    else:
        return redirect('/')

@app.route('/create_recipe', methods=["POST"])
def newRecipe():
    if 'user_id' not in session:
        return redirect ("/")
    if Recipe.is_valid_recipe(request.form):
        data = {
            "name": request.form['name'],
            "description": request.form['description'],
            "instructions": request.form['instructions'],
            "date_cooked": request.form['date_cooked'],
            "over_under": request.form['over_under'],
            "user_id": session['user_id'],
        }
        Recipe.save(data)
        return redirect("/recipes")
    else: 
        return redirect('/recipes/new')

@app.route('/edit_recipe', methods=["POST"])
def edit_recipe():
    if 'user_id' not in session:
        return redirect ("/")
    if Recipe.is_valid_recipe(request.form): 
        data = {
            "id": request.form["id"],
            "name": request.form['name'],
            "description": request.form['description'],
            "instructions": request.form['instructions'],
            "date_cooked": request.form['date_cooked'],
            "over_under": request.form['over_under'],
            "user_id": session['user_id'],
        }
        Recipe.edit(data)
        return redirect("/recipes")
    else:
        return redirect("/recipes/edit/{}".format(request.form["id"]))
