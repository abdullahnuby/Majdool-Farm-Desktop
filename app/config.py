from pathlib import Path
import os
APP_DIR=Path(os.getenv("LOCALAPPDATA",Path.home()))/"MedjoolFarmManager"
APP_DIR.mkdir(parents=True,exist_ok=True)
DATABASE_URL=f"sqlite:///{APP_DIR/'medjool_farm.db'}"
