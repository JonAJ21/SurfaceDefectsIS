import asyncio
import subprocess
from functools import wraps
import os
from pathlib import Path
import shutil
import sys
from typing import Optional

import requests
from typer import Argument, Option, Typer
import typer
from core.config.settings import settings

cli = Typer()


def async_typer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))
    return wrapper


@cli.command()
@async_typer 
async def download_osm(region: str, output_dir: str):
    
    regions = {
        "moscow_oblast": "https://download.geofabrik.de/russia/central-fed-district-latest.osm.pbf",
        "small": "https://download.geofabrik.de/europe/isle-of-man-latest.osm.pbf",
    }
    
    if region not in regions:
        print(f"Unknown region. Available: {list(regions.keys())}")
        return None
    
    url = regions[region]
    output_file = Path(output_dir) / f"{region}.osm.pbf"
    
    print(f"Downloading {region} from {url}")
    print(f"Output: {output_file}")
    
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(output_file, 'wb') as f:
        downloaded = 0
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            downloaded += len(chunk)
            if total_size:
                percent = (downloaded / total_size) * 100
                print(f"\rProgress: {percent:.1f}%", end="")
    
    print(f"\nDownloaded to {output_file}")
    return str(output_file)

@cli.command()
def import_osm(
    pbf_file: Path = typer.Argument(
        settings.pbf_file_path,
        help="Путь к .osm.pbf файлу",
    ),
    host: str = typer.Option(settings.postgres_host, "--host", "-h", help="Хост БД"),
    port: int = typer.Option(settings.postgres_port, "--port", "-P", help="Порт БД"),
    dbname: str = typer.Option(settings.postgres_name, "--dbname", "-d", help="Имя БД"),
    user: str = typer.Option(settings.postgres_user, "--user", "-U", help="Пользователь БД"),
    password: Optional[str] = typer.Option(
        None,
        "--password", "-W",
        hide_input=True,
        help="Пароль БД (по умолчанию из settings)",
    ),
    # Параметры osm2pgsql
    cache_mb: int = typer.Option(2048, "--cache", "-C", help="Кэш ОЗУ в МБ"),
    slim: bool = typer.Option(True, "--slim/--no-slim", help="Slim-режим"),
    append: bool = typer.Option(False, "--append", "-a", help="Добавить к существующим таблицам"),
    processes: int = typer.Option(4, "--processes", "-p", help="Потоки CPU"),
):
    """Импорт OSM .pbf в PostGIS через osm2pgsql"""
    
    db_password = password or settings.postgres_password

    if not shutil.which("osm2pgsql"):
        typer.echo("osm2pgsql не найден в PATH.", err=True)
        raise typer.Exit(1)

    pbf_path = Path(pbf_file)
    if not pbf_path.exists():
        typer.echo(f"Файл не найден: {pbf_path}", err=True)
        raise typer.Exit(1)

    cmd = ["osm2pgsql"]
    cmd.append("-a" if append else "-c")
    cmd.extend(["-d", dbname, "-U", user, "-H", host, "-P", str(port)])
    cmd.extend(["--cache", str(cache_mb), "--number-processes", str(processes)])
    if slim:
        cmd.append("--slim")
    cmd.append("--hstore")
    cmd.append(str(pbf_path))

    env = os.environ.copy()
    env["PGPASSWORD"] = db_password

    size_mb = pbf_path.stat().st_size / (1024 ** 2)
    typer.echo(f"  {pbf_path.name} ({size_mb:.1f} МБ) в {dbname}@{host}:{port}...")

    proc = None
    try:
        with subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, env=env, bufsize=1
        ) as proc:
            for line in proc.stdout:
                line = line.rstrip()
                if not line: continue

                if any(k in line.lower() for k in ["processing:", "node", "way", "relation", "indexing"]):
                    sys.stdout.write(f"\r{line}  ")
                    sys.stdout.flush()
                else:
                    sys.stdout.write(f"\n  {line}\n")
                    sys.stdout.flush()

            proc.wait()
            sys.stdout.write("\n")

            if proc.returncode != 0:
                typer.echo(f"Ошибка импорта (код {proc.returncode})", err=True)
                raise typer.Exit(1)

            typer.echo("Импорт успешно завершён!")

    except KeyboardInterrupt:
        typer.echo("\nИмпорт прерван пользователем", err=True)
        if proc:
            proc.terminate()
            try: proc.wait(timeout=5)
            except subprocess.TimeoutExpired: proc.kill()
        raise typer.Exit(130)
    except Exception as e:
        typer.echo(f"Критическая ошибка: {e}", err=True)
        raise typer.Exit(1)


@cli.command()
@async_typer
async def init():
    print("Init")

if __name__ == "__main__":
    cli()