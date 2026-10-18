"""Manage only the project's isolated, loopback-only PostgreSQL cluster on Windows.

Existing PostgreSQL services/data are never modified. Generated credentials stay ignored.
"""
import argparse
import os
from pathlib import Path
import secrets
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BIN = Path(os.environ.get("POSTGRES_BIN", "C:/Program Files/PostgreSQL/18/bin"))
DATA = ROOT / "work/postgres-data"
PORT = "55432"

def run(program, *args):
    def native_arg(value):
        # PostgreSQL Windows tools need an ASCII path on some localized systems.
        if isinstance(value, Path) and value.exists() and os.name == "nt":
            import ctypes
            buffer = ctypes.create_unicode_buffer(4096)
            if ctypes.windll.kernel32.GetShortPathNameW(str(value), buffer, len(buffer)):
                return buffer.value
        return str(value)
    result = subprocess.run([str(BIN / f"{program}.exe"), *map(native_arg, args)],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode:
        raise RuntimeError(f"{program}: {result.stderr or result.stdout}")
    return result.stdout

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["start", "stop", "status"])
    action = parser.parse_args().action
    if action == "stop":
        run("pg_ctl", "-D", DATA, "stop", "-m", "fast")
        print("Project PostgreSQL stopped")
        return
    if action == "status":
        print(run("pg_ctl", "-D", DATA, "status"))
        return
    if not (BIN / "initdb.exe").is_file():
        raise RuntimeError("PostgreSQL 18 binaries not found; set POSTGRES_BIN")
    env_path = ROOT / ".env"
    ROOT.joinpath("work").mkdir(exist_ok=True)
    fresh = not DATA.exists()
    if fresh:
        if env_path.exists():
            raise RuntimeError("Existing .env found; configure a cluster manually rather than overwrite credentials")
        password = secrets.token_hex(24)
        password_path = ROOT / "work/postgres-bootstrap-password"
        try:
            password_path.write_text(password, encoding="ascii")
            run("initdb", "-D", DATA, "-U", "technicalnexus", "--pwfile", password_path,
                "--auth", "scram-sha-256", "--encoding", "UTF8", "--locale", "C")
        finally:
            password_path.unlink(missing_ok=True)
        with (DATA / "postgresql.conf").open("a", encoding="utf-8") as f:
            f.write("\nlisten_addresses = '127.0.0.1'\nport = 55432\n")
        env_path.write_text(
            f"DATABASE_URL=postgresql+psycopg://technicalnexus:{password}@127.0.0.1:{PORT}/technicalnexus_dev\n"
            f"TEST_DATABASE_URL=postgresql+psycopg://technicalnexus:{password}@127.0.0.1:{PORT}/technicalnexus_test\n"
            "APP_LANGUAGE=es\nMANUALS_PATH=ManualesDeImpresoras/DCP-T430W\n", encoding="utf-8")
    status = subprocess.run([str(BIN / "pg_ctl.exe"), "-D", str(DATA), "status"], capture_output=True)
    if status.returncode:
        run("pg_ctl", "-D", DATA, "-l", ROOT / "work/postgres.log", "-w", "start")
    from dotenv import dotenv_values
    from sqlalchemy.engine import make_url
    import psycopg
    values = dotenv_values(env_path)
    connection_url = make_url(values["DATABASE_URL"])
    with psycopg.connect(host=connection_url.host, port=connection_url.port, user=connection_url.username,
                         password=connection_url.password, dbname="postgres", autocommit=True) as connection:
        for name in ("technicalnexus_dev", "technicalnexus_test"):
            if not connection.execute("SELECT 1 FROM pg_database WHERE datname = %s", (name,)).fetchone():
                from psycopg import sql
                connection.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))
    print("Project PostgreSQL ready on 127.0.0.1:55432; development and test databases available")

if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
