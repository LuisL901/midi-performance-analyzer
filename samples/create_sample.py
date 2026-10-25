from mido import Message, MidiFile, MidiTrack


def create_midi(
    file_path,
    notes,
    late_note_index=None,
    durations=None, 
    velocities=None,
    start_delays=None,
    ticks_per_beat=480,
):
    midi = MidiFile(ticks_per_beat=ticks_per_beat)
    track = MidiTrack()
    midi.tracks.append(track)

    if durations is None:
        durations = [480] * len(notes)

    if velocities is None:
        velocities = [80] * len(notes)

    if start_delays is None:
        start_delays = [0] * len(notes)

    for index, note in enumerate(notes):
        delay = start_delays[index]

        if index == late_note_index:
            delay += 120

        track.append(
            Message(
                "note_on",
                note=note,
                velocity=velocities[index],
                time=delay,
            )
        )

        track.append(
            Message(
                "note_off",
                note=note,
                velocity=0,
                time=durations[index],
            )
        )

    midi.save(file_path)
    print("Created:", file_path)


reference_notes = [60, 62, 64, 65, 67, 69, 71, 72]

student_notes = [60, 62, 64, 66, 67, 69, 71, 72]

student_missing_notes = [60, 62, 64, 67, 69, 71, 72]

student_extra_notes = [
    60,
    62,
    64,
    65,
    66,  # Extra F#4
    67,
    69,
    71,
    72,
]

#Expressions

student_expression_notes = [
    60,
    62,
    64,
    65,
    67,
    69,
    71,
    72,
]

student_expression_durations = [
    480,
    480,
    480,
    240,  # F4 is held for half a beat
    480,
    480,
    480,
    480,
]

student_expression_velocities = [
    80,
    80,
    80,
    50,  # F4 is played more softly
    80,
    80,
    80,
    80,
]

student_expression_delays = [
    0,
    0,
    0,
    0,
    240,  # Wait before G4 so it still starts on time
    0,
    0,
    0,
]

student_two_missing_notes = [
    60,  # C4
    62,  # D4
    # E4 is missing
    # F4 is missing
    67,  # G4
    69,  # A4
    71,  # B4
    72,  # C5
]

student_two_extra_notes = [
    60,  # C4
    61,  # Extra C#4
    63,  # Extra D#4
    62,  # D4
    64,  # E4
    65,  # F4
    67,  # G4
    69,  # A4
    71,  # B4
    72,  # C5
]

reference_repeated_notes = [
    60,  # First C4
    60,  # Second C4
    62,  # D4
]

student_repeated_missing_notes = [
    60,  # First C4
    62,  # D4
]

student_repeated_delays = [
    0,
    480,  # Wait through the missing second C4
]

student_high_resolution_notes = [
    60,
    62,
    64,
    65,
    67,
    69,
    71,
    72,
]

student_high_resolution_durations = [
    960,
    960,
    960,
    960,
    960,
    960,
    960,
    960,
]

create_midi(
    "samples/reference_scale.mid",
    reference_notes,
)

create_midi(
    "samples/student_scale.mid",
    student_notes,
    late_note_index=3,
)

create_midi(
    "samples/student_missing_scale.mid",
    student_missing_notes,
)

create_midi(
    "samples/student_extra_scale.mid",
    student_extra_notes,
)

create_midi(
    "samples/student_expression_scale.mid",
    student_expression_notes,
    durations=student_expression_durations,
    velocities=student_expression_velocities,
    start_delays=student_expression_delays,
)

create_midi(
    "samples/student_two_missing_scale.mid",
    student_two_missing_notes,
)

create_midi(
    "samples/student_two_extra_scale.mid",
    student_two_extra_notes,
)

create_midi(
    "samples/reference_repeated.mid",
    reference_repeated_notes,
)

create_midi(
    "samples/student_repeated_missing.mid",
    student_repeated_missing_notes,
    start_delays=student_repeated_delays,
)

create_midi(
    "samples/student_high_resolution_scale.mid",
    student_high_resolution_notes,
    durations=student_high_resolution_durations,
    ticks_per_beat=960,
)