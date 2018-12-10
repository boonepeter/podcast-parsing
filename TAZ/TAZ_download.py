import os
import requests
import re
import pandas as pd

from bs4 import BeautifulSoup

tracking_doc_url = "https://docs.google.com/document/d/e/2PACX-1vT5IOvuFz988qAbP2P5ELDIekf4mUdfBsF1LGGW8CxMcry0YjJ34H1iFYN1qx0B7eYPUzw4CiSd8kbM/pub"
tracking_html = requests.get(tracking_doc_url)


tracking_beautiful = BeautifulSoup(tracking_html.text)

rows = tracking_beautiful.findAll('tr')
completed_links = {}

for row in rows:
    if row.text.endswith('100%'):
        a = row.find('a')
        completed_links[a.text] = a['href']

def google_doc_download(docID, download_as='txt'):
    return 'https://docs.google.com/document/d/' + docID + '/export?format=' + download_as

for episode, link in completed_links.items():
    try:
        docID = re.search(string=link, pattern=r'(?:/d/|id%3D)(.*?)(?:/|&)')[1]
    except:
        print(f"{episode} didn't download ({link})")
        continue
    download_link = google_doc_download(docID, download_as='txt')
    with open(os.path.join(os.getcwd(), 'data', episode + '.txt'), 'w') as openfile:
        document = requests.get(download_link)
        openfile.write(document.text)

docs = os.listdir(os.path.join(os.getcwd(), 'data'))

for script in docs:
    with open(os.path.join(os.getcwd(), 'data', script)) as myfile:
        onefile = pd.read_csv(myfile, sep='\n', header=None)
    onefile[:][0] = onefile[:][0].str.lower()
    onefile = pd.DataFrame(onefile[0].str.split(':', expand=True))
    onefile = onefile.fillna('')
    onefile.iloc[:,1] = onefile.iloc[:,1].astype(str).str.cat(onefile.iloc[:,2:])
    onefile = onefile.drop(columns=[i for i in range(2, len(onefile.columns))])
    try:
        epnum = int(re.search(string=script, pattern=r'[\d]+')[0])
    except:
        print(script)
        continue
    onefile['episode'] = epnum
    onefile.columns = ['speaker', 'lines', 'episode']
    try:
        onefile = onefile.iloc[onefile[onefile.speaker.str.startswith('[theme')].index[0] + 2:]
    except:
        pass
    onefile.speaker = onefile.speaker.str.strip()
    onefile = onefile[-onefile.speaker.str.contains('[\[\,\.\&\-\{\%]|and')]
    onefile = onefile[['episode', 'speaker', 'lines']]
    onefile.reset_index(inplace=True, drop=True)
    onefile.to_csv(os.path.join(os.getcwd(), 'export', f'{epnum}.csv'))


csvs = os.listdir(os.path.join(os.getcwd(), 'export'))



df = pd.read_csv(os.path.join(os.getcwd(), 'export', csvs[0]))
df.columns = ['line_num', 'episode', 'speaker', 'lines']



for csv in csvs[1:]:
    newdf = pd.read_csv(os.path.join(os.getcwd(), 'export', csv))
    newdf.columns = ['line_num', 'episode', 'speaker', 'lines']
    df = df.append(newdf)

df.reset_index(inplace=True, drop=True)

df = df.sort_values(by=['episode', 'line_num'], ascending=True)
df.line_num = df.line_num.astype(int)
df.episode = df.episode.astype(int)


df.to_csv('./TAZ.csv')
