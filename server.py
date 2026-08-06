from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.generator import Generator

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

        lexer = Lexer(source)
        tokens = lexer.tokenize()

        parser = Parser(tokens)
        ast = parser.parse()

        generator = Generator(ast)
        javascript = generator.generate()

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
