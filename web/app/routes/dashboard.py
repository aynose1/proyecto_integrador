from flask import Blueprint, render_template

from app.decorators import admin_required

bp = Blueprint("dashboard", __name__)


@bp.route("/")
@admin_required
def index():
    return render_template("dashboard/index.html")
