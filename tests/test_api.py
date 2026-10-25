from fastapi.testclient import TestClient
from pathlib import Path
from api import app


client = TestClient(app)


def test_home():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "MIDI Performance Analyzer API is running"
    }

def test_rejects_non_midi_extension():
    response = client.post(
        "/analyze",
        files={
            "reference_file": (
                "reference.pdf",
                b"not MIDI data",
                "application/pdf",
            ),
            "student_file": (
                "student.mid",
                b"not MIDI data",
                "audio/midi",
            ),
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Both uploads must be MIDI files."
    }

def test_rejects_invalid_midi_contents():
    response = client.post(
        "/analyze",
        files={
            "reference_file": (
                "reference.mid",
                b"not actual MIDI data",
                "audio/midi",
            ),
            "student_file": (
                "student.mid",
                b"not actual MIDI data",
                "audio/midi",
            ),
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": (
            "One of the uploaded MIDI files "
            "could not be read."
        )
    }

def test_analyzes_valid_midi_files():
    sample_path = (
        Path(__file__).parent.parent
        / "samples"
        / "reference_scale.mid"
    )

    with sample_path.open("rb") as reference:
        with sample_path.open("rb") as student:
            response = client.post(
                "/analyze",
                files={
                    "reference_file": (
                        "reference.mid",
                        reference,
                        "audio/midi",
                    ),
                    "student_file": (
                        "student.mid",
                        student,
                        "audio/midi",
                    ),
                },
            )

    assert response.status_code == 200

    report = response.json()

    assert report["pitch_score"] == 100.0
    assert report["timing_score"] == 100.0
    assert report["duration_score"] == 100.0
    assert report["velocity_score"] == 100.0
    assert report["overall_score"] == 100.0

def test_rejects_empty_reference_midi():
    samples = Path(__file__).parent.parent / "samples"

    with (samples / "empty.mid").open("rb") as reference:
        with (samples / "reference_scale.mid").open("rb") as student:
            response = client.post(
                "/analyze",
                files={
                    "reference_file": (
                        "empty.mid",
                        reference,
                        "audio/midi",
                    ),
                    "student_file": (
                        "student.mid",
                        student,
                        "audio/midi",
                    ),
                },
            )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Reference MIDI file contains no notes."
    }

def test_rejects_empty_student_midi():
    samples = Path(__file__).parent.parent / "samples"

    with (samples / "reference_scale.mid").open("rb") as reference:
        with (samples / "empty.mid").open("rb") as student:
            response = client.post(
                "/analyze",
                files={
                    "reference_file": (
                        "reference.mid",
                        reference,
                        "audio/midi",
                    ),
                    "student_file": (
                        "empty.mid",
                        student,
                        "audio/midi",
                    ),
                },
            )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student MIDI file contains no notes."
    }

