import csv
import json
from io import StringIO

def write_as_text(channel_data: list, allowed_metadata: list) -> StringIO:
    output = StringIO()
    for data in channel_data:

        output.write(f"Transcript for {data['video_id']}:\n")

        for metadata in allowed_metadata:
            output.write(f'{metadata} --> {data["snippet"][metadata]} \n')
        for entry in data['transcript']:
            output.write(f"{entry['start']} --> {entry['start'] + entry['duration']}\n")
            output.write(f"{entry['text']}\n")
        output.write("\n")
    output.seek(0)
    return output

def write_as_csv(channel_data: list, allowed_metadata: list) -> StringIO:
    
    output = StringIO()
    fieldnames = ['index', 'video_id', 'start', 'duration', *allowed_metadata, 'text']
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    i = 0

    for data in channel_data:
        for entry in data['transcript']:
            row = {
                'index': i,
                'video_id': data['video_id'],
                **{field: data['snippet'].get(field, '') for field in allowed_metadata},
                'start': entry['start'],
                'duration': entry['duration'],
                'text': entry['text']
            }
            writer.writerow(row)
            i += 1
    output.seek(0)
    return output


def write_as_json(channel_data: list, allowed_metadata: list) -> StringIO:
    output = StringIO()
    export_data = []

    for data in channel_data:
        video_data = {
            "video_id": data['video_id'],
            **{field: data['snippet'][field] for field in allowed_metadata},
            "transcript": [
                {
                    "start": entry["start"],
                    "duration": entry["duration"],
                    "text": entry["text"]
                }
                for entry in data['transcript']
            ]
        }
        export_data.append(video_data)

    json.dump(export_data, output, indent=2, ensure_ascii=False)
    output.seek(0)
    return output