# Monitor de Recursos com GraphQL e WebSocket

Projeto academico simples para demonstrar dois paradigmas de APIs usando Python, FastAPI, GraphQL e WebSocket.

O sistema coleta periodicamente o uso de CPU e memoria RAM da maquina, salva o historico em SQLite e disponibiliza os dados de duas formas:

- GraphQL: consultas ao historico armazenado.
- WebSocket: envio automatico das metricas em tempo real para o navegador.

## Tecnologias utilizadas

- Python 3
- FastAPI
- GraphQL com graphql-core
- WebSocket nativo do FastAPI
- psutil
- SQLite
- SQLAlchemy
- HTML, CSS e JavaScript puro

## Arquitetura

Fluxo de coleta e persistencia:

```text
psutil -> coletor em segundo plano -> FastAPI -> SQLite
```

Fluxo de consulta historica:

```text
SQLite -> GraphQL -> cliente
```

Fluxo em tempo real:

```text
coleta -> WebSocket -> navegador
```

## Como executar no Windows

Crie o ambiente virtual:

```powershell
python -m venv .venv
```

Ative o ambiente virtual:

```powershell
.venv\Scripts\activate
```

Instale as dependencias:

```powershell
pip install -r requirements.txt
```

Inicie o servidor:

```powershell
uvicorn app.main:app --reload
```

Para alterar o intervalo de coleta, defina a variavel de ambiente antes de iniciar:

```powershell
$env:COLLECTION_INTERVAL = "2"
uvicorn app.main:app --reload
```

## URLs

- Aplicacao web: http://127.0.0.1:8000/
- GraphQL: http://127.0.0.1:8000/graphql
- WebSocket: ws://127.0.0.1:8000/ws/metrics

## Queries GraphQL

Ultimas metricas:

```graphql
query {
  latestMetrics(limit: 10) {
    timestamp
    cpuPercent
    ramPercent
  }
}
```

Media dos ultimos 10 minutos:

```graphql
query {
  averageMetrics(minutes: 10) {
    averageCpu
    averageRam
  }
}
```

Maior uso de CPU e RAM nos ultimos 10 minutos:

```graphql
query {
  peakMetrics(minutes: 10) {
    peakCpu
    peakCpuTimestamp
    peakRam
    peakRamTimestamp
  }
}
```

Consulta por intervalo de datas:

```graphql
query {
  metricsBetween(
    start: "2026-09-15T16:30:00",
    end: "2026-09-15T16:40:00"
  ) {
    timestamp
    cpuPercent
    ramPercent
    ramUsed
    ramTotal
  }
}
```

Quantidade de registros:

```graphql
query {
  metricsCount
}
```

## Como o WebSocket funciona

O endpoint `ws://127.0.0.1:8000/ws/metrics` mantem uma conexao aberta entre navegador e servidor. A cada coleta, o servidor salva a metrica no SQLite e envia automaticamente a mesma informacao para todos os clientes conectados.

Exemplo de mensagem:

```json
{
  "timestamp": "2026-09-15T16:30:00",
  "cpu_percent": 32.5,
  "ram_percent": 61.2,
  "ram_used": 10234567890,
  "ram_total": 17179869184
}
```

Se o navegador desconectar, o servidor remove aquela conexao e continua funcionando normalmente.

## Estrutura de pastas

```text
.
|-- app/
|   |-- main.py
|   |-- database.py
|   |-- models.py
|   |-- collector.py
|   |-- websocket.py
|   |-- graphql_schema.py
|   `-- services/
|       |-- __init__.py
|       `-- metrics_service.py
|-- static/
|   |-- index.html
|   |-- style.css
|   `-- script.js
|-- data/
|   `-- metrics.db
|-- requirements.txt
|-- README.md
|-- RELATORIO_BASE.md
`-- .gitignore
```

O arquivo `data/metrics.db` e criado automaticamente na primeira execucao.
