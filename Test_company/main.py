# main.py - FastAPI backend สำหรับ AI Assistant ที่ตอบคำถามและสรุปปัญหาจากเอกสารภายใน

from fastapi import FastAPI
from pydantic import BaseModel
from app.vector_store import load_faiss_index
import uvicorn
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from fastapi.responses import HTMLResponse
import json
from agent import agent_decide_tool

# สร้าง FastAPI instance
app = FastAPI()

# โหลด FAISS index และ LLM ตอนเริ่มแอป
@app.on_event("startup")
async def startup_event():
    global index, texts, metadatas, llm
    index, texts, metadatas = load_faiss_index()  # โหลดเวกเตอร์ + เอกสาร
    model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id)
    llm = pipeline("text-generation", model=model, tokenizer=tokenizer)

# หน้า root
@app.get("/")
async def root():
    return {"message": "AI Assistant is running. Try /ask or /docs"}

# Endpoint สำหรับ list routes ทั้งหมด
@app.get("/routes")
async def list_routes():
    return [route.path for route in app.routes]

# HTML UI แบบง่ายเพื่อส่งคำถาม
@app.get("/ask", response_class=HTMLResponse)
async def ask_page():
    return """
    <!DOCTYPE html>
    <html>
    <head><title>AI Assistant Q&A</title></head>
    <body>
        <h2>Ask the AI Assistant</h2>
        <textarea id="question" rows="4" cols="50" placeholder="Type your question here..."></textarea><br><br>
        <button onclick="submitQuestion()">Ask</button>
        <p><strong>Examples:</strong></p>
        <ul>
            <li>What are the issues reported on email notification?</li>
            <li>What did users say about the search bar?</li>
            <li>Summarize the most common problems reported</li>
        </ul>
        <pre id="response" style="white-space: pre-wrap; background:#eee; padding:10px;"></pre>
        <script>
            async function submitQuestion() {
                const q = document.getElementById("question").value;
                const res = await fetch("/query", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ question: q })
                });
                const data = await res.json();
                document.getElementById("response").innerText = JSON.stringify(data, null, 2);
            }
        </script>
    </body>
    </html>
    """

# Pydantic model สำหรับรับคำถาม
class QueryRequest(BaseModel):
    question: str

# ค้นหาเอกสารที่คล้ายกับคำถาม
def search_similar_documents(question: str, top_k: int = 3):
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2")
    q_emb = model.encode([question])
    import faiss
    D, I = index.search(q_emb, top_k)
    return [texts[i] for i in I[0]]

# ส่ง prompt เข้า LLM แล้วคืนผล
def ask_llm(prompt: str):
    result = llm(prompt, max_new_tokens=300, do_sample=True)
    raw = result[0]['generated_text']
    cleaned = raw.replace("<|user|>", "").replace("<|assistant|>", "").strip()

    try:
        # ถ้า LLM ตอบเป็น JSON ก็ parse เลย
        json_start = cleaned.find("{")
        json_end = cleaned.rfind("}") + 1
        if json_start != -1 and json_end != -1:
            return json.loads(cleaned[json_start:json_end])
    except:
        pass

    # ถ้าไม่ใช่ JSON ก็คืนข้อความดิบ
    return {"answer": cleaned}

# Core API สำหรับประมวลผลคำถาม
@app.post("/query")
async def query(request: QueryRequest):
    agent_result = agent_decide_tool(request.question)  # ให้ agent ตัดสินใจว่าใช้ tool ไหน
    q_type = agent_result["tool"]
    reasoning = agent_result["reasoning"]

    # ดึงเอกสารคล้ายคำถาม
    context_docs = search_similar_documents(request.question)
    context = "\n".join(context_docs)

    if q_type == "qa":
        # ถ้าเป็น Q&A ให้สร้าง prompt เพื่อถาม LLM
        prompt = f"""
        You are an internal assistant. Answer the following based on context:

        Respond ONLY in this JSON format:
        {{ "answer": "string" }}

        Context:
        {context}

        Question: {request.question}
        """
        answer = ask_llm(prompt)
        return {
            "type": "qa",
            "reasoning": reasoning,
            **answer,
            "source": context_docs
        }

    else:
        # ถ้าเป็น summary ให้สรุปปัญหาในรูปแบบ structured JSON
        prompt = f"""
        You are an assistant that summarizes issues from bug reports.

        Respond ONLY in JSON:
        {{
          "reported_issues": ["..."],
          "affected_features": ["..."],
          "severity": ["High", "Medium"]
        }}

        Context:
        {context}
        """
        summary = ask_llm(prompt)
        return {
            "type": "summary",
            "reasoning": reasoning,
            **summary,
            "source": context_docs
        }

# รัน FastAPI บน localhost ถ้ารันแบบ Python ปกติ (ไม่ใช่ Docker)
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
