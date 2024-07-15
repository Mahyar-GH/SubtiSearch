from fastapi import FastAPI, Response, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import re
import os
import json

app = FastAPI()

templates = Jinja2Templates(directory="templates")

Span = tuple[int, int]


@app.get("/{limit}")
async def root(request: Request, limit: int = -1):
    return templates.TemplateResponse(
            request=request, name="index.html", context={"limit": limit}
    )

    with open("./frontend/index.html") as f:
        s = f.read()
        return Response(s)

@app.get("/search/{limit}/")
async def search(request: Request, q: str, limit: int):
    return await search_limited(q, limit)


@app.get("/search/")
async def search_limited(q: str, limit: int = 100):
    if q == "":
        return "Empty Search."

    def typo(q: str):
        q = re.sub("a", "[Ääa]", q, flags=re.I)
        q = re.sub("u", "[Üüu]", q, flags=re.I)
        q = re.sub("o", "[Ööo]", q, flags=re.I)
        q = re.sub("ss", "(ß|ss)", q, flags=re.I)
        return q

    def deumlaut(t: str):
        t.replace("Ä", "a")
        t.replace("ä", "a")
        t.replace("Ü", "u")
        t.replace("ü", "u")
        t.replace("Ö", "o")
        t.replace("ö", "o")
        t.replace("ß", "ss")

    q = typo(q)

    subs_list = os.listdir("./subs")
    results: list[SubtitleItem] = []

    for subtitle_name in subs_list:
        with open(f"./subs/{subtitle_name}") as f:
            sub = json.load(f)

            for segment in sub:
                spans = [
                    *map(lambda x: x.span(), re.finditer(q, segment["text"], re.I))
                ]
                if spans:
                    src = f'{os.path.basename(subtitle_name).removesuffix(".json")} / {segment["span"]}'
                    results.append(
                        SubtitleItem(src, segment["text"], spans)
                    )

    return Response("<hr>".join(map(lambda x: x.to_html(), results[:limit])) or "No Results.")


class SubtitleItem:
    src: str
    text: str
    spans: list[Span]

    def __init__(self, src: str, text: str, spans: list[Span]):
        self.src = src
        self.text = text
        self.spans = spans

    def to_html(self):
        html = [f'<div class="src">{self.src}</div>']

        curspan = self.spans[0]
        html.append(self.text[: curspan[0]])
        html.append(f"<span>{self.text[curspan[0]: curspan[1]]}</span>")

        for i in range(1, len(self.spans)):
            prevspan = self.spans[i - 1]
            curspan = self.spans[i]
            html.append(self.text[prevspan[1] : curspan[0]])
            html.append(f"<span>{self.text[curspan[0]: curspan[1]]}</span>")

        html.append(self.text[curspan[1] :])

        # # html.append()

        # for i, span in enumerate(self.spans):
        #     html.append(
        #         self.text[: span[0]]
        #         + f"<span>{self.text[span[0]: span[1]]}</span>"
        #         + self.text[span[1] : self.spans[i + 1][0]]
        #     )
        return "".join(html)
