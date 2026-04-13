# services/google_sheets.py
import pandas as pd
from io import StringIO
import aiohttp

async def fetch_sheet(spreadsheet_id: str) -> pd.DataFrame:
    url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise Exception("Таблица недоступна")
            text = await resp.text()
    return pd.read_csv(StringIO(text), on_bad_lines='skip', header=None)