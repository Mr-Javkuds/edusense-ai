# Gunakan Python 3.10 sebagai dasar
FROM python:3.10

# Set working directory
WORKDIR /code

# Install library sistem yang dibutuhkan OpenCV & InsightFace
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt dulu (biar cache Docker jalan optimal)
COPY ./requirements.txt /code/requirements.txt

# Install dependencies Python
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy semua file codingan kamu ke dalam container
COPY . /code

# Beri hak akses ke folder cache (Penting untuk Hugging Face Spaces)
RUN mkdir -p /code/cache && chmod -R 777 /code/cache
ENV INSIGHTFACE_HOME=/code/cache

# Buat folder-folder yang dibutuhkan aplikasi
RUN mkdir -p /code/logs /code/temp_videos /code/hasil_crop /code/hasil_crop/reports /code/laporan_excel /code/a114109 /code/static

# Set environment variables untuk production
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port untuk dokumentasi
EXPOSE 7860

# Perintah untuk menjalankan aplikasi
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]