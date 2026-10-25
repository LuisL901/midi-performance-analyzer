import mido

NOTE_NAMES = [
    "C",
    "C#",
    "D",
    "D#",
    "E",
    "F",
    "F#",
    "G",
    "G#",
    "A",
    "A#",
    "B",
]


def midi_note_to_name(note_number):
    note_name = NOTE_NAMES[note_number % 12]
    octave = (note_number // 12) - 1

    return f"{note_name}{octave}"


def extract_notes(file_source):
    if hasattr(file_source, "read"):
        # FastAPI uploaded file or another open file object
        midi = mido.MidiFile(file=file_source)
    else:
        # String or Path pointing to a file on disk
        midi = mido.MidiFile(file_source)
        
    completed_notes = []

    for track in midi.tracks:
        current_tick = 0
        active_notes = {}

        for message in track:
            current_tick += message.time

            if message.type == "note_on" and message.velocity > 0:
                active_notes[message.note] = {
                    "start_tick": current_tick,
                    "velocity": message.velocity,
                }

            elif message.type == "note_off" or (
                message.type == "note_on" and message.velocity == 0
            ):
                if message.note in active_notes:
                    note_data = active_notes.pop(message.note)

                    duration_ticks = (
                        current_tick - note_data["start_tick"]
                    )

                    duration_beats = (
                        duration_ticks / midi.ticks_per_beat
                    )

                    completed_notes.append(
                        {
                            "pitch": message.note,
                            "name": midi_note_to_name(message.note),
                            "start_tick": note_data["start_tick"],
                            "start_beat": (
                                note_data["start_tick"] / midi.ticks_per_beat
                            ),
                            "duration_beats": duration_beats,
                            "velocity": note_data["velocity"],
                        }
                    )

    return completed_notes

def align_notes(reference_notes, student_notes):
    reference_count = len(reference_notes)
    student_count = len(student_notes)

    # Each cell stores:
    # (number of edits, cumulative timing difference)
    matrix = [
        [None] * (student_count + 1)
        for _ in range(reference_count + 1)
    ]

    directions = [
        [None] * (student_count + 1)
        for _ in range(reference_count + 1)
    ]

    matrix[0][0] = (0, 0)

    # Empty student performance: all reference notes are missing.
    for reference_index in range(1, reference_count + 1):
        matrix[reference_index][0] = (
            reference_index,
            0,
        )
        directions[reference_index][0] = "missing"

    # Empty reference performance: all student notes are extra.
    for student_index in range(1, student_count + 1):
        matrix[0][student_index] = (
            student_index,
            0,
        )
        directions[0][student_index] = "extra"

    # Fill the matrix.
    for reference_index in range(1, reference_count + 1):
        for student_index in range(1, student_count + 1):
            reference = reference_notes[reference_index - 1]
            student = student_notes[student_index - 1]

            if reference["pitch"] == student["pitch"]:
                substitution_cost = 0
            else:
                substitution_cost = 1

            timing_difference = abs(
                student["start_beat"]
                - reference["start_beat"]
            )

            previous_diagonal = matrix[
                reference_index - 1
            ][student_index - 1]

            diagonal_cost = (
                previous_diagonal[0] + substitution_cost,
                previous_diagonal[1] + timing_difference,
            )

            previous_missing = matrix[
                reference_index - 1
            ][student_index]

            missing_cost = (
                previous_missing[0] + 1,
                previous_missing[1],
            )

            previous_extra = matrix[
                reference_index
            ][student_index - 1]

            extra_cost = (
                previous_extra[0] + 1,
                previous_extra[1],
            )

            lowest_cost = min(
                diagonal_cost,
                missing_cost,
                extra_cost,
            )

            matrix[reference_index][student_index] = (
                lowest_cost
            )

            if diagonal_cost == lowest_cost:
                directions[reference_index][student_index] = (
                    "diagonal"
                )
            elif missing_cost == lowest_cost:
                directions[reference_index][student_index] = (
                    "missing"
                )
            else:
                directions[reference_index][student_index] = (
                    "extra"
                )

    # Backtrack through the selected directions.
    aligned_notes = []

    reference_index = reference_count
    student_index = student_count

    while reference_index > 0 or student_index > 0:
        direction = directions[reference_index][student_index]

        if direction == "diagonal":
            aligned_notes.append(
                (
                    reference_notes[reference_index - 1],
                    student_notes[student_index - 1],
                )
            )

            reference_index -= 1
            student_index -= 1

        elif direction == "missing":
            aligned_notes.append(
                (
                    reference_notes[reference_index - 1],
                    None,
                )
            )

            reference_index -= 1

        elif direction == "extra":
            aligned_notes.append(
                (
                    None,
                    student_notes[student_index - 1],
                )
            )

            student_index -= 1

    aligned_notes.reverse()

    return aligned_notes


def compare_performances(reference_notes, student_notes):
    timing_tolerance = 0.125
    duration_tolerance = 0.15
    velocity_tolerance = 10

    correct_pitch_count = 0
    on_time_count = 0
    correct_duration_count = 0
    correct_velocity_count = 0
    note_results = []

    aligned_notes = align_notes(
        reference_notes,
        student_notes,
    )

    for position, (reference, student) in enumerate(
        aligned_notes,
        start=1,
    ):
        if reference is None:
            expected_name = "-"
            played_name = student["name"]
            pitch_result = "Extra"
            timing_result = "Extra note"
            duration_result = "Extra note"
            velocity_result = "Extra note"

        elif student is None:
            expected_name = reference["name"]
            played_name = "-"
            pitch_result = "Missing"
            timing_result = "Not played"
            duration_result = "Not played"
            velocity_result = "Not played"

        else:
            expected_name = reference["name"]
            played_name = student["name"]

            # Pitch
            pitch_is_correct = (
                reference["pitch"] == student["pitch"]
            )

            if pitch_is_correct:
                pitch_result = "Correct"
                correct_pitch_count += 1
            else:
                pitch_result = "Incorrect"

            # Timing
            timing_error = (
                student["start_beat"]
                - reference["start_beat"]
            )

            if abs(timing_error) <= timing_tolerance:
                timing_result = "On time"
                on_time_count += 1
            elif timing_error > 0:
                timing_result = (
                    f"{timing_error:.2f} beats late"
                )
            else:
                timing_result = (
                    f"{abs(timing_error):.2f} beats early"
                )

            # Duration
            duration_error = (
                student["duration_beats"]
                - reference["duration_beats"]
            )

            if abs(duration_error) <= duration_tolerance:
                duration_result = "Correct"
                correct_duration_count += 1
            elif duration_error > 0:
                duration_result = (
                    f"{duration_error:.2f} beats too long"
                )
            else:
                duration_result = (
                    f"{abs(duration_error):.2f} beats too short"
                )

            # Velocity
            velocity_error = (
                student["velocity"]
                - reference["velocity"]
            )

            if abs(velocity_error) <= velocity_tolerance:
                velocity_result = "Correct"
                correct_velocity_count += 1
            elif velocity_error > 0:
                velocity_result = (
                    f"{velocity_error} levels louder"
                )
            else:
                velocity_result = (
                    f"{abs(velocity_error)} levels softer"
                )

        note_results.append(
            {
                "position": position,
                "expected": expected_name,
                "played": played_name,
                "pitch_result": pitch_result,
                "timing_result": timing_result,
                "duration_result": duration_result,
                "velocity_result": velocity_result,
            }
        )

    pitch_total = max(
        len(reference_notes),
        len(student_notes),
        1,
    )

    expected_total = max(len(reference_notes), 1)

    pitch_score = (
        correct_pitch_count / pitch_total
    ) * 100

    timing_score = (
        on_time_count / expected_total
    ) * 100

    duration_score = (
        correct_duration_count / expected_total
    ) * 100

    velocity_score = (
        correct_velocity_count / expected_total
    ) * 100

    overall_score = (
        pitch_score * 0.50
        + timing_score * 0.25
        + duration_score * 0.15
        + velocity_score * 0.10
    )

    return {
        "note_results": note_results,
        "pitch_score": pitch_score,
        "timing_score": timing_score,
        "duration_score": duration_score,
        "velocity_score": velocity_score,
        "overall_score": overall_score,
    }