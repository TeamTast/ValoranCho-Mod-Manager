import flet as ft
import threading
import time
import logging
import os
import requests
import json
import re
import shutil
from datetime import datetime
from logging import getLogger, StreamHandler, DEBUG

# Logger configuration
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False

# Variables
Ver = "1.12.2"
AppdataPath = os.getenv('APPDATA') + "\\"
VersionsPath = AppdataPath + ".minecraft\\versions"
ProfilePath = AppdataPath + ".minecraft\\launcher_profiles.json"
CustomPath = AppdataPath + ".cho\\"
ModsPath = CustomPath + "mods\\"
ModsUri = "https://files-cho.tast.jp/manager/mods.json"
ForgeUri = "https://files-cho.tast.jp/manager/link.json"
ForgeProfileUri = "https://files-cho.tast.jp/manager/forge.json"

# Functions
def GetJson(uri):
    response = requests.get(uri)
    if response.status_code == 200:
        return response.json()
    else:
        return response.status_code

def DlFile(url, dir, filename=None):
    if not os.path.exists(dir):
        os.makedirs(dir)
    if filename is None:
        filename = url.split('/')[-1]
    filePath = os.path.join(dir, filename)
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(filePath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

def ProfileAdd(Ver, dataName):
    newData = {
        "created": datetime.now().isoformat(),
        "icon": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAACXBIWXMAAAsTAAALEwEAmpwYAAACcElEQVRYhe2XzU/TYBzHP2PdyraMOjYWLMJ0Ghghvr8kxGRHPRkPeuTs/+PVI1cTbx70YmJMTCQEX2KyREAhUDZhq1uzbt068bBQKVtLjbBd9j09z/N72u+339+vz4uvrBv79BECwL75G+NXtafE4pkIPmGoLaBRqbHxYrmnAs4/vo04GmGop6xdMBAwECC4BSOyhDAcwFB16qreewGTd6eJyjEAtj+sorxfP3EBnlNQLVROnBy6OHBgO4Bf/BsWxABSOmH1y+t7pyPgsO2Hkb532dZfevr6dAT8L+T5NCPn4lS2ip5qpkNAabVAabWAUda5eP8K/qDAXk6h9C3vWURUjmEaTYRQgMhZCXBOWYeAnyubVtsfbIcrm0XPOS/l8kzcuUTsQpLYkyQAmqI6Pu/4FwihgNU2jSZSOoGUTtjGu+HweqEpKq2G6TrfsQYOrAOYfnDDFtt4m7M5dRSaohKVY+SeL7mSg4sDohQGQC9qaIqKodWsWCqbYTgWPvblXuDoQLVQZuXZG8xa0xqbW5gnHI8CMJoZt1W5EAowmZ0hlk7iDwoYWo3k9SlXp8DFgapStpEDVLZKVtus23ObvDZJIiNbTonREKlshrmFeSKyhBM8L8URWWJsdgKAVsOklNuxxf1iuzh3v24D7TrQixrheJSZhzcdU+ZpNxyZijM2O4E/KNBqmKy9+tzpzmaR8aspUtkMADvL36nulJl5dAt9V3PcTV0FtGpNpFScltEk//EHZr395UfJob3QfFl8x2hmnFIubxGuvfyEWe+c70lAXdX/aQvuNv+4c0TfT0QDAQMBvrJu7Pfzcurr9/X8D89S+mvg76YQAAAAAElFTkSuQmCC",
        "lastVersionId": dataName,
        "javaArgs": "-Xmx4G -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC -XX:G1NewSizePercent=20 -XX:G1ReservePercent=20 -XX:MaxGCPauseMillis=50 -XX:G1HeapRegionSize=32M",
        "name": dataName,
        "type": "custom"
    }
    with open(ProfilePath, "r") as file:
        data = json.load(file)
    data["profiles"][dataName] = newData
    with open(ProfilePath, "w") as file:
        json.dump(data, file, indent=2)

def InstallForge():
    response = requests.get(ForgeUri)
    data = response.json()
    link = data.get("link", "")
    
    filename_pattern = r'/([^/]+)\.jar$'
    filename_match = re.search(filename_pattern, link)
    if filename_match:
        filename = filename_match.group(1)
        parts = filename.split('-')
        if len(parts) == 4:
            name, version, build, filetype = parts
        else:
            parts = ""
    else:
        name, version, build, filetype = "", "", "", ""
    
    forgeDir = os.path.join(AppdataPath, ".minecraft\\libraries\\net\\minecraftforge\\forge\\", f"{version}-{build}\\")
    forgeVer = f"cho-{Ver}-forge-{build}"
    forgeProfileDir = os.path.join(AppdataPath, ".minecraft\\versions\\", forgeVer + "\\")
    forgeProfilePath = forgeVer + ".json"
    forgePath = f"forge-{Ver}-{build}.jar"

    logger.info('[INFO]: Forgeのダウンロードを開始します')
    DlFile(link, forgeDir, forgePath)
    logger.info('[INFO]: Forgeのインストール Step2')
    DlFile(ForgeProfileUri, forgeProfileDir, forgeProfilePath)
    ProfileAdd(Ver, forgeVer)
    logger.info('[INFO]: Forgeのインストールが完了しました')

def DelFiles(name, folder_path):
    if os.path.exists(folder_path):
        logger.info(f'[INFO]: {name} の削除を開始します')
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                logger.error(f'[ERROR]: 削除に失敗: {file_path} 理由: {e}')
        logger.info(f'[INFO]: {name} の削除が完了しました')
    else:
        logger.info(f'[INFO]: フォルダが存在しません: {folder_path}')

def DlMods():
    DelFiles("Mod", ModsPath)
    logger.info('[INFO]: Modのダウンロードを開始します')
    response = requests.get(ModsUri)
    if response.status_code == 200:
        mods_data = response.json().get("mods", [])
        for mod in mods_data:
            url = mod.get("url", "")
            name = mod.get("name", "unknown")
            if url:
                DlFile(url, ModsPath, name + ".jar")
                logger.info(f'[INFO]: {name} のダウンロードを開始しました')
    else:
        logger.error(f'[ERROR]: Modのダウンロードでエラーが発生しました。 {response.status_code}')
    logger.info('[INFO]: Modのダウンロードが完了しました。')

# GUI logging handler
class GUIHandler(logging.Handler):
    def __init__(self, log_widget, max_logs=100):
        super().__init__()
        self.log_widget = log_widget
        self.max_logs = max_logs

    def emit(self, record):
        msg = self.format(record)
        if len(self.log_widget.controls) >= self.max_logs:
            del self.log_widget.controls[0]
        self.log_widget.controls.append(ft.Text(value=msg))
        self.log_widget.scroll_position = 1.0
        self.log_widget.update()

# GUI log polling function
def poll_log(page):
    while True:
        time.sleep(0.1)
        page.update()

# Threaded functions
def run_install_forge(status_bar):
    status_bar.value = "ステータス: Forge をインストール中..."
    status_bar.update()
    InstallForge()
    status_bar.value = "ステータス: Forge のインストールが完了しました"
    status_bar.update()

def run_dl_mods(status_bar):
    status_bar.value = "ステータス: Mod をダウンロード中..."
    status_bar.update()
    DlMods()
    status_bar.value = "ステータス: Mod のダウンロードが完了しました"
    status_bar.update()

def run_functions_sequentially(page, status_bar):
    thread =threading.Thread(target=run_functions_sequentially_thread, args=(page, status_bar))
    thread.start()

def run_functions_sequentially_thread(page, status_bar):
    run_install_forge(status_bar)
    run_dl_mods(status_bar)
    status_bar.value = "ステータス: 初期設定が完了しました"
    status_bar.update()

# Main function for GUI
def main(page: ft.Page):
    page.title = "ValoranCho Mod Manager Ver 1.0"
    page.window_center()
    page.window_width = 800
    page.window_height = 500

    # Title
    title = ft.Container(ft.Text("ValoranCho Mod Manager", style="headlineMedium"), margin=15)
    page.add(title)

    # Main container
    main_container = ft.Row(expand=True)
    page.add(main_container)

    # Button column
    button_column = ft.Container(ft.Column(
        width=200,
        alignment=ft.alignment.center,
        controls=[
            ft.ElevatedButton("初期設定", on_click=lambda e: run_functions_sequentially(page, status_bar), width=170),
            ft.ElevatedButton("Forge をインストール", on_click=lambda e: run_install_forge(status_bar), width=170),
            ft.ElevatedButton("Mod をダウンロード", on_click=lambda e: run_dl_mods(status_bar), width=170),
        ]
    ), margin=10)
    button_column.border = ft.border.only(right=ft.border.BorderSide(1, "Black"))
    main_container.controls.append(button_column)

    # Log display area
    log_text = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, auto_scroll=True, spacing=10, expand=True, width=500)
    log_text_container = ft.Container(content=log_text, margin=10)
    main_container.controls.append(log_text_container)

    # GUI log handler
    gui_handler = GUIHandler(log_text)
    logger.addHandler(gui_handler)

    # Status bar
    status_bar = ft.Text("ステータス: 準備完了", width=page.window_width, style="bodySmall", text_align=ft.TextAlign.LEFT)
    status_bar_container = ft.Container(content=status_bar, padding=10)
    status_bar_container.border = ft.border.only(top=ft.border.BorderSide(1, "Black"))
    page.add(status_bar_container)

    # Log polling thread
    polling_thread = threading.Thread(target=poll_log, args=(page,), daemon=True)
    polling_thread.start()

ft.app(target=main)