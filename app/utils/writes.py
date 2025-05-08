import csv
import json
from io import StringIO
from app.types.youtube import Snippet

def write_as_text(all_transcripts: dict, snippet: list[Snippet]) -> StringIO:
    output = StringIO()
    for idx, (video_id, transcript) in enumerate(all_transcripts.items()):
        output.write(f"Transcript for {video_id}:\n")
        output.write(f'Title --> {snippet[idx].title} \n')
        output.write(f'Description --> {snippet[idx].description} \n')
        output.write(f'Published At --> {snippet[idx].publishedAt} \n')
        for entry in transcript:
            output.write(f"{entry['start']} --> {entry['start'] + entry['duration']}\n")
            output.write(f"{entry['text']}\n")
        output.write("\n")
    output.seek(0)
    return output

def write_as_csv(all_transcripts: dict, snippet: list[Snippet]) -> StringIO:
    output = StringIO()
    fieldnames = ['index', 'video_id', 'start', 'duration', 'title', 'description', 'publishedAt', 'text']
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for i, (video_id, transcript) in enumerate(all_transcripts.items()):
        for idx, (entry) in enumerate(transcript):
            writer.writerow({
                'index': idx,
                'video_id': video_id,
                'start': entry['start'],
                'duration': entry['duration'],
                'title': snippet[i].title,
                'description': snippet[i].description,
                'publishedAt': snippet[i].publishedAt,
                'text': entry['text']
            })
    output.seek(0)
    return output

def write_as_json(all_transcripts: dict, snippet: list[Snippet]) -> StringIO:
    output = StringIO()
    export_data = []

    for idx, (video_id, transcript) in enumerate(all_transcripts.items()):
        video_data = {
            "video_id": video_id,
            "title": snippet[idx].title,
            "description": snippet[idx].description,
            'publishedAt': snippet[idx].publishedAt,
            "transcript": [
                {
                    "start": entry["start"],
                    "duration": entry["duration"],
                    "text": entry["text"]
                }
                for entry in transcript
            ]
        }
        export_data.append(video_data)

    json.dump(export_data, output, indent=2, ensure_ascii=False)
    output.seek(0)
    return output