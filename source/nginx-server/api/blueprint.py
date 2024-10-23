from flask import Blueprint, render_template

blueprint = Blueprint("blueprint", __name__, static_folder="static", template_folder="templates")

# @blueprint.route("/home")
# @blueprint.route("/")

# def home():
#     return render_template("Home.html")