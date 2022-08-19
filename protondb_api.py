import json
import os
import requests
import sys
import time

JSON_FILE = os.path.join(os.path.dirname(__file__), 'steamapi.json')
PDB_API = 'https://www.protondb.com/api/v1/reports/summaries/'
USERAGENT = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:103.0)'
             ' Gecko/20100101 Firefox/103.0', 'Referer': '-'}


def Sort(e):
    """Sort Function."""
    return e[0]["len"]


def get_protondb(appid):
    """Get Proton rating from ProtonDB."""
    resp = requests.get(f'{PDB_API}{appid}.json', headers=USERAGENT)
    if resp.ok:
        pdb = json.loads(resp.text)
        return pdb["tier"]
    else:
        return "Not Found"


def get_query():
    """Get search string."""
    query = ''
    n = len(sys.argv)
    if n < 2:
        sys.exit(0)
    for i in range(1, n):
        query += f"{sys.argv[i]} "
    query.lower()
    return query.lower()


def get_data(query, num=5, err=5):
    """Get appid."""
    f = open(JSON_FILE,)
    json_list = json.load(f)

    # extract games data by query string
    # and store it in a list
    list = []
    for i in range(1, len(json_list["applist"]['apps'])):
        el = json_list["applist"]['apps'][i]
        if query.lower().strip() in el['name'].lower().strip():
            list.append([{'name': el['name'],
                        'appid': el['appid'], 'len': len(el['name'])}])
    # sort the list
    list.sort(reverse=False, key=Sort)

    # create json string
    newj = []
    li = 0
    error = 0
    for i in list:
        pdb = get_protondb(i[0]["appid"])
        if pdb != "Not Found":
            pdb = pdb.title()
            jj = {"name": i[0]["name"], "appid": i[0]["appid"], "pdb": pdb}
            newj.append(jj)
            # sleep to prevent hammering the server
            time.sleep(0.2)
            li += 1
            if li == num:
                break
        else:
            error += 1
            if error == err:
                break
    # return json string
    return json.dumps(newj)
