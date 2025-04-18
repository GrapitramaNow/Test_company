import os
import pickle
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer
from langchain.schema import Document

#โหลดเอกสารทั้งหมดจากโฟลเดอร์ (เฉพาะ .txt) และสร้างเป็น Document objects
def load_documents_from_folder(folder_path="data"):
    docs = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
                text = f.read()
                # 📝 ใส่ metadata เป็นชื่อไฟล์
                docs.append(Document(page_content=text, metadata={"source": filename}))
    return docs

#ตัดเอกสารให้เป็นชิ้นเล็กๆ (chunks) เพื่อให้ LLM ประมวลผลได้ดีขึ้น
def split_documents(documents, chunk_size=500, chunk_overlap=50):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_documents(documents)

#สร้าง FAISS vector index + บันทึกไฟล์ index และ metadata ต่างๆ
def save_faiss_index(chunks, index_path="index"):
    os.makedirs(index_path, exist_ok=True)

    # ใช้ HuggingFace model เพื่อแปลงข้อความเป็น embedding
    embedder = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    #สร้าง FAISS index จากเอกสารที่แบ่งแล้ว
    db = FAISS.from_documents(chunks, embedder)

    #บันทึก index ลงในโฟลเดอร์ที่กำหนด
    db.save_local(index_path)

    #บันทึก texts และ metadata แยกต่างหาก (ใช้สำหรับอ้างอิงเวลาค้นหา)
    with open(os.path.join(index_path, "texts.pkl"), "wb") as f:
        pickle.dump([doc.page_content for doc in chunks], f)

    with open(os.path.join(index_path, "metadata.pkl"), "wb") as f:
        pickle.dump([doc.metadata for doc in chunks], f)

#จุดเริ่มต้นของสคริปต์ — รันทุกอย่างเมื่อถูกเรียกตรงๆ (เช่น: python ingestion.py)
if __name__ == "__main__":
    raw_docs = load_documents_from_folder("data")     # โหลดไฟล์เอกสาร
    chunks = split_documents(raw_docs)                # ตัดเอกสารเป็นชิ้นเล็ก
    save_faiss_index(chunks)                          # สร้างและบันทึก index
