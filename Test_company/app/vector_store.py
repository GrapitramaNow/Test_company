import pickle
import os
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer

# ฟังก์ชันสำหรับโหลด FAISS index และข้อมูลประกอบ (texts และ metadata)
def load_faiss_index(index_path="index"):
    # โหลด embedding model สำหรับเปรียบเทียบความคล้ายกันของข้อความ
    embedder = SentenceTransformer("all-MiniLM-L6-v2")

    # โหลด FAISS vector store ที่ถูกบันทึกไว้
    db = FAISS.load_local(index_path, HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2"))

    # โหลดข้อความ (text chunks) ที่ถูกใช้ในการสร้าง index
    with open(os.path.join(index_path, "texts.pkl"), "rb") as f:
        texts = pickle.load(f)

    # โหลด metadata ที่แนบมากับแต่ละข้อความ
    with open(os.path.join(index_path, "metadata.pkl"), "rb") as f:
        metadatas = pickle.load(f)

    # คืนค่า FAISS index, ข้อความ และ metadata
    return db.index, texts, metadatas
