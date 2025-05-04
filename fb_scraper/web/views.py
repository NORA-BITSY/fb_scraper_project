from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required
from fb_scraper.web.forms import GroupForm
from fb_scraper.core.tasks import scrape_group
from fb_scraper.db.models import Post
from fb_scraper.db.init import Session
import yaml

bp = Blueprint("views", __name__)

@bp.route("/")
@login_required
def index():
    return render_template("index.html")

@bp.route("/groups", methods=["GET", "POST"])
@login_required
def groups():
    form = GroupForm()
    cfg_path = "scrape_config.yaml"
    cfg = yaml.safe_load(open(cfg_path))
    if form.validate_on_submit():
        cfg["groups"][form.group_id.data] = form.url.data
        yaml.safe_dump(cfg, open(cfg_path, "w"))
        return redirect(url_for("views.groups"))
    return render_template("groups.html", cfg=cfg["groups"], form=form)

@bp.route("/groups/<gid>/scrape", methods=["POST"])
@login_required
def trigger(gid):
    cfg = yaml.safe_load(open("scrape_config.yaml"))
    scrape_group.delay(cfg["groups"][gid], gid)
    return ("", 204)

@bp.route("/posts")
@login_required
def posts():
    q = request.args.get("q")
    sess = Session()
    if q:
        rows = sess.execute(
            "SELECT * FROM posts WHERE text ILIKE :q ORDER BY published_at DESC LIMIT 100",
            {"q": f"%{q}%"}
        )
    else:
        rows = sess.execute("SELECT * FROM posts ORDER BY published_at DESC LIMIT 100")
    return render_template("posts.html", rows=rows)
