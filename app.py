from flask import Flask, request, render_template, send_file
from converter import convert_excel_to_ps_txt # Importação corrigida
import os
import io

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("ps_txt.html")

@app.route('/convert', methods=['POST'])
def convert():
    """
    Gera um TXT com o Layout PS.txt a partir de um arquivo Excel.
    """
    file = request.files.get("excel_file")
    if not file:
        return "Nenhum arquivo Excel foi enviado.", 400

    try:
        txt_stream = convert_excel_to_ps_txt(file)
    except ValueError as e:
        return str(e), 400
    except Exception as e:
        return f"Erro inesperado durante a conversão: {e}", 500

    return send_file(
        txt_stream,
        as_attachment=True,
        download_name="Layout PS.txt",
        mimetype="text/plain"
    )

@app.route('/download_template')
def download_template():
    """Permite o download do modelo de planilha de Planos de Saúde."""
    template_path = os.path.join(os.getcwd(), "MODELODEPLANILHA-PLANODESAUDEAUTONOMOS.XLSX")
    return send_file(
        template_path,
        as_attachment=True,
        download_name="MODELODEPLANILHA-PLANODESAUDEAUTONOMOS.XLSX",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

