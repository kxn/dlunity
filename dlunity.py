import argparse
import requests
import progressbar
import re
import os

CHUNK_SIZE= 1048576 * 5
TERM_SIZE = os.get_terminal_size().columns

def download_url(url):
    file_name = url.split('/')[-1]
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        widgets=[
            file_name, ":",
            progressbar.Bar(),
            progressbar.FileTransferSpeed(),
            ' [', progressbar.Timer(), ' / ', progressbar.ETA(), ']',
        ] 
        bar = progressbar.ProgressBar(maxval=int(r.headers.get('content-length')), widgets = widgets, term_width=TERM_SIZE)
        pos = 0
        bar.start()
        with open(file_name, 'wb') as f:
            for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    pos += len(chunk)
                    bar.update(pos)
                    f.write(chunk)
            f.close()

class UnityHubLink:
    def __init__(self, hublink, platform) -> None:
        m = re.match('unityhub://([\w\d\.]+)/([\d\w]+)', hublink)
        if not m:
            raise Exception("Unknown hub link %s" % hublink)
        self.version = m[1]
        self.hash = m[2]
        self.platform = platform
    def get_init_file_url(self):
        return "%sunity-%s-%s.ini" % (self.get_base_url() , self.version, self.platform)
    def get_base_url(self):
        return "https://download.unitychina.cn/download_unity/%s/" % self.hash
    def get_file_list(self):
        result = []
        with requests.get(self.get_init_file_url(), allow_redirects=True) as r:
            r.raise_for_status()
            for l in r.text.split("\n"):
                if l.startswith("url="):
                    url = l[4:]    
                    if url.startswith("http"):
                        # Skip external links like Visual Studio
                        continue
                    url = self.get_base_url() + url
                    result.append(url.strip())
        return result    
    
parser = argparse.ArgumentParser()
parser.add_argument("--os", type=str, help="platform of unity to download", choices= ['win','osx', 'linux'], default='win')
parser.add_argument("hublink", type=str, help="unity hublink to download")
args = parser.parse_args()
print("Download Unity Tool (c) 2022 ")
for fn in UnityHubLink(args.hublink, args.os).get_file_list():
    print('Downloading %s' % fn)
    download_url(fn)
print("Done")
