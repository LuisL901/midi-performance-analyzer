from analyzer import analyze
report = analyze(
    "samples/reference_scale.mid",
    "samples/student_extra_scale.mid",
)

note_results = report["note_results"]

for result in note_results:
    position = result["position"]
    status = result["status"]

    if status == "extra":
        print(position, "Extra note:", result["played"])
    elif status == "missing":
        print(position, "Missing note:", result["expected"])
    else:
        if result["pitch_correct"]:
            pitch_text = "Correct"
        else:
            pitch_text = "Incorrect"

        timing_error = result["timing_error_beats"]

        if result["timing_correct"]:
            timing_text = "On time"
        elif timing_error > 0:
            timing_text = f"{timing_error:.2f} beats late"
        else:
            timing_text = (
                f"{abs(timing_error):.2f} beats early"
            )
    
        duration_error = result["duration_error_beats"]

        if result["duration_correct"]:
            duration_text = "Correct"
        elif duration_error > 0:
            duration_text = (
                f"{duration_error:.2f} beats too long"
            )
        else:
            duration_text = (
                f"{abs(duration_error):.2f} beats too short"
            )

        velocity_error = result["velocity_error"]

        if result["velocity_correct"]:
            velocity_text = "Correct"
        elif velocity_error > 0:
            velocity_text = f"{velocity_error} too loud"
        else:
            velocity_text = (
                f"{abs(velocity_error)} too soft"
            )

        print(
            position,
            "Expected:", result["expected"],
            "Played:", result["played"],
            "| Pitch:", pitch_text,
            "| Timing:", timing_text,
            "| Duration:", duration_text,
            "| Velocity:", velocity_text,
        )

    

print("=========================")

print(f"Pitch score: {report['pitch_score']:.1f}%")
print(f"Timing score: {report['timing_score']:.1f}%")
print(f"Duration score: {report['duration_score']:.1f}%")
print(f"Velocity score: {report['velocity_score']:.1f}%")
print(f"Overall score: {report['overall_score']:.1f}%")