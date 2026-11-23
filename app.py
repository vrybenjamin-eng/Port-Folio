import os
from flask import Flask, render_template, abort, url_for, Response
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


# Cherche le fichier dans static/ puis dans les sous-dossiers usuels,
# pour que "app1.jpeg" marche qu'il soit dans static/ ou static/img/.
DOSSIERS = ["", "img/", "images/", "videos/", "video/"]


def resolve(path):
    if not path:
        return None
    for d in DOSSIERS:
        if os.path.isfile(os.path.join(app.static_folder, d + path)):
            return d + path
    return None


@app.context_processor
def helpers():
    def exists(path):
        return resolve(path) is not None

    def asset(path):
        return url_for("static", filename=resolve(path) or path)

    return dict(asset=asset, exists=exists)


@app.route("/diagnostic")
def diagnostic():
    """Page de test : http://127.0.0.1:5000/diagnostic"""
    lignes = ["FICHIERS ATTENDUS PAR projets.py", ""]
    attendus = [("photo", PROFIL["photo"]), ("cv", PROFIL["cv_pdf"])]
    for p in PROJETS:
        attendus += [(p["slug"], f) for f in p["captures"] + p["videos"]]
    for nom, f in attendus:
        r = resolve(f)
        lignes.append(("OK      " if r else "MANQUANT") + f"  {f}   ({nom})" + (f" -> static/{r}" if r else ""))
    lignes += ["", "FICHIERS PRESENTS DANS static/", ""]
    for racine, _, fichiers in os.walk(app.static_folder):
        for f in fichiers:
            lignes.append(os.path.relpath(os.path.join(racine, f), app.static_folder).replace(os.sep, "/"))
    return Response("\n".join(lignes), mimetype="text/plain; charset=utf-8")


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