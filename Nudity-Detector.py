import os
import shutil
import urllib

from flask import Flask, request, jsonify
from keras import backend as K
from nudenet import NudeClassifier

app = Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    return "<h1>Nudity-Detector</h1><p>This site is a prototype API for Nudity image detection.</p> "


# For Multiple urls
@app.route('/api/batch', methods=['POST'])
def batch():
    req_json = request.get_json(force=True)
    if "urls" in req_json:
        image_entries = req_json["urls"]
    else:
        return 'Accepted formats are {"urls": ["url1", "url2"]}'
    a = url_to_path(image_entries)
    path = []
    for e in a:
        path.append("Temp/" + e)

    result = classify_from_paths(path, image_entries)

    return jsonify(result)


# For single urls
@app.route('/api/single')
def single_classify():
    if request.args.__contains__('url'):
        single_image = {'url': request.args.get('url')}
        result = classify_from_url(single_image)
        print(result)
        return jsonify(result)
    else:
        return "Missing  url parameter", 400


# For single image
def classify_from_url(image_entry):
    opener = urllib.request.build_opener()
    opener.addheaders = [
        ('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5')]
    urllib.request.install_opener(opener)
    try:
        f = "Temp/1.jpg"
        urllib.request.urlretrieve(image_entry['url'], f)
        result = classify(f)  # for classification

        if result[f]["unsafe"] >= result[f]["safe"]:
            result = {"status": "unsafe"}
        else:
            result = {"status": "safe"}
    except urllib.error.HTTPError as e:
        result = {'error_code': e.code, 'error_reason': e.reason}
    except urllib.error.URLError as e:
        result = {'error_code': 500, 'error_reason': str(e.reasson)}
    except Exception as e:
        result = {'error_code': 500, 'error_reason1': e.args}

    result.update(image_entry)
    return result


def classify_from_paths(paths, url):
    result = classify(paths)
    Result = {"Predictions": []}
    for (i, u) in zip(list(result.keys()), url):
        if result[i]["unsafe"] >= result[i]["safe"]:
            Res = {"url": u, "status": "unsafe"}
        else:
            Res = {"url": u, "status": "safe"}
        Result["Predictions"].append(Res)
    return Result


def url_to_path(url):
    opener = urllib.request.build_opener()
    opener.addheaders = [
        ('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5')]
    urllib.request.install_opener(opener)
    name = 0
    try:
        for u in url:
            ext = u.split(".")
            path = "Temp/" + str(name) + "." + ext[-1]
            urllib.request.urlretrieve(u, path)
            name += 1
    except urllib.error.HTTPError as e:
        result = {'error_code': e.code, 'error_reason': e.reason}
    except urllib.error.URLError as e:
        result = {'error_code': 500, 'error_reason': str(e.reasson)}
    except Exception as e:
        result = {'error_code': 500, 'error_reason1': e.args}

    arr = os.listdir("Temp/")
    return arr


def classify(image):
    # Classify.
    classifier = NudeClassifier()
    Result = classifier.classify(image)
    K.clear_session()
    shutil.rmtree('Temp')
    os.makedirs('Temp')
    return Result


if __name__ == '__main__':
    if not os.path.exists('Temp'):
        os.mkdir('Temp')
    app.run()
