import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from graphql import graphql_sync

from app.collector import collect_metrics_forever
from app.database import init_db
from app.graphql_schema import schema
from app.websocket import router as websocket_router


BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    collector_task = asyncio.create_task(collect_metrics_forever())
    try:
        yield
    finally:
        collector_task.cancel()
        try:
            await collector_task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title="Monitor de Recursos",
    description="Projeto academico com GraphQL e WebSocket.",
    lifespan=lifespan,
)

app.include_router(websocket_router)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")


GRAPHQL_TEST_PAGE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GraphQL - Monitor de Recursos</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 24px; background: #f4f7fb; color: #172033; }
    textarea, pre { width: 100%; box-sizing: border-box; border: 1px solid #d8e0ec; border-radius: 8px; }
    textarea { min-height: 180px; padding: 12px; font-family: Consolas, monospace; }
    button { margin: 12px 0; padding: 10px 14px; border: 0; border-radius: 8px; background: #246bfe; color: white; cursor: pointer; }
    pre { min-height: 220px; padding: 12px; background: white; overflow: auto; }
  </style>
</head>
<body>
  <h1>GraphQL - Monitor de Recursos</h1>
  <textarea id="query">query {
  latestMetrics(limit: 10) {
    timestamp
    cpuPercent
    ramPercent
  }
}</textarea>
  <button onclick="runQuery()">Executar query</button>
  <pre id="result"></pre>
  <script>
    async function runQuery() {
      const query = document.getElementById("query").value;
      const response = await fetch("/graphql", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query })
      });
      const data = await response.json();
      document.getElementById("result").textContent = JSON.stringify(data, null, 2);
    }
  </script>
</body>
</html>
"""


@app.api_route("/graphql", methods=["GET", "POST"])
async def graphql_endpoint(request: Request):
    if request.method == "GET":
        query = request.query_params.get("query")
        if not query:
            return HTMLResponse(GRAPHQL_TEST_PAGE)
        variables = None
    else:
        body = await request.json()
        query = body.get("query")
        variables = body.get("variables")

    if not query:
        return JSONResponse({"errors": [{"message": "Campo 'query' e obrigatorio."}]}, status_code=400)

    result = graphql_sync(schema, query, variable_values=variables)
    response: dict = {}

    if result.errors:
        response["errors"] = [{"message": error.message} for error in result.errors]
    if result.data is not None:
        response["data"] = result.data

    return JSONResponse(response, status_code=400 if result.errors else 200)
