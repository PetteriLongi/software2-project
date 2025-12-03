from flask import Blueprint, jsonify, request
from config_redone import RunState
from services_redone import rest
from services_redone import travel_to_index
import io, sys

Menu_redone = Blueprint('Menu_redone', __name__)

def show_commands():
    return "Choose: [1] Travel  [2] Inventory  [3] Rest  [H] Help  [Q] Quit"

def show_help():
    return """HELP

Game Menu
[1] Travel [2] Inventory [3] Rest [H] Help [Q] Quit"""


@Menu_redone.route("/show_commands")
def Commandments():
    return jsonify({"output": show_commands()})

@Menu_redone.route("/show_help")
def Help_showing():
    return jsonify({"output": show_help()})
