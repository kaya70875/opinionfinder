import csv
import json
from io import StringIO

def write_as_text(all_transcripts: dict) -> StringIO:
    output = StringIO()
    for video_id, transcript in all_transcripts.items():
        output.write(f"Transcript for {video_id}:\n")
        for entry in transcript:
            output.write(f"{entry['start']} --> {entry['start'] + entry['duration']}\n")
            output.write(f"{entry['text']}\n")
        output.write("\n")
    output.seek(0)
    return output

def write_as_csv(all_transcripts: dict) -> StringIO:
    output = StringIO()
    fieldnames = ['video_id', 'start', 'duration', 'text']
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for video_id, transcript in all_transcripts.items():
        for entry in transcript:
            writer.writerow({
                'video_id': video_id,
                'start': entry['start'],
                'duration': entry['duration'],
                'text': entry['text']
            })
    output.seek(0)
    return output

def write_as_json(all_transcripts: dict) -> StringIO:
    output = StringIO()
    json.dump(all_transcripts, output, indent=2)
    output.seek(0)
    return output