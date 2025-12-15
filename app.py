
from flask import Flask, render_template, request, redirect, url_for
import cloudinary
import cloudinary.uploader
import os

app = Flask(__name__)

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

ordens = []

@app.route("/")
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", ordens=ordens)

@app.route("/nova-os", methods=["GET", "POST"])
def nova_os():
    if request.method == "POST":
        os_data = {
            "data": request.form.get("data", ""),
            "cliente": request.form.get("cliente", ""),
            "modelo": request.form.get("modelo", ""),
            "placa": request.form.get("placa", ""),
            "km": request.form.get("km", ""),
            "ano": request.form.get("ano", ""),
            "cor": request.form.get("cor", ""),
            "mecanico": request.form.get("mecanico", ""),
            "servicos_executar": request.form.get("servicos_executar", ""),
            "codigo_erro": request.form.get("codigo_erro", ""),
            "combustivel": request.form.get("combustivel", ""),
            "obs": request.form.get("obs", ""),
            "fotos": []
        }

        files_upload = request.files.getlist("fotos")
        for file in files_upload:
            if file and file.filename:
                try:
                    upload = cloudinary.uploader.upload(file, folder="ordens_servico")
                    os_data["fotos"].append(upload.get("secure_url"))
                except Exception as e:
                    print("Erro Cloudinary:", e)

        ordens.append(os_data)
        return redirect(url_for("dashboard"))

    return render_template("os_form.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
