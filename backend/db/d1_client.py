import asyncio
import sqlite3
from contextlib import contextmanager

import httpx

from config.settings import settings


class D1Client:
    """Thin wrapper over Cloudflare D1 REST API.

    Falls back to a local SQLite file when D1 credentials are not set —
    lets the whole backend run and be tested without a Cloudflare account.
    """

    def __init__(self):
        self._local = not settings.use_d1
        if self._local:
            self._conn = sqlite3.connect(settings.local_sqlite_path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
        else:
            self._base_url = (
                f"https://api.cloudflare.com/client/v4/accounts/"
                f"{settings.d1_account_id}/d1/database/{settings.d1_database_id}/query"
            )
            self._headers = {
                "Authorization": f"Bearer {settings.d1_api_token}",
                "Content-Type": "application/json",
            }

    async def execute(self, sql: str, params: list | None = None) -> dict:
        params = params or []
        if self._local:
            return await asyncio.to_thread(self._local_execute, sql, params)
        result = await self._remote_query(sql, params)
        return result

    async def query(self, sql: str, params: list | None = None) -> list[dict]:
        params = params or []
        if self._local:
            return await asyncio.to_thread(self._local_query, sql, params)
        result = await self._remote_query(sql, params)
        return result.get("results", [])

    async def execute_batch(self, statements: list[dict]) -> list:
        if self._local:
            return await asyncio.to_thread(self._local_batch, statements)
        results = []
        for stmt in statements:
            results.append(await self._remote_query(stmt["sql"], stmt.get("params", [])))
        return results

    async def _remote_query(self, sql: str, params: list) -> dict:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                self._base_url, headers=self._headers, json={"sql": sql, "params": params}
            )
            resp.raise_for_status()
            data = resp.json()
            if not data.get("success", True):
                raise RuntimeError(f"D1 query failed: {data}")
            result = data.get("result", [{}])[0]
            return {"results": result.get("results", []), "meta": result.get("meta", {})}

    def _local_execute(self, sql: str, params: list) -> dict:
        with self._local_cursor() as cur:
            cur.execute(sql, params)
            self._conn.commit()
            return {"results": [], "meta": {"rows_written": cur.rowcount}}

    def _local_query(self, sql: str, params: list) -> list[dict]:
        with self._local_cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
            return [dict(row) for row in rows]

    def _local_batch(self, statements: list[dict]) -> list:
        results = []
        with self._local_cursor() as cur:
            for stmt in statements:
                cur.execute(stmt["sql"], stmt.get("params", []))
                if stmt["sql"].strip().upper().startswith("SELECT"):
                    results.append([dict(row) for row in cur.fetchall()])
                else:
                    results.append({"rows_written": cur.rowcount})
            self._conn.commit()
        return results

    @contextmanager
    def _local_cursor(self):
        cur = self._conn.cursor()
        try:
            yield cur
        finally:
            cur.close()


d1 = D1Client()
