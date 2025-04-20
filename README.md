AI Assistant for Product & Engineering Team
ระบบผู้ช่วย AI สำหรับทีม Product และ Engineering ใช้ในการสรุปปัญหา (Issue Summarization) และตอบคำถาม (Document Q&A) จากเอกสารภายใน เช่น bug reports และ user feedback

ขั้นตอนการติดตั้ง
1. เตรียมเครื่อง
ติดตั้ง Docker Desktop (จำเป็น)
พื้นที่ว่างขั้นต่ำ: 5GB (เพื่อโหลดและรันโมเดล LLM)

2. Clone โปรเจกต์
git clone https://github.com/GrapitramaNow/Test_company.git
cd Test_company

3. สร้าง Docker Image
docker build -t ai-assistant .

4. รันระบบ
docker run -p 8000:8000 ai-assistant

วิธีใช้งาน
เปิดเบราว์เซอร์แล้วไปที่:
http://localhost:8000/ask

กรอกคำถาม เช่น:
What are the issues reported on email notification?

What did users say about the search bar?

Summarize the most common problems reported

โครงสร้างโปรเจกต์
Test_company/
├── app/
│   ├── ingestion.py           # เตรียมข้อมูล สร้าง FAISS Index
│   ├── vector_store.py        # โหลดเวกเตอร์จากดิสก์
├── agent.py                   # Agent เลือกว่าจะใช้ Q&A หรือ Summary
├── main.py                    # FastAPI app
├── data/                      # เอกสาร .txt (bug report / feedback)
├── index/                     # FAISS index และ metadata
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker configuration

ข้อมูลเพิ่มเติม
ใช้โมเดล LLM: TinyLlama-1.1B-Chat-v1.0 จาก HuggingFace
Embedding: all-MiniLM-L6-v2
Vector Store: FAISS
Framework: FastAPI
