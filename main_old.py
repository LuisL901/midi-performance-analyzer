import mido
from analyzer import extract_notes, compare_performances




reference_notes = extract_notes(
    "samples/reference_scale.mid"
)

student_notes = extract_notes(
    "samples/student_expression_scale.mid"
)

report = compare_performances(
    reference_notes,
    student_notes,
)

for result in report["note_results"]:
    print(
        f"Note {result['position']}: "
        f"expected {result['expected']}, "
        f"played {result['played']}"
    )

    

    print(
        f"  Pitch: {result['pitch_result']} | "
        f"Timing: {result['timing_result']} | "
        f"Duration: {result['duration_result']} | "
        f"Velocity: {result['velocity_result']}"
    )

    print()

print()
print("Performance Summary")
print("-------------------")
print(f"Pitch score: {report['pitch_score']:.1f}%")
print(f"Timing score: {report['timing_score']:.1f}%")
print(f"Duration score: {report['duration_score']:.1f}%")
print(f"Velocity score: {report['velocity_score']:.1f}%")
print(f"Overall score: {report['overall_score']:.1f}%")