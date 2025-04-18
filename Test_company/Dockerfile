# ใช้ Python 3.9.22 ที่มีขนาดเล็กเป็น base image
FROM python:3.9.22-slim

# ตั้ง working directory ภายใน container
WORKDIR /app

# ติดตั้งเครื่องมือที่จำเป็นสำหรับการ build package ต่าง ๆ
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# คัดลอก requirements.txt มาไว้ใน container
COPY requirements.txt ./

# อัปเกรด pip และติดตั้ง dependencies ที่ระบุในไฟล์ requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# คัดลอกโค้ดทั้งหมดจากโปรเจกต์เข้า container
COPY . .

# เปิดพอร์ต 8000 เพื่อให้ container รับ request ภายนอกได้
EXPOSE 8000

# รัน FastAPI ผ่าน Uvicorn เมื่อ container เริ่มทำงาน
CMD ["bash", "-c", "python app/ingestion.py && uvicorn main:app --host 0.0.0.0 --port 8000"]
