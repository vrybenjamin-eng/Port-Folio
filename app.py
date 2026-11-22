import os
from flask import Flask, render_template, abort, url_for
from projets import PROFIL, PROJETS, CV

app = Flask(__name__)

# Securite : si un champ manque dans projets.py, on met une valeur par defaut
# au lieu de faire planter le site.
DEFAUTS = {
    "titre": "[Titre]", "resume": "", "phare": False, "role": "", "duree": "",
    "stack": [], "probleme": "", "solution": "", "choix_technique": "",
    "captures": [], "videos": [], "demo": "", "code": "",
}
for _p in PROJETS:
    for _k, _v in DEFAUTS.items():
        _p.setdefault(_k, _v)
for _k in ("formation", "experience"):
    CV.setdefault(_k, [])
CV.setdefault("competences", {})


@app.context_processor
def helpers():
    def exists(path):
        return bool(path) and os.path.exists(os.path.join(app.static_folder, path))

    def asset(path):
        # Fichier absent -> image de remplacement "Ajoute ta preuve ici"
        return url_for("static", filename=path if exists(path) else "img/placeholder.svg")

    return dict(asset=asset, exists=exists)


@app.route("/")
def index():
    return render_template("index.html", profil=PROFIL, projets=PROJETS, cv=CV)


@app.route("/projet/<slug>")
def projet(slug):
    p = next((x for x in PROJETS if x["slug"] == slug), None)
    if p is None:
        abort(404)
    return render_template("projet.html", profil=PROFIL, p=p)


if __name__ == "__main__":
    app.run(debug=True)
