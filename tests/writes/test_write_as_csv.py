from app.types.youtube import FetchAndMetaResponse, Snippet
from app.utils.writes import write_as_csv
import csv

def parse_csv_output(output):
    output.seek(0)
    return list(csv.reader(output, 'excel'))

def test_write_as_csv_basic():
    metadata = ['title', 'description']
    test_response = FetchAndMetaResponse(
        video_id="testid123",
        transcript=[
            {"start": 0, "duration": 0, "text": "testing text"},
            {"start": 1, "duration": 1.5, "text": "second text"}
        ],
        snippet=Snippet(
            title="Test",
            description="desc",
            publishedAt="datetime",
            channelId="123"
        )
    )
    output = write_as_csv([test_response], metadata)
    rows = parse_csv_output(output)
    print(rows)
    assert rows[0] == ['index', 'video_id', 'start', 'duration', 'title', 'description', 'text']
    assert rows[1][1] == "testid123"
    assert rows[1][4] == "Test"
    assert rows[1][5] == "desc"
    assert rows[1][6] == "testing text"
    assert rows[2][6] == "second text"