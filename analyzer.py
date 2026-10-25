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

TIMING_TOLERANCE_BEATS = 0.125
DURATION_TOLERANCE_BEATS = 0.125
VELOCITY_TOLERANCE = 10

def midi_note_to_name(note_number):
    note_name = NOTE_NAMES[note_number % 12]
    octave = (note_number // 12) - 1

    return f"{note_name}{octave}"

def finish_note(released_pitch, active_notes, completed_notes,end_tick,ticks_per_beat):
    if released_pitch not in active_notes:
        return
    note_data = active_notes.pop(released_pitch)
    duration = end_tick - note_data["tick"]

    completed_notes.append({
        "pitch" : released_pitch,
        "name" : midi_note_to_name(released_pitch),
        "start_tick" : note_data["tick"],
        "duration": duration,
        "start_beat": note_data["tick"]/ticks_per_beat,
        "duration_beats": duration/ticks_per_beat,
        "velocity": note_data["velocity"]
    })

def extract_notes(file_source):
    if hasattr(file_source, "read"):
        midi = mido.MidiFile(file=file_source)
    else:
        midi = mido.MidiFile(file_source)    
    active_notes = {}
    completed_notes = []
    for track in midi.tracks:
        current_tick = 0
        for message in track:
            current_tick += message.time
            if message.type == "note_on" and message.velocity > 0:
                active_notes[message.note] = {
                    "tick" : current_tick,
                    "velocity" : message.velocity,
                }
            elif message.type == "note_off" or (message.type == "note_on" and message.velocity == 0):
                finish_note(message.note, active_notes, completed_notes, current_tick, midi.ticks_per_beat)

    completed_notes.sort(key=lambda note: note["start_tick"])
    return completed_notes

def create_cost_matrix(reference_notes, student_notes):
    rows = len(reference_notes) + 1
    columns = len(student_notes) + 1

    cost_matrix = [
        [(0,0) for column in range(columns)]
        for row in range(rows)
    ]

    for row in range(rows):
        cost_matrix[row][0] = (row,0)

    for column in range(columns):
        cost_matrix[0][column] = (column,0)

    for row in range(1,rows):
        for column in range(1,columns):
            reference = reference_notes[row - 1]
            student = student_notes[column - 1]

            pitch_penalty = (
                0 if reference["pitch"] == student["pitch"] 
                else 1
            )
            timing_penalty = abs(
                student["start_beat"] - reference["start_beat"]
            )

            previous_pair = cost_matrix[row - 1][column - 1]
            pair_cost = (
                previous_pair[0] + pitch_penalty,
                previous_pair[1] + timing_penalty
            )

            previous_extra = cost_matrix[row][column - 1]
            extra = (
                previous_extra[0] + 1,
                previous_extra[1]
            )

            previous_missing = cost_matrix[row - 1][column]
            missing = (
                previous_missing[0] + 1,
                previous_missing[1]
            )
            cost_matrix[row][column] = min(pair_cost,extra,missing)

    return cost_matrix

def backtrack_alignment(
        cost_matrix,
        reference_notes,
        student_notes
):
    row = len(reference_notes)
    column = len(student_notes)

    aligned_notes = []

    while(row > 0 or column > 0):
        if row > 0 and column > 0:
            pitch_penalty = (
                0 
                if reference_notes[row - 1]["pitch"] == student_notes[column - 1]["pitch"] 
                else 1
            )
            timing_penalty = abs(
                student_notes[column - 1]["start_beat"]
                - reference_notes[row - 1]["start_beat"]
            )

            previous_pair = cost_matrix[row - 1][column - 1]

            pair_cost = (
                previous_pair[0] + pitch_penalty,
                previous_pair[1] + timing_penalty
            )

            if pair_cost == cost_matrix[row][column]:
                aligned_notes.append(
                    {
                        "reference" : reference_notes[row - 1],
                        "student": student_notes[column - 1]
                    }
                )
                row -= 1
                column -= 1
                continue

        if row > 0:
            previous_missing = cost_matrix[row - 1][column]

            missing_cost = (
                previous_missing[0] + 1,
                previous_missing[1 ]
            )

            if missing_cost == cost_matrix[row][column]:
                aligned_notes.append(
                    {
                        "reference": reference_notes[row -1],
                        "student": None
                    }
                )
                row -= 1
                continue

        if column > 0:
            previous_extra = cost_matrix[row][column - 1]

            extra_cost = (
                previous_extra[0] + 1,
                previous_extra[1]
            )
            if extra_cost == cost_matrix[row][column]:
                aligned_notes.append(
                    {
                        "reference": None,
                        "student": student_notes[column - 1]
                    }
                )
                column -= 1
                continue
    aligned_notes.reverse()
    return aligned_notes

def count_correct_pitches(aligned_notes):
    correct_count = 0
    for pair in aligned_notes:
        if pair["student"] is not None and pair["reference"] is not None:
            if pair["student"]["pitch"] == pair["reference"]["pitch"]:
                correct_count += 1
    return correct_count

def count_on_time(aligned_notes):
    on_time_count = 0 

    for pair in aligned_notes:
        student = pair["student"]
        reference = pair["reference"]
        if student is not None and reference is not None:
            timing_error = student["start_beat"] - reference["start_beat"]
            if abs(timing_error) <= TIMING_TOLERANCE_BEATS:
                on_time_count += 1

    return on_time_count

def count_correct_duration(aligned_notes):
    correct_count_duration = 0

    for pair in aligned_notes:
        student = pair["student"]
        reference = pair["reference"]
        if student is not None and reference is not None:
            duration_error = student["duration_beats"] - reference["duration_beats"]
            if abs(duration_error) <= DURATION_TOLERANCE_BEATS:
                correct_count_duration += 1

    return correct_count_duration

def count_correct_velocity(aligned_notes):
    correct_count_velocity = 0
    velocity_tolerance = 10
    for pair in aligned_notes:
        if pair["student"] is not None and pair["reference"] is not None:
            velocity_error = pair["student"]["velocity"] - pair["reference"]["velocity"]
            if abs(velocity_error) <= VELOCITY_TOLERANCE:
                correct_count_velocity += 1
    return correct_count_velocity

def calculate_score(count_correct, aligned_notes):
    if len(aligned_notes) == 0:
        return 0.0

    return count_correct / len(aligned_notes) * 100

def calculate_overall_score(pitch_score, timing_score, duration_score, velocity_score):
    pitch_weight = .4
    timing_weight = .35
    duration_weight = .15
    velocity_weight = .1

    return velocity_score * velocity_weight + timing_score * timing_weight + duration_score * duration_weight + pitch_score * pitch_weight

def analyze(reference_path, student_path):
    reference_notes = extract_notes(reference_path)
    student_notes = extract_notes(student_path)
    if len(reference_notes) == 0:
        raise ValueError(
            "Reference MIDI file contains no notes."
        )

    if len(student_notes) == 0:
        raise ValueError(
            "Student MIDI file contains no notes."
        )

    cost_matrix = create_cost_matrix(reference_notes, student_notes);
    aligned_notes = backtrack_alignment(cost_matrix, reference_notes, student_notes)
    note_results = build_note_results(aligned_notes)

    correct_pitch_count = count_correct_pitches(aligned_notes)
    on_time_count = count_on_time(aligned_notes)
    correct_duration_count = count_correct_duration(aligned_notes)
    correct_velocity_count = count_correct_velocity(aligned_notes)

    pitch_score = calculate_score(correct_pitch_count, aligned_notes)
    timing_score = calculate_score(on_time_count, aligned_notes)
    duration_score = calculate_score(correct_duration_count, aligned_notes)
    velocity_score = calculate_score(correct_velocity_count,aligned_notes)

    overall_score = calculate_overall_score(
        pitch_score,
        timing_score,
        duration_score,
        velocity_score,
    )   

    return {
    "aligned_notes": aligned_notes,
    "pitch_score": pitch_score,
    "timing_score": timing_score,
    "duration_score": duration_score,
    "velocity_score": velocity_score,
    "overall_score": overall_score,
    "note_results": note_results
    }

def build_note_results(aligned_notes):
    note_results = []

    for position, pair in enumerate(aligned_notes, start=1):
        reference = pair["reference"]
        student = pair["student"]

        if reference is None:
            note_results.append(
                {
                    "position": position,
                    "status": "extra",
                    "expected": None,
                    "played": student["name"],
                }
            )

        elif student is None:
            note_results.append(
                {
                    "position": position,
                    "status": "missing",
                    "expected": reference["name"],
                    "played": None,
                }
            )

        else:
            pitch_correct = (
                reference["pitch"] == student["pitch"]
            )

            timing_error_beats = (
                student["start_beat"]
                - reference["start_beat"]
            )

            timing_correct = (
                abs(timing_error_beats)
                <= TIMING_TOLERANCE_BEATS
            )
            duration_error_beats = (
                student["duration_beats"]
                - reference["duration_beats"]
            )

            duration_correct = (
                abs(duration_error_beats)
                <= DURATION_TOLERANCE_BEATS
            )

            velocity_error = (
                student["velocity"]
                - reference["velocity"]
            )

            velocity_correct = (
                abs(velocity_error)
                <= VELOCITY_TOLERANCE
            )

            note_results.append(
                {
                    "position": position,
                    "status": "paired",
                    "expected": reference["name"],
                    "played": student["name"],
                    "pitch_correct": pitch_correct,
                    "timing_error_beats": timing_error_beats,
                    "timing_correct": timing_correct,
                    "duration_error_beats": duration_error_beats,
                    "duration_correct": duration_correct,
                    "velocity_error": velocity_error,
                    "velocity_correct": velocity_correct
                }
            )

    return note_results