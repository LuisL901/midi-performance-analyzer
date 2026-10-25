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


def finish_note(released_pitch, active_notes, completed_notes,end_tick):
    note_data = active_notes.pop(released_pitch)
    duration = end_tick - note_data["tick"]
    completed_notes.append({
        "pitch" : released_pitch,
        "name" : midi_note_to_name(released_pitch),
        "start_tick" : note_data["tick"],
        "duration": duration,
        "velocity": note_data["velocity"]
    })

def extract_notes(file_path):
    midi = mido.MidiFile(file_path)
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
                finish_note(message.note, active_notes, completed_notes, current_tick)

    completed_notes.sort(key=lambda note: note["start_tick"])
    return completed_notes

def count_correct_pitches(aligned_notes):
    correct_count = 0
    for pair in aligned_notes:
        if pair["student"] is not None and pair["reference"] is not None:
            if pair["student"]["pitch"] == pair["reference"]["pitch"]:
                correct_count += 1
    return correct_count

def calculate_score(count_correct, aligned_notes):
    return count_correct/len(aligned_notes) * 100

def count_on_time(aligned_notes):
    on_time_count = 0 
    timing_tolerance = 60

    for pair in aligned_notes:
        if pair["student"] is not None and pair["reference"] is not None:
            timing_error = pair["student"]["start_tick"] - pair["reference"]["start_tick"]
            if abs(timing_error) <= timing_tolerance:
                on_time_count += 1

    return on_time_count

def count_correct_duration(aligned_notes):
    correct_count_duration = 0
    duration_tolerance = 60
    for pair in aligned_notes:
        if pair["student"] is not None and pair["reference"] is not None:
            duration_error = pair["student"]["duration"] - pair["reference"]["duration"]
            if duration_tolerance >= abs(duration_error):
                correct_count_duration += 1

    return correct_count_duration

def count_correct_velocity(aligned_notes):
    correct_count_velocity = 0
    velocity_tolerance = 10
    for pair in aligned_notes:
        if pair["student"] is not None and pair["reference"] is not None:
            velocity_error = pair["student"]["velocity"] - pair["reference"]["velocity"]
            if velocity_tolerance >= abs(velocity_error):
                correct_count_velocity += 1
    return correct_count_velocity

def calculate_overall_score(pitch_score, timing_score, duration_score, velocity_score):
    pitch_weight = .4
    timing_weight = .35
    duration_weight = .15
    velocity_weight = .1

    return velocity_score * velocity_weight + timing_score * timing_weight + duration_score * duration_weight + pitch_score * pitch_weight

def create_cost_matrix(reference_notes, student_notes):
    rows = len(reference_notes) + 1
    columns = len(student_notes) + 1

    cost_matrix = [
        [0 for column in range(columns)]
        for row in range(rows)
    ]

    for row in range(rows):
        cost_matrix[row][0] = row

    for column in range(columns):
        cost_matrix[0][column] = column

    for row in range(1,rows):
        for column in range(1,columns):
            pitch_penalty = (
                0 if reference_notes[row - 1]["pitch"] == student_notes[column - 1]["pitch"] 
                else 1
            )
            pair_cost = cost_matrix[row - 1][column - 1] + pitch_penalty
            extra = cost_matrix[row][column - 1] + 1
            missing = cost_matrix[row - 1][column] + 1
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
                else 1)

            if cost_matrix[row - 1][column - 1] + pitch_penalty == cost_matrix[row][column]:
                aligned_notes.append(
                    {
                        "reference" : reference_notes[row - 1],
                        "student": student_notes[column - 1]
                    }
                )
                row -= 1
                column -= 1
                continue

        if (row > 0 and cost_matrix[row - 1][column] + 1 == cost_matrix[row][column]):
            aligned_notes.append(
                {
                    "reference": reference_notes[row -1],
                    "student": None
                }
            )
            row -= 1
            continue

        if (column > 0 and cost_matrix[row][column - 1] + 1 == cost_matrix[row][column]):
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



reference_notes = extract_notes("samples/reference_scale.mid")
student_notes = extract_notes(
    "samples/student_extra_scale.mid"
)
cost_matrix = create_cost_matrix(
    reference_notes,
    student_notes,
)

aligned_notes = backtrack_alignment(
    cost_matrix,
    reference_notes,
    student_notes,
)

for position, pair in enumerate(aligned_notes, start=1):
    reference = pair["reference"]
    student = pair["student"]

    if reference is None:
        print(position, "Extra note:", student["name"])

    elif student is None:
        print(position, "Missing note:", reference["name"])

    else:
        if reference["pitch"] == student["pitch"]:
            pitch_result = "Correct"
        else:
            pitch_result = "Incorrect"

        timing_error = (
            student["start_tick"]
            - reference["start_tick"]
        )

        if abs(timing_error) <= 60:
            timing_result = "On time"
        elif timing_error > 0:
            timing_result = f"{timing_error} ticks late"
        else:
            timing_result = f"{abs(timing_error)} ticks early"

        duration_error = (
            student["duration"]
            - reference["duration"]
        )
        if abs(duration_error) <= 60:
            duration_result = "Correct"
        elif duration_error > 0:
            duration_result = f"{duration_error} ticks too long"
        else:
            duration_result = f"{abs(duration_error)} ticks too short"

        velocity_error = (
            student["velocity"]
            - reference["velocity"]
        )
        if abs(velocity_error) <= 10:
            velocity_result = "Correct"
        elif velocity_error > 0:
            velocity_result = f"{velocity_error} too loud"
        else:
            velocity_result = f"{abs(velocity_error)} too soft"



        print(
            position,
            "Expected:", reference["name"],
            "Played:", student["name"],
            "| Pitch:", pitch_result,   
            "| Timing:", timing_result,
            "| Duration:", duration_result,
            "| Velocity:", velocity_result
        )

print("=========================")

correct_pitch_count = count_correct_pitches(aligned_notes)
on_time_count = count_on_time(aligned_notes)


pitch_score = calculate_score(correct_pitch_count, aligned_notes)
timing_score = calculate_score(on_time_count, aligned_notes)

print(f"Pitch score: {pitch_score:.1f}%")
print(f"Timing score: {timing_score:.1f}%")

correct_duration_count = count_correct_duration(aligned_notes)
duration_score = calculate_score(correct_duration_count, aligned_notes)
print(f"Duration score: {duration_score:.1f}%")

correct_velocity_count = count_correct_velocity(aligned_notes)
velocity_score = calculate_score(correct_velocity_count,aligned_notes)
print(f"Velocity score: {velocity_score:.1f}%")

overall_score = calculate_overall_score(
    pitch_score,
    timing_score,
    duration_score,
    velocity_score,
)

print(f"Overall score: {overall_score:.1f}%")


