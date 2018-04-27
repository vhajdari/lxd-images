import grequests
import requests
import json
import datetime
import hashlib
import uuid
from functools import partial
from timeit import default_timer as timer

REMOTE = 'https://images.linuxcontainers.org'
FILE_NAME = 'images.json'

class Images:
    def __init__(self):
        self.urls = self.images()
        self.image_json = {}

    def exception(self, request, exception):
        print("Problem: {}: {}".format(request.url, exception))

    def fetch(self):
        results = grequests.map((grequests.get(url) for url in self.urls), exception_handler=self.exception, size=50)
        images = []
        for result in results:
            images.append(result.text)

        self.image_json.update({
            'source': REMOTE,
            'timestamp': '{:%Y-%m-%dT%H:%M:%S}'.format(datetime.datetime.utcnow()),
            # 'sha1': self.sha1_fingerprint(results),
            'run_id': str(uuid.uuid4()).replace('-', ''),
            'images': images
        })
        self.save(self.image_json)
        # print(self.image_json)

    def images(self):
        url = REMOTE
        r = requests.get(url + '/1.0/images')
        i = r.json()
        images = i.get('metadata')
        img_list = []
        for image in images:
            img_list.append(url + image)
        return img_list

    def save(self, data):
        try:
            with open(FILE_NAME, 'w') as f:
                print('Saving image file: {}'.format(FILE_NAME))
                f.write(json.dumps(data, indent=2))
        except (FileNotFoundError, IOError) as e:
            print('Unable to open file for writing.')
            print(e)

    def md5_fingerprint(self, data):
        with open(data, 'b') as f:
            d = hashlib.sha1()
            for buf in iter(partial(f.read, 128), b''):
                d.update(buf)
        return d.hexdigest()

    def sha1_fingerprint(cls, data):
        sha1 = hashlib.sha1(data).hexdigest()
        return sha1

if __name__ == "__main__":
    # start = timer()
    images = Images()
    images.fetch()
    # end = timer()
    # print('it took {} sec to complete'.format(round(end - start, 4)))

