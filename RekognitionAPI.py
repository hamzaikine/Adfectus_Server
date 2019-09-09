
from flask import jsonify
import boto3
from flask import Flask
from flask_restful import Resource, Api, reqparse
import random
import requests
from datetime import datetime
import os

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()


class Pictures(Resource):
    def get(self):
        return jsonify({"Error": "You need to provide a picture."})

    def post(self):
        parser.add_argument('url', type=str)
        args = parser.parse_args()
        url = args['url']
        imageFile = getImage(url)

        if not imageFile is 'download_error':
            client = boto3.client('rekognition')
            fDetails = dict()
            with open(imageFile, 'rb') as image:
                response = client.detect_faces(Image={'Bytes': image.read()}, Attributes=['ALL'])

            for faceDetail in response['FaceDetails']:
                fDetails['Age'] = (int(faceDetail['AgeRange']['Low']) + \
                                   int(faceDetail['AgeRange']['High'])) / 2
                fDetails['Gender'] = (faceDetail['Gender']['Value'])
                fDetails['Emotions'] = [e for e in faceDetail['Emotions']]

            os.remove(imageFile)

            return jsonify(fDetails)
        else:
            os.remove(imageFile)
            return jsonify({"Download_error": "Failed downloading image"})


api.add_resource(Pictures, '/')


def getImage(URL):
    try:
        r = requests.get(URL, allow_redirects=True)
        random.seed(datetime.now())
        rand = random.randint(0, 2147483647)
        path = str(rand) + '.jpg'
        with open(path, 'wb') as cf:
            cf.write(r.content)
        return path
    except Exception:
        return 'download_error'


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
