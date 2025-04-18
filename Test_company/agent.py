def agent_decide_tool(question: str) -> dict:
    # แปลงคำถามให้เป็น lowercase เพื่อให้ง่ายต่อการตรวจสอบคำสำคัญ
    q = question.lower()

    # ตรวจสอบคำถามว่ามีคำที่เกี่ยวข้องกับการสรุปปัญหาหรือไม่
    for kw in ["bug", "issue", "problem", "severity", "summarize", "summary"]:
        if kw in q:
            return {
                "tool": "summary",
                "reasoning": f"The keyword '{kw}' indicates the question is about summarizing issues. Therefore, the 'summary' tool was selected."
            }

    # หากไม่พบคำสำคัญเกี่ยวกับ summary ให้ใช้เครื่องมือถาม-ตอบแทน
    return {
        "tool": "qa",
        "reasoning": "No keywords related to summarizing were found. Therefore, the 'qa' tool was selected to retrieve information from documents."
    }
