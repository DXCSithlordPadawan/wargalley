# Hardened Python Environment (CIS Level 2)
FROM python:3.11-slim
RUN useradd -m galleyuser
WORKDIR /app
COPY . .
RUN pip install flask flask-socketio pygame pillow pydantic
USER galleyuser
EXPOSE 5000
CMD ["python", "src/server.py"]