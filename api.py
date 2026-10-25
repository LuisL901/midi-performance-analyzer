from typing import Annotated
from analyzer import analyze
from fastapi import FastAPI, File, UploadFile, HTTPException
app = FastAPI()

@app.get("/")
def home():
    return{
        "message": "MIDI Performance Analyzer API is running"
    }

@app.post("/analyze")
async def analyze_performance(
    reference_file: Annotated[UploadFile,File()],
    student_file: Annotated[UploadFile,File()]
):
    uploaded_files = [reference_file,student_file]
    for file in uploaded_files:
        filename = file.filename
        if filename is None or not filename.lower().endswith((".mid",".midi")):
            raise HTTPException(
                status_code=400,
                detail="Both uploads must be MIDI files."
            )
    try:
        report = analyze(
            reference_file.file,
            student_file.file,
        )  
    except (OSError, EOFError) as error:
        raise HTTPException(
            status_code=400,
            detail="One of the uploaded MIDI files could not be read."
        ) from error
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error


    return report