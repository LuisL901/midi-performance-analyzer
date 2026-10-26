# MIDI Performance Analyzer

A Python application that compares a student's MIDI performance against a reference MIDI file. It aligns the performances using dynamic programming and evaluates pitch, timing, note duration, and velocity.

## How It Works

The application accepts two MIDI files: a reference performance and a student performance. As each file is read, `note_on` messages are stored in an active-notes dictionary. When a matching note_off message—or a note_on message with velocity zero—is encountered, the note is removed from the dictionary and added to a list of completed-note dictionaries. Each completed note contains its pitch, name, velocity, start time, and duration.

The application converts start times and durations from MIDI ticks into beats. This allows performances with different tick resolutions to be compared consistently.

The program then uses dynamic programming to create a cost matrix and align the reference notes with the student notes. The matrix minimizes musical mistakes first and uses timing differences to resolve alignments with equal mistake counts. This allows the analyzer to identify matching notes, incorrect pitches, missing notes, and extra notes.

Finally, the program backtracks through the cost matrix to reconstruct the selected alignment. It evaluates the pitch, timing, duration, and velocity of each aligned pair, calculates the individual category scores and weighted overall score, and creates a detailed performance report. The API returns this report as JSON.

## Features

- Compare a student's MIDI performance against a reference MIDI file.
- Detect incorrect pitches, missing notes, and extra notes.
- Evaluate note timing, velocity, and duration.
- Compare MIDI files with different tick resolutions using beat-based measurements.
- Generate category scores and a weighted overall performance score.
- Provide detailed feedback for individual notes.
- Run comparisons through the terminal or upload files through a FastAPI endpoint.
- Reject unsupported filenames, unreadable MIDI data, and MIDI files containing no notes.

## Scoring

Each category score is calculated as:

category score = correct entries / total aligned entries × 100

Missing and extra notes remain in the alignment but receive no credit in any category.

### Pitch

A pitch is correct when the student and reference notes have the same MIDI pitch number. For example, C4 matches C4, but C3 does not because it is an octave lower.

### Timing

Timing is correct when the student's note starts within 0.125 beats of the reference note's start time. Notes outside this tolerance are reported as early or late.

### Duration

Duration is correct when the student's note duration differs from the reference by no more than 0.125 beats. For example, if the reference lasts 2 beats, a student duration from 1.875 to 2.125 beats is accepted.

### Velocity

Velocity is correct when the student's MIDI velocity differs from the reference by no more than 10 units. MIDI velocity represents the strength of the note attack and is used here to compare playing dynamics.

### Overall Score

The overall score combines the four category scores using these weights:

- Pitch: 40%
- Timing: 35%
- Duration: 15%
- Velocity: 10%

overall score = pitch × 0.40 + timing × 0.35 + duration × 0.15 + velocity × 0.10

## Installation

The following commands use Windows PowerShell.

Requires Python and pip. The project was developed using Python 3.13.

Download or clone the repository, then open a terminal in the project folder.

Create a virtual environment:

```powershell
py -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Usage

Run all commands from the project root.

### Terminal

Run the included sample comparison:

```powershell
python main.py
```

To compare different files, change the reference and student paths passed to `analyze()` in `main.py`.

The terminal displays individual note feedback, category scores, and the overall score.

### API

Start the API server:

```powershell
python -m uvicorn api:app --reload
```

Open http://127.0.0.1:8000/docs in your browser.

1. Expand `POST /analyze`.
2. Click **Try it out**.
3. Select a reference MIDI file and a student MIDI file.
4. Click **Execute**.

The API returns the performance report as JSON. Stop the server with `Ctrl+C`.

## Testing

Run the automated tests from the project root:

```powershell
python -m pytest -q
```

The suite includes 14 tests covering:

- Perfect performances and incorrect pitches
- Missing and extra notes
- Repeated-pitch alignment
- Different MIDI tick resolutions
- Empty alignment scoring and unmatched note-off messages
- API responses for valid uploads, invalid extensions, unreadable MIDI data, and empty MIDI files

## Project Structure

- `analyzer.py`: Extracts MIDI notes, aligns performances, and calculates scores and individual note feedback.
- `main.py`: Runs a sample comparison and prints the report in the terminal.
- `api.py`: Provides the FastAPI endpoints for uploading and comparing MIDI files.
- `samples/`: Contains example MIDI files and the sample-generation script.
- `tests/test_analyzer.py`: Tests note alignment and scoring behavior.
- `tests/test_api.py`: Tests API requests, upload validation, and responses.
- `requirements.txt`: Lists the Python dependencies.

