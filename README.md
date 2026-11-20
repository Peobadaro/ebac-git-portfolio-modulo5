# EBAC – Backend Python – Exercício Módulo 4 (Threads e Processos)

Web scraper do catálogo de filmes do professor (https://havokkmorands.github.io/movie-catalog/), que substituiu o IMDb por causa dos bloqueios do site.

Para cada filme pega **título, lançamento, nota e sinopse** e grava em `movies.csv`.

## Comparativo

A mesma extração roda de 3 jeitos e o script mostra o tempo de cada um:

| Modo | Como funciona |
|---|---|
| Sequencial | 1 thread, um filme por vez |
| Threads | `ThreadPoolExecutor` com `min(MAX_THREADS, nº de filmes)` threads |
| Processos | `ProcessPoolExecutor` com `min(MAX_THREADS, nº de filmes)` processos |

Como o trabalho é quase todo espera de rede (I/O), threads e processos ficam bem mais rápidos que o sequencial.

## Resultado (execução real, 30 filmes, 10 threads)

| Modo | Tempo | Ganho |
|---|---|---|
| Sequencial | 13,87 s | – |
| Threads | 0,56 s | 24,8x mais rápido |
| Processos | 1,14 s | 12,1x mais rápido |

Threads venceram processos porque o trabalho é espera de rede (I/O). Processos custam mais para criar e não ganham nada com isso. Saída completa em `resultado_execucao.txt`; dados em `movies.csv`.

## Como rodar

```bash
pip install -r requirements.txt
python multithreading.py        # MAX_THREADS = 10
python multithreading.py 5      # testa com 5 threads
python multithreading.py 20     # testa com 20 threads
```
