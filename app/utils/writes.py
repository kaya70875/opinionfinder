import csv
import json
from io import StringIO
from app.types.youtube import FetchAndMetaResponse

def write_as_text(channel_data: list[FetchAndMetaResponse], allowed_metadata: list, timing: bool) -> StringIO:
    output = StringIO()
    for data in channel_data:

        output.write(f"Transcript for {data.video_id}:\n")

        for metadata in allowed_metadata:
            output.write(f'{metadata} --> {getattr(data.snippet, metadata)} \n')
        for entry in data.transcript:
            output.write(f"{entry['start']} --> {entry['start'] + entry['duration']}\n") if timing else None
            output.write(f"{entry['text']}\n")
        output.write("\n")
    output.seek(0)
    return output

def write_as_csv(channel_data: list[FetchAndMetaResponse], allowed_metadata: list, timing: bool) -> StringIO:
    
    output = StringIO()

    t = ['start', 'duration']

    fieldnames = ['index', 'video_id', *allowed_metadata, 'text']
    fieldnames += t if timing else []
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    i = 0

    for data in channel_data:
        for entry in data.transcript:
            row = {
                'index': i,
                'video_id': data.video_id,
                **{field: getattr(data.snippet, field) for field in allowed_metadata},
                **({"start": entry["start"], "duration": entry["duration"]} if timing else {}),
                'text': entry['text']
            }
            writer.writerow(row)
            i += 1
    output.seek(0)
    return output


def write_as_json(channel_data: list[FetchAndMetaResponse], allowed_metadata: list, timing: bool) -> StringIO:
    output = StringIO()
    export_data = []

    for data in channel_data:
        video_data = {
            "video_id": data.video_id,
            **{field: getattr(data.snippet, field) for field in allowed_metadata},
            "transcript": [
                {   
                    **({"start": entry["start"], "duration": entry["duration"]} if timing else {}),
                    "text": entry["text"]
                }
                for entry in data.transcript
            ]
        }
        export_data.append(video_data)

    json.dump(export_data, output, indent=2, ensure_ascii=False)
    output.seek(0)
    return output