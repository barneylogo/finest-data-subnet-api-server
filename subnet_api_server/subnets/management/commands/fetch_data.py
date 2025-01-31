# myapp/management/commands/fetch_data.py
import gzip
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand

from subnet_api_server.common.services import BittensorService
from subnet_api_server.subnets.models import Crawl
from subnet_api_server.subnets.models import Neuron
from subnet_api_server.subnets.models import WarcFile

HTTP_OK = 200
REQUEST_TIMEOUT = 30


class Command(BaseCommand):
    command_help = "Fetches data and commits it to the database"

    def handle(self, *args, **kwargs):
        self.fetch_neuron()

    def fetch_crawl(self):
        url = "https://index.commoncrawl.org/collinfo.json"
        response = requests.get(url)

        if response.status_code == HTTP_OK:
            crawls = response.json()
            for crawl in crawls:
                crawl_id = crawl["id"]
                index_url = (
                    f"https://data.commoncrawl.org/crawl-data/{crawl_id}/index.html"
                )
                index_response = requests.get(index_url)
                soup = BeautifulSoup(index_response.content, "html.parser")
                size = None
                try:
                    table = soup.find("table")
                    rows = table.find_all("tr")
                    for row in rows:
                        try:
                            cols = row.find_all("td")
                            if cols and "WARC" in cols[0].text:
                                size = cols[3].text.strip()
                                break
                        except Exception as e:
                            self.stdout.write(str(e))
                except Exception as e:
                    self.stdout.write(str(e))

                new_crawl = Crawl.objects.create(
                    dump=crawl["id"],
                    name=crawl["name"],
                    timegate=crawl["timegate"],
                    cdx_api=crawl["cdx-api"],
                    date_from=datetime.strptime(crawl["from"], "%Y-%m-%dT%H:%M:%S"),
                    date_to=datetime.strptime(crawl["to"], "%Y-%m-%dT%H:%M:%S"),
                    warc_size=size if size is not None else 0,
                )
                self.stdout.write(f"Added crawl: {new_crawl.name}")
        else:
            self.stdout.write("Error: Failed to fetch data from Common Crawl.")

    def fetch_warc_file(self, warc_path):
        try:
            warc_url = f"https://data.commoncrawl.org/{warc_path}"
            response = requests.head(warc_url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            size = response.headers.get("Content-Length")
            date = response.headers.get("Date")
            last_modified = response.headers.get("Last-Modified")
            etag = response.headers.get("ETag")
            return {
                "size": size,
                "date": date,
                "last_modified": last_modified,
                "etag": etag,
            }
        except requests.RequestException as e:
            self.stdout.write(f"Failed to retrieve WARC file size for {warc_path}: {e}")
            return {}

    def fetch_warc_files(self):
        try:
            crawl_ids = Crawl.objects.all()
            for crawl in crawl_ids[:2]:
                warc_url = f"https://data.commoncrawl.org/crawl-data/{crawl.dump}/warc.paths.gz"
                response = requests.get(warc_url)
                response.raise_for_status()
                warc_files = (
                    gzip.decompress(response.content).decode("utf-8").splitlines()
                )
                self.stdout.write(f"Found {len(warc_files)} WARC files")
                for warc_path in warc_files:
                    file = self.fetch_warc_file(warc_path)
                    new_warc_file = WarcFile.objects.create(
                        warc_path=warc_path,
                        crawl_id=crawl.id,
                        size=file["size"],
                        date=datetime.strptime(
                            file["date"],
                            "%a, %d %b %Y %H:%M:%S %Z",
                        ),
                        last_modified=datetime.strptime(
                            file["last_modified"],
                            "%a, %d %b %Y %H:%M:%S %Z",
                        ),
                        etag=file["etag"],
                    )
                    self.stdout.write(f"Added WARC file: {new_warc_file.id}")
        except Exception as e:
            self.stdout.write(str(e))

    def fetch_neuron(self):
        try:
            config = BittensorService.get_config()
            subtensor = BittensorService.get_subtensor()
            metagraph = subtensor.metagraph(netuid=config.netuid)

            for uid in metagraph.uids:
                hotkey = metagraph.hotkeys[uid]
                coldkey = metagraph.coldkeys[uid]
                new_neuron = Neuron.objects.create(
                    uid=int(uid),
                    hotkey=hotkey,
                    coldkey=coldkey,
                )
                self.stdout.write(f"Added neuron: {new_neuron.uid}")
        except Exception as e:
            self.stdout.write(str(e))

    def get_current_block(self):
        current_block = BittensorService.get_current_block()
        print(current_block)
