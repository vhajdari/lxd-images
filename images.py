import grequests
import requests
import json
import datetime
import hashlib
import uuid


REMOTE = 'https://images.linuxcontainers.org'
FILE_NAME = 'images.json'

class Images:
    def __init__(self):
        self.urls = self.images()
        self.image_json = {}

    def exception(self, request, exception):
        print("Problem: {}: {}".format(request.url, exception))

    def fetch(self):
        images = []
        responses = grequests.map((grequests.get(url) for url in self.urls), exception_handler=self.exception, size=50)
        for response in responses:
            images.append(json.loads(response.text))

        self.image_json.update({
            'source': REMOTE,
            'timestamp': '{:%Y-%m-%dT%H:%M:%S}'.format(datetime.datetime.utcnow()),
            'sha1': self.sha1_fingerprint(images),
            'run_id': str(uuid.uuid4()).replace('-', ''),
            'images': images
        })
        self.save(self.image_json)
        # print(self.image_json)

    @staticmethod
    def images():
        url = REMOTE
        r = requests.get(url + '/1.0/images')
        i = r.json()
        images = i.get('metadata')
        img_list = []
        for image in images:
            img_list.append(url + image)
        return img_list

    @staticmethod
    def save(data):
        try:
            with open(FILE_NAME, 'w') as f:
                print('Saving image file: {}'.format(FILE_NAME))
                f.write(json.dumps(data, indent=2))
        except (FileNotFoundError, IOError) as e:
            print('Unable to open file for writing.')
            print(e)

    @staticmethod
    def sha1_fingerprint(data):
        sha1 = hashlib.sha1()
        sha1.update(repr(data).encode('utf-8'))
        return sha1.hexdigest()

if __name__ == "__main__":
    # from timeit import default_timer as timer
    # start = timer()
    images = Images()
    images.fetch()
    # end = timer()
    # print('it took {} sec to complete'.format(round(end - start, 4)))