import sqlite3
import asyncio
from typing import Any, List, Optional, Tuple
import aiosqlite


class Database:
    """Asynchrone SQLite-Datenbank-Klasse."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._connection: Optional[aiosqlite.Connection] = None

    async def _get_connection(self) -> aiosqlite.Connection:
        """Gibt eine aktive Datenbankverbindung zurück."""
        if self._connection is None:
            self._connection = await aiosqlite.connect(self.db_path)
            await self._connection.execute("PRAGMA foreign_keys = ON")
        return self._connection

    def execute(self, query: str, params: Tuple = ()) -> None:
        """Synchrone Ausführung (für einfache Operationen)."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()

    async def execute_async(self, query: str, params: Tuple = ()) -> None:
        """Asynchrone Ausführung."""
        conn = await self._get_connection()
        await conn.execute(query, params)
        await conn.commit()

    def fetch_one(self, query: str, params: Tuple = ()) -> Optional[Tuple]:
        """Synchrone Abfrage einer einzelnen Zeile."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchone()
        conn.close()
        return result

    async def fetch_one_async(self, query: str, params: Tuple = ()) -> Optional[Tuple]:
        """Asynchrone Abfrage einer einzelnen Zeile."""
        conn = await self._get_connection()
        async with conn.execute(query, params) as cursor:
            return await cursor.fetchone()

    def fetch_all(self, query: str, params: Tuple = ()) -> List[Tuple]:
        """Synchrone Abfrage aller Zeilen."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return results

    async def fetch_all_async(self, query: str, params: Tuple = ()) -> List[Tuple]:
        """Asynchrone Abfrage aller Zeilen."""
        conn = await self._get_connection()
        async with conn.execute(query, params) as cursor:
            return await cursor.fetchall()

    async def close(self):
        """Schließt die Datenbankverbindung."""
        if self._connection:
            await self._connection.close()
            self._connection = None