from flask import render_template, request, jsonify, send_file, redirect, url_for, session
import random
import time
import os

from core.utils import load_study_material, load_txt
from core.prompt import generate_exam_with_quality_control
from core.prompt import generate_exam_with_curator_loop
from core.agents.learning_goal_generator import run_learning_goal_generator
from core.agents.output_curator import output_curator
from core.apikey import apikey

from file_handler import save_file
from document_generator import generate_docx, generate_pdf


admin_email = os.getenv("ADMIN_email")
admin_password = os.getenv("ADMIN_password")


def register_routes(app):

    @app.route("/", methods=["GET", "POST"])
    @app.route("/login", methods=["GET", "POST"])
    def inloggen():
        if request.method == "POST":
            email = request.form.get("email").strip().lower()
            password = request.form.get("password", "")

            if email == admin_email and password == admin_password:
                code = str(random.randint(100000, 999999))

                session["pending_2fa"] = True
                session["2fa_code"] = code
                session["2fa_expires"] = time.time() + 300
                session["2fa_attempts"] = 0

                print("2FA CODE:", code)

                return redirect(url_for("two_factor"))

            return render_template("login.html", error="Ongeldige inloggegevens.")

        return render_template("login.html")

    @app.route("/two-factor")
    def two_factor():
        if not session.get("pending_2fa"):
            return redirect(url_for("inloggen"))

        return render_template("tweefac_auth.html")

    @app.route("/auth/verify-twofactor", methods=["POST"])
    def verify_twofactor():
        if not session.get("pending_2fa"):
            return "Tweefactor niet gestart", 400

        if time.time() > session.get("2fa_expires", 0):
            return "2FA_EXPIRED", 400

        attempts = session.get("2fa_attempts", 0)

        if attempts >= 3:
            session.pop("pending_2fa", None)
            session.pop("2fa_code", None)
            session.pop("2fa_expires", None)
            session.pop("2fa_attempts", None)

            return "2FA_TOO_MANY_ATTEMPTS", 400

        code = request.form.get("code", "").strip()

        if code != session.get("2fa_code"):
            session["2fa_attempts"] = attempts + 1
            return "2FA_INCORRECT", 400

        session["logged_in"] = True
        session.pop("pending_2fa", None)
        session.pop("2fa_code", None)
        session.pop("2fa_expires", None)
        session.pop("2fa_attempts", None)

        return "2FA_SUCCESS", 200

    @app.route("/auth/resend-twofactor", methods=["POST"])
    def resend_twofactor():
        if not session.get("pending_2fa"):
            return "Tweefactor niet gestart", 400

        code = str(random.randint(100000, 999999))

        session["2fa_code"] = code
        session["2fa_expires"] = time.time() + 300
        session["2fa_attempts"] = 0

        print("Nieuwe 2FA CODE:", code)

        return "2FA_RESENT", 200

    @app.route("/index")
    def index():
        if not session.get("logged_in"):
            return redirect(url_for("inloggen"))

        return render_template("index.html")

    @app.route("/settings")
    def settings():
        if not session.get("logged_in"):
            return redirect(url_for("inloggen"))

        return render_template("settings.html")

    @app.route("/generate-subdoelen", methods=["POST"])
    def generate_subdoelen_route():
        onderwerp = request.form.get("onderwerp", "")
        niveau = request.form.get("niveau", "")
        leerdoelen_path = save_file(request.files.get("leerdoelen"))
        leerdoelen = load_study_material(leerdoelen_path) if leerdoelen_path else ""

        subdoelen = run_learning_goal_generator(leerdoelen, niveau, onderwerp, apikey)

        return jsonify(generated_subdoelen=str(subdoelen))

    @app.route("/generate", methods=["POST"])
    def generate():
        onderwerp = request.form.get("onderwerp", "")
        niveau = request.form.get("niveau", "")
        selection = request.form.get("selection", "")
        extra_instructions = request.form.get("extra_instructions", "")
        subgoals_mode = request.form.get("subgoals_mode", "generate")
        action = request.form.get("action", "")

        study_material_path = save_file(request.files.get("study_material"))
        leerdoelen_path = save_file(request.files.get("leerdoelen"))
        voorbeeldvragen_path = save_file(request.files.get("voorbeeldvragen"))
        subdoelen_path = save_file(request.files.get("subdoelen_file"))

        study_material = load_study_material(study_material_path) if study_material_path else ""
        leerdoelen = load_study_material(leerdoelen_path) if leerdoelen_path else ""
        voorbeeldvragen = load_txt(voorbeeldvragen_path) if voorbeeldvragen_path else ""

        subdoelen = ""

        if subdoelen_path:
            print("DEBUG: gebruiker heeft de subdoelenbestand aangeleverd")
            subdoelen = load_study_material(subdoelen_path)

        elif subgoals_mode == "generate":
            subdoelen = run_learning_goal_generator(
                leerdoelen=leerdoelen,
                niveau=niveau,
                onderwerp=onderwerp,
                apikey=apikey
            )

        else:
            subdoelen = leerdoelen

        if action == "generate_subdoelen":
            return render_template(
                "index.html",
                generated_subdoelen=subdoelen
            )

        aantal_vragen = {
            "Onthouden": int(request.form.get("aantal_onthouden") or 0),
            "Begrijpen": int(request.form.get("aantal_begrijpen") or 0),
            "Toepassen": int(request.form.get("aantal_toepassen") or 0),
        }

        if sum(aantal_vragen.values()) == 0:
            return jsonify(exam_text="Fout: Voer het aantal gewenste vragen in.")

        print("DEBUG MAIN.PY: subdoelen-call wordt gebruikt")
        print("DEBUG subdoelen:", subdoelen[:100] if subdoelen else "GEEN SUBDOELEN")

        exam_text, curator_result = generate_exam_with_curator_loop(
            onderwerp=onderwerp,
            blooms=request.form.getlist("blooms"),
            niveau=niveau,
            subdoelen=subdoelen,
            study_material=study_material,
            voorbeeldvragen=voorbeeldvragen,
            aantal_vragen=aantal_vragen,
            apikey=apikey
            )

        if "Error:" in exam_text or "Fout:" in exam_text:
            return jsonify(exam_text="Er ging iets mis in de generatie, probeer het opnieuw.")

        if len(exam_text) < 20:
            return jsonify(exam_text="Het gegenereerde examen is te kort. Probeer opnieuw.")


        return jsonify(exam_text=exam_text, curator_result=curator_result)

    @app.route("/download/<format>", methods=["POST"])
    def download(format):
        text = request.form.get("exam_text", "")

        if format == "docx":
            buffer = generate_docx(text)
            return send_file(buffer, download_name="examen.docx", as_attachment=True)

        elif format == "pdf":
            buffer = generate_pdf(text)
            return send_file(buffer, download_name="examen.pdf", as_attachment=True)