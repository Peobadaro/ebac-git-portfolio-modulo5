"""
EBAC - Backend Python - Exercício Módulo 4 (Threads e Processos)

Web scraping do catálogo de filmes usado pelo professor
(https://havokkmorands.github.io/movie-catalog/), que substituiu o IMDb
por causa dos bloqueios do site.

O script baixa a lista de filmes e entra na página de cada um para pegar
título, lançamento, nota e sinopse. A mesma extração é feita de 3 jeitos,
para comparar o tempo:

    1. sequencial  -> 1 thread, um filme por vez
    2. threads     -> ThreadPoolExecutor (concurrent.futures)
    3. processos   -> ProcessPoolExecutor (concurrent.futures)

O resultado é gravado em movies.csv.

Uso:
    python multithreading.py              # roda os 3 modos (10 threads)
    python multithreading.py 20           # muda o MAX_THREADS para 20
"""

import concurrent.futures
import csv
import random
import sys
import time

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://havokkmorands.github.io"
CATALOG_URL = f"{BASE_URL}/movie-catalog/"
CSV_FILE = "movies.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8",
}

MAX_THREADS = 10


def get_soup(url):
    """Baixa uma página e devolve o HTML já interpretado pelo BeautifulSoup."""
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()
    return BeautifulSoup(response.content, "html.parser")


def get_text(container, test_id, prefix=""):
    """Pega o texto de um elemento pelo data-testid, tirando o rótulo."""
    tag = container.find(attrs={"data-testid": test_id})
    if tag is None:
        return None
    return tag.get_text(strip=True).replace(prefix, "").strip()


def extract_movie_links():
    """Lê a página do catálogo e devolve o link de cada filme."""
    soup = get_soup(CATALOG_URL)
    container = soup.find("section", attrs={"data-testid": "movies-list"})
    if container is None:
        print("Lista de filmes não encontrada na página.")
        return []

    links = []
    for movie in container.find_all("article", attrs={"data-testid": "movie-item"}):
        a_tag = movie.find("a", attrs={"data-testid": "movie-link"}, href=True)
        if a_tag:
            links.append(f"{BASE_URL}/{a_tag['href'].lstrip('/')}")
    return links


def extract_movie_details(movie_link):
    """Entra na página do filme e devolve [título, lançamento, nota, sinopse]."""
    time.sleep(random.uniform(0, 0.2))  # pausa curta para não sobrecarregar o site
    soup = get_soup(movie_link)

    detail = soup.find("section", attrs={"data-testid": "movie-detail"})
    if detail is None:
        print(f"Detalhe do filme não encontrado: {movie_link}")
        return None

    row = [
        get_text(detail, "movie-title"),
        get_text(detail, "movie-release", "Lançamento:"),
        get_text(detail, "movie-rating", "Nota:"),
        get_text(detail, "movie-synopsis", "Sinopse:"),
    ]
    return row if all(row) else None


def run_sequential(links):
    """Modo 1: uma thread só, um filme depois do outro."""
    return [extract_movie_details(link) for link in links]


def run_threads(links):
    """Modo 2: pool de threads. Usa min(MAX_THREADS, nº de filmes) threads."""
    workers = min(MAX_THREADS, len(links))
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        return list(executor.map(extract_movie_details, links))


def run_processes(links):
    """Modo 3: pool de processos. Usa min(MAX_THREADS, nº de filmes) processos."""
    workers = min(MAX_THREADS, len(links))
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
        return list(executor.map(extract_movie_details, links))


def save_csv(rows):
    """Grava os filmes no movies.csv (uma escrita só, sem disputa entre threads)."""
    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["title", "release", "rating", "synopsis"])
        writer.writerows(rows)


def timed(name, func, links):
    """Executa um modo e mede o tempo."""
    start = time.perf_counter()
    rows = [row for row in func(links) if row]
    elapsed = time.perf_counter() - start
    print(f"{name:<12} {len(rows):>3} filmes em {elapsed:6.2f} s")
    return rows, elapsed


def main():
    global MAX_THREADS
    if len(sys.argv) > 1:
        MAX_THREADS = int(sys.argv[1])

    links = extract_movie_links()
    if not links:
        return
    print(f"{len(links)} filmes encontrados | MAX_THREADS = {MAX_THREADS}\n")

    _, t_seq = timed("Sequencial", run_sequential, links)
    rows, t_thr = timed("Threads", run_threads, links)
    _, t_proc = timed("Processos", run_processes, links)

    save_csv(rows)
    for row in rows:
        print(" | ".join(row[:3]))

    print(f"\nThreads foram {t_seq / t_thr:.1f}x mais rápidas que o sequencial.")
    print(f"Processos foram {t_seq / t_proc:.1f}x mais rápidos que o sequencial.")
    print(f"Resultado salvo em {CSV_FILE}")


if __name__ == "__main__":
    main()
