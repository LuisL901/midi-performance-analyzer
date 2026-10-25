from analyzer import analyze
from analyzer import (
    analyze,
    backtrack_alignment,
    count_correct_duration,
    count_on_time,
    create_cost_matrix,
    calculate_score,
    finish_note
)

def test_perfect_performance():
    report = analyze(
        "samples/reference_scale.mid",
        "samples/reference_scale.mid",
    )

    assert report["pitch_score"] == 100
    assert report["timing_score"] == 100
    assert report["duration_score"] == 100
    assert report["velocity_score"] == 100
    assert report["overall_score"] == 100

def test_extra_note_is_detected():
    report = analyze(
        "samples/reference_scale.mid",
        "samples/student_extra_scale.mid",
    )

    aligned_notes = report["aligned_notes"]
    extra_pair = aligned_notes[4]
    note_result = report["note_results"][4]

    assert note_result["position"] == 5
    assert note_result["status"] == "extra"
    assert note_result["expected"] is None
    assert note_result["played"] == "F#4"

    late_result = report["note_results"][5]

    assert late_result["expected"] == "G4"
    assert late_result["played"] == "G4"
    assert late_result["timing_error_beats"] == 1.0
    assert late_result["timing_correct"] is False
    assert late_result["duration_error_beats"] == 0.0
    assert late_result["duration_correct"] is True
    assert late_result["velocity_error"] == 0
    assert late_result["velocity_correct"] is True

    assert len(aligned_notes) == 9
    assert extra_pair["reference"] is None
    assert extra_pair["student"]["pitch"] == 66
    assert round(report["pitch_score"], 1) == 88.9
    assert round(report["timing_score"], 1) == 44.4

def test_missing_note_is_detected():
    report = analyze(
        "samples/reference_scale.mid",
        "samples/student_missing_scale.mid",
    )

    aligned_notes = report["aligned_notes"]
    missing_pair = aligned_notes[3]

    assert len(aligned_notes) == 8
    assert missing_pair["reference"]["pitch"] == 65
    assert missing_pair["student"] is None
    assert report["pitch_score"] == 87.5
    assert report["timing_score"] == 37.5

def test_incorrect_pitch_is_paired():
    report = analyze(
        "samples/reference_scale.mid",
        "samples/student_scale.mid",
    )

    aligned_notes = report["aligned_notes"]
    incorrect_pair = aligned_notes[3]
    note_result = report["note_results"][3]

    assert note_result["status"] == "paired"
    assert note_result["expected"] == "F4"
    assert note_result["played"] == "F#4"
    assert note_result["pitch_correct"] is False

    assert len(aligned_notes) == 8
    assert incorrect_pair["reference"]["pitch"] == 65
    assert incorrect_pair["student"]["pitch"] == 66

    assert report["pitch_score"] == 87.5
    assert report["timing_score"] == 37.5
    assert report["duration_score"] == 100
    assert report["velocity_score"] == 100
    assert round(report["overall_score"], 1) == 73.1

def test_repeated_pitch_uses_correct_occurrence():
    report = analyze(
        "samples/reference_repeated.mid",
        "samples/student_repeated_missing.mid",
    )

    aligned_notes = report["aligned_notes"]

    # The first C should pair with the student's first C.
    assert aligned_notes[0]["reference"]["pitch"] == 60
    assert aligned_notes[0]["student"]["pitch"] == 60

    # The second C should be identified as missing.
    assert aligned_notes[1]["reference"]["pitch"] == 60
    assert aligned_notes[1]["student"] is None

def test_different_tick_resolutions_use_beats():

    reference_notes = [
        {
            "pitch": 60,
            "start_tick": 480,
            "start_beat": 1.0,
            "duration": 480,
            "duration_beats": 1.0,
            "velocity": 80,
        }
    ]

    student_notes = [
        {
            "pitch": 60,
            "start_tick": 960,
            "start_beat": 1.0,
            "duration": 960,
            "duration_beats": 1.0,
            "velocity": 80,
        }
    ]

    matrix = create_cost_matrix(
        reference_notes,
        student_notes,
    )

    aligned_notes = backtrack_alignment(
        matrix,
        reference_notes,
        student_notes,
    )

    assert matrix[1][1] == (0, 0.0)
    assert count_on_time(aligned_notes) == 1
    assert count_correct_duration(aligned_notes) == 1

def test_empty_alignment_returns_zero_score():
    assert calculate_score(0, []) == 0.0

def test_unmatched_note_off_is_ignored():
    active_notes = {}
    completed_notes = []

    finish_note(
        60,
        active_notes,
        completed_notes,
        480,
        480,
    )

    assert completed_notes == []

