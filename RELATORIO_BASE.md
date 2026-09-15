# Implementacao de APIs GraphQL e WebSocket

## 1. Introducao

Este trabalho tem como objetivo implementar um sistema simples de monitoramento de recursos do computador, demonstrando o uso de dois paradigmas de APIs: GraphQL e WebSocket. O sistema coleta periodicamente informacoes de CPU e memoria RAM, armazena os dados em banco SQLite e apresenta as metricas em uma interface web.

## 2. Tecnologias utilizadas

- Python: linguagem principal usada no backend.
- FastAPI: framework utilizado para criar o servidor HTTP, o endpoint GraphQL, o WebSocket e servir os arquivos estaticos.
- GraphQL: tecnologia usada para consultar o historico das metricas de forma flexivel.
- WebSocket: tecnologia usada para enviar dados em tempo real do servidor para o navegador.
- SQLite: banco de dados local usado para armazenar o historico.
- SQLAlchemy: biblioteca usada para comunicar a aplicacao Python com o banco SQLite.
- psutil: biblioteca usada para coletar uso de CPU e memoria RAM da maquina.

## 3. Arquitetura do sistema

O fluxo principal de coleta funciona assim:

```text
psutil -> coleta -> servidor FastAPI -> SQLite
```

O `psutil` coleta as informacoes da maquina. Em seguida, o servidor salva cada registro no banco SQLite.

Para consultas historicas, o fluxo e:

```text
SQLite -> GraphQL -> cliente
```

O cliente faz uma query GraphQL e recebe apenas os campos solicitados.

Para transmissao em tempo real, o fluxo e:

```text
coleta -> WebSocket -> cliente em tempo real
```

Quando uma nova metrica e coletada, ela tambem e enviada automaticamente aos navegadores conectados.

## 4. API GraphQL

A API GraphQL tem como objetivo consultar o historico das metricas armazenadas.

Endpoint:

```text
http://127.0.0.1:8000/graphql
```

Queries disponiveis:

- `latestMetrics(limit: Int)`: retorna as ultimas metricas coletadas.
- `averageMetrics(minutes: Int)`: calcula a media de CPU e RAM dos ultimos minutos.
- `peakMetrics(minutes: Int)`: retorna os maiores valores de CPU e RAM em um periodo.
- `metricsBetween(start: String, end: String)`: retorna metricas entre duas datas.
- `metricsCount`: retorna a quantidade de registros no banco.

Exemplo:

```graphql
query {
  latestMetrics(limit: 10) {
    timestamp
    cpuPercent
    ramPercent
  }
}
```

## 5. API WebSocket

A API WebSocket tem como objetivo transmitir metricas em tempo real para o cliente.

Endpoint:

```text
ws://127.0.0.1:8000/ws/metrics
```

O navegador abre uma conexao persistente com o servidor. Enquanto a conexao estiver ativa, o servidor envia automaticamente as novas metricas coletadas. Assim, a tela e atualizada sem recarregar a pagina e sem fazer requisicoes repetidas.

## 6. Comparacao GraphQL x WebSocket

GraphQL:

- Mais adequado para consulta ao historico.
- Permite selecionar exatamente os campos desejados.
- Permite consultas especificas e mais flexiveis.
- O cliente solicita os dados quando precisa.

WebSocket:

- Mantem uma conexao persistente.
- O servidor envia dados automaticamente.
- E adequado para informacoes em tempo real.
- Evita polling constante do cliente.

## 7. Testes

Esta secao deve ser preenchida apos a execucao dos testes.

Sugestoes de testes:

- Verificar se a pagina web recebe novas metricas sem atualizar o navegador.
- Verificar se o status do WebSocket muda para conectado e desconectado.
- Executar a query `latestMetrics` e conferir se os dados retornados existem no banco.
- Executar a query `averageMetrics` para diferentes intervalos.
- Executar a query `peakMetrics` e conferir os maiores valores no periodo.
- Executar a query `metricsBetween` com datas conhecidas.
- Medir a quantidade de requisicoes HTTP usadas pelo GraphQL.
- Observar o comportamento em tempo real do WebSocket.
- Comparar o tamanho aproximado dos dados transmitidos em cada abordagem.

Nao foram registrados resultados experimentais neste modelo de relatorio. Os valores devem ser preenchidos somente depois da realizacao dos testes.

## 8. Conclusao

O projeto demonstra que GraphQL e WebSocket resolvem problemas diferentes. O GraphQL e adequado para consultas ao historico, pois permite ao cliente escolher os campos e realizar consultas especificas. O WebSocket e adequado para dados em tempo real, pois mantem uma conexao aberta e permite que o servidor envie novas informacoes automaticamente.

Assim, no contexto deste monitor de recursos, o GraphQL atende bem a recuperacao de dados armazenados, enquanto o WebSocket atende melhor a atualizacao continua da interface.
