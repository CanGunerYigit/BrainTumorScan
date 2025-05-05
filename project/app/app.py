from flask import Flask, render_template, request, send_from_directory
import numpy as np
import os
import shutil
from model import image_pre, predict, generate_heatmap

app = Flask(__name__)

# Klasör yolları
STATIC_FOLDER = 'C:/Users/TR/Desktop/project/app/static'
UPLOAD_FOLDER = 'C:/Users/TR/Desktop/project/app/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    result = ''
    show_heatmap = False

    if request.method == 'POST':
        if 'file1' not in request.files:
            return 'Formda "file1" bulunamadı!'
        
        file1 = request.files['file1']
        filename = file1.filename

        if '.' not in filename or filename.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS:
            return 'Desteklenmeyen dosya türü!'

        # Orijinal görseli uploads/output.jpg olarak kaydet
        original_path = os.path.join(UPLOAD_FOLDER, 'output.jpg')
        file1.save(original_path)

        # Model işlemi için static klasörüne kopyala
        model_input_path = os.path.join(STATIC_FOLDER, 'output.jpg')
        shutil.copy(original_path, model_input_path)

        # Tahmin ve heatmap üret
        data = image_pre(model_input_path)
        probability = predict(data)
        generate_heatmap(model_input_path)

        # Sonuç metni
        percentage = round(probability * 100, 2)

        if probability <= 0.5:
            show_heatmap = True
            tumor_percentage = round((1 - probability) * 100, 2)

            if tumor_percentage == 100:
                result = f"""
                <strong>Beyin Tümörü Tespit Edildi</strong><br>
                Risk Oranı: %{tumor_percentage}<br>
                Model, görüntüde %100 oranında tümör tespiti yapmıştır. 
                <strong>Tıbbi uzman tarafından acilen değerlendirilmesi önerilir.</strong>
                """
            elif 70 <= tumor_percentage < 100:
                result = f"""
                <strong>Beyin Tümörü Tespit Edildi</strong><br>
                Risk Oranı: %{tumor_percentage}<br>
                Model, görüntüde yüksek olasılıkla tümör bulunduğunu tahmin etmektedir.
                <strong>Kesin tanı için uzman incelemesi önerilir.</strong>
                """
            elif 50 <= tumor_percentage < 70:
                result = f"""
                <strong>Beyin Tümörü Tespit Edildi</strong><br>
                Risk Oranı: %{tumor_percentage}<br>
                Orta düzeyde tümör ihtimali gözlemlenmiştir.
                <strong>Ek tetkikler gerekebilir.</strong>
                """
            else:
                result = f"<strong>Beyin Tümörü Tespit Edildi</strong><br>Risk Oranı: %{tumor_percentage}"
        else:
            result = f"<strong>Tümör Tespit Edilmedi</strong><br>Güven Oranı: %{percentage}"

    return render_template('index.html', result=result, show_heatmap=show_heatmap)

# uploads klasöründeki görsellere erişim için
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True)
