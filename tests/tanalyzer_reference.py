from pathlib import Path

import pytest

from analyzer import extract_notes, compare_performances


PROJECT_FOLDER = Path(__file__).resolve().parent.parent
SAMPLES_FOLDER = PROJECT_FOLDER / "samples"


def analyze(student_filename, reference_filename="reference_scale.mid",):
    reference_notes = extract_notes(
        str(SAMPLES_FOLDER / reference_filename)
    )

    student_notes = extract_notes(
        str(SAMPLES_FOLDER / student_filename)
    )

    return compare_performances(
        reference_notes,
        student_notes,
    )


def test_correct_performance():
    report = analyze("reference_scale.mid")

    assert report["pitch_score"] == pytest.approx(100)
    assert report["timing_score"] == pytest.approx(100)
    assert report["duration_score"] == pytest.approx(100)
    assert report["velocity_score"] == pytest.approx(100)
    assert report["overall_score"] == pytest.approx(100)


def test_incorrect_pitch():
    report = analyze("student_scale.mid")

    f_note = next(
        result
        for result in report["note_results"]
        if result["expected"] == "F4"
    )

    assert f_note["played"] == "F#4"
    assert f_note["pitch_result"] == "Incorrect"


def test_missing_note():
    report = analyze("student_missing_scale.mid")

    missing_note = next(
        result
        for result in report["note_results"]
        if result["pitch_result"] == "Missing"
    )

    assert missing_note["expected"] == "F4"
    assert missing_note["played"] == "-"


def test_extra_note():
    report = analyze("student_extra_scale.mid")

    extra_note = next(
        result
        for result in report["note_results"]
        if result["pitch_result"] == "Extra"
    )

    assert extra_note["expected"] == "-"
    assert extra_note["played"] == "F#4"


def test_expression_mistakes():
    report = analyze("student_expression_scale.mid")

    f_note = next(
        result
        for result in report["note_results"]
        if result["expected"] == "F4"
    )

    assert f_note["duration_result"] == "0.50 beats too short"
    assert f_note["velocity_result"] == "30 levels softer"

    assert report["duration_score"] == pytest.approx(87.5)
    assert report["velocity_score"] == pytest.approx(87.5)


def test_two_consecutive_missing_notes():
    report = analyze("student_two_missing_scale.mid")

    missing_notes = [
        result["expected"]
        for result in report["note_results"]
        if result["pitch_result"] == "Missing"
    ]

    assert missing_notes == ["E4", "F4"]

    g_note = next(
        result
        for result in report["note_results"]
        if result["expected"] == "G4"
    )

    assert g_note["played"] == "G4"
    assert g_note["pitch_result"] == "Correct"


def test_two_consecutive_extra_notes():
    report = analyze("student_two_extra_scale.mid")

    extra_notes = [
        result["played"]
        for result in report["note_results"]
        if result["pitch_result"] == "Extra"
    ]

    assert extra_notes == ["C#4", "D#4"]

    d_note = next(
        result
        for result in report["note_results"]
        if result["expected"] == "D4"
    )

    assert d_note["played"] == "D4"
    assert d_note["pitch_result"] == "Correct"


def test_repeated_pitch_uses_correct_occurrence():
    report = analyze(
        "student_repeated_missing.mid",
        "reference_repeated.mid",
    )

    results = report["note_results"]

    assert results[0]["expected"] == "C4"
    assert results[0]["played"] == "C4"
    assert results[0]["pitch_result"] == "Correct"

    assert results[1]["expected"] == "C4"
    assert results[1]["played"] == "-"
    assert results[1]["pitch_result"] == "Missing"

    assert results[2]["expected"] == "D4"
    assert results[2]["played"] == "D4"
    assert results[2]["pitch_result"] == "Correct"


def test_different_tick_resolutions():
    report = analyze(
        "student_high_resolution_scale.mid"
    )

    assert report["pitch_score"] == pytest.approx(100)
    assert report["timing_score"] == pytest.approx(100)
    assert report["duration_score"] == pytest.approx(100)
    assert report["velocity_score"] == pytest.approx(100)
    assert report["overall_score"] == pytest.approx(100)