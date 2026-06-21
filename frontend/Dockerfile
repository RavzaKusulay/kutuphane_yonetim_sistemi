FROM python:3.10-slim

WORKDIR /app

# Sadece frontend için gerekli olan 3 paketi kuruyoruz
RUN pip install --no-cache-dir streamlit requests pandas

COPY . .

# Streamlit uygulamasını başlatma komutu
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]