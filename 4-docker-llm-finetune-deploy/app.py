from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class CourseRequest(BaseModel):
    text: str

@app.post("/extract-course-name/")
async def extract_course_name(request: CourseRequest):
    #inputs = tokenizer(request.text, return_tensors="pt", padding=True, truncation=True)
    #outputs = model(**inputs)
    #predictions = outputs.logits.argmax(dim=-1)
    extracted_names = [request.text]  # placeholder logic
    return {"extracted_course_names": extracted_names}