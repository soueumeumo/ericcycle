from flask import Flask, render_template, request, redirect, url_for
import os

try:
    import cloudinary
    import cloudinary.uploader
    CLOUDINARY_OK = True
except:
    CLOUDINARY_OK = False

app = Flask(__name__)

# Só configura Cloudinary se TODAS as variáveis existirem
if CLOUDINARY_OK and all([
    os.getenv("CLOUDINARY_CLOUD_NAME"),
    os.getenv("CLOUDINARY_API_KEY"),
    os.getenv("CLOUDINARY_API_SECRET")
]):
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET")
    )
else:
    CLOUDINARY_OK = False
    print("⚠️ Cloudinary desativado")

ordens = []

@app.route("/")
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", ordens=ordens)

@app.route("/nova-os", methods=["GET", "POST"])
def nova_os():
    try:
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

            if CLOUDINARY_OK:
                for file in request.files.getlist("fotos"):
                    if file and file.filename:
                        try:
                            upload = cloudinary.uploader.upload(
                                file,
                                folder="ordens_servico"
                            )
                            os_data["fotos"].append(upload.get("secure_url"))
                        except Exception as e:
                            print("Erro upload:", e)

            ordens.append(os_data)
            return redirect(url_for("dashboard"))

        return render_template("os_form.html")

    except Exception as e:
        print("🔥 ERRO GERAL NA OS:", e)
        return "Erro interno ao salvar OS", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

