from typing import Annotated

from fastapi import FastAPI, File, HTTPException, UploadFile

from analyzer import extract_notes, compare_performances


app = FastAPI(
    title="MIDI Performance Analyzer",
    description=(
        "Compare a student MIDI performance "
        "against a reference performance."
    ),
)


@app.get("/")
def home():
    return {
        "message": "MIDI Performance Analyzer API is running"
    }


@app.post("/analyze")
async def analyze_performance(
    reference_file: Annotated[
        UploadFile,
        File(description="The correct reference MIDI file"),
    ],
    student_file: Annotated[
        UploadFile,
        File(description="The student's MIDI performance"),
    ],
):
    uploaded_files = [reference_file, student_file]

    for uploaded_file in uploaded_files:
        filename = uploaded_file.filename

        if filename is None or not filename.lower().endswith(
            (".mid", ".midi")
        ):
            raise HTTPException(
                status_code=400,
                detail="Both uploads must be MIDI files.",
            )

    await reference_file.seek(0)
    await student_file.seek(0)

    try:
        reference_notes = extract_notes(reference_file.file)
        student_notes = extract_notes(student_file.file)

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail="One of the uploaded MIDI files could not be read.",
        ) from error

    if not reference_notes:
        raise HTTPException(
            status_code=400,
            detail="The reference MIDI file contains no notes.",
        )

    if not student_notes:
        raise HTTPException(
            status_code=400,
            detail="The student MIDI file contains no notes.",
        )

    report = compare_performances(
        reference_notes,
        student_notes,
    )

    return report