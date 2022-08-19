from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
import requests
import json
import os
import time
import protondb_api

api_url = 'https://api.steampowered.com/ISteamApps/GetAppList/v0002/?format=json'
steamapi = os.path.join(os.path.dirname(__file__), 'steam_api.py')
steamjson = os.path.join(os.path.dirname(__file__), 'steamapi.json')
PDB = 'https://www.protondb.com/app/'


class Extension(Extension):

    def __init__(self):
        super(Extension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):

    def download_api(self):
        """Download API json file."""
        data = requests.get(api_url)
        with open(steamjson, 'wb')as file:
            file.write(data.content)

    def steam_api_check(self):
        """Check if api json file exists or is outdated."""
        try:
            age = int(time.time() - os.path.getmtime(steamjson))
            if age > 43200:
                self.download_api()
        except FileNotFoundError:
            self.download_api()

    def on_event(self, event, extension):
        """Query SteamDB."""
        self.steam_api_check()
        num = extension.preferences['search_results']
        print(num)
        query = event.get_argument() or str()
        if len(query.strip()) == 0:
            return RenderResultListAction([
                ExtensionResultItem(icon='icon.png',
                                    name='No input',
                                    on_enter=HideWindowAction())
            ])
        else:
            data = protondb_api.get_data(query, num)
            items = []
            if data.strip() != '':
                jdata = json.loads(data)
                for i in jdata:
                    items.append(ExtensionResultItem(
                        icon='icon.svg',
                        name=f"[{i['pdb']}] {i['name']} ({i['appid']})",
                        description=f"{PDB}{i['appid']}",
                        on_enter=OpenUrlAction(f"{PDB}{i['appid']}")))

            return RenderResultListAction(items)


if __name__ == '__main__':
    Extension().run()
