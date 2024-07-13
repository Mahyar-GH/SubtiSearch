from fastapi import FastAPI, Response
import re
import os
import json

app = FastAPI()

Span = tuple[int, int]


@app.get("/")
async def root():
    with open("./frontend/index.html") as f:
        s = f.read()
        return Response(s)


@app.get("/search/")
async def search(q: str):
    subs_list = os.listdir("./subs/json")
    results: list[SubtitleItem] = []

    for sub in subs_list:
        with open(f"./subs/json/{sub}") as f:
            sub = json.load(f)
            for segment in sub["segments"]:
                spans = [*map(lambda x: x.span(), re.finditer(q, segment["text"]))]
                if spans:
                    results.append(
                        SubtitleItem(segment["start"], segment["text"], spans)
                    )

    return '<hr>'.join(map(lambda x: x.to_html(), results))
    # return Response('<br>'.join(subs_list))
    # return Response(f'You searched for "{q}"')


class SubtitleItem:
    start: float
    text: str
    spans: list[Span]

    def __init__(self, start: float, text: str, spans: list[Span]):
        self.start = start
        self.text = text
        self.spans = spans

    def to_html(self):
        html = []
        for span in self.spans:
            html.append(
                self.text[: span[0]]
                + f"<span>{self.text[span[0]: span[1]]}</span>"
                + self.text[span[1] :]
            )
        return '<br>'.join(html)

