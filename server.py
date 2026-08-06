from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# These modules do not exist yet.
# We will build them next.
from compiler.lexer import tokenize
from compiler.parser import parse
from compiler.generator import generate

app = FastAPI(title="Intent Language Compiler")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def home():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/compile")
async def compile_code(request: Request):

    body = await request.json()

    source = body.get("code", "")

    try:

        tokens = tokenize(source)

        ast = parse(tokens)

        javascript = generate(ast)

        return JSONResponse({
            "success": True,
            "javascript": javascript
        })

    except Exception as e:

        return JSONResponse({
            "success": False,
            "error": str(e)
        })


if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=6040,
        reload=True
    )
