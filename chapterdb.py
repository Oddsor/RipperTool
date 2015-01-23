import requests
import xmltodict


def __chapter_get(title=None, chapter_id=None):
    headers = {"ApiKey": "TE4Y0Q8CQBA0GIAI88ML"}
    if title is not None:
        response = requests.get("http://www.chapterdb.org/chapters/search?title=" + title, headers=headers)
    else:
        response = requests.get("http://www.chapterdb.org/chapters/" + str(chapter_id), headers=headers)
    result = xmltodict.parse(response.text)

    if 'results' in result:
        iteration = result.get('results').get('chapterInfo')
    else:
        iteration = list()
        iteration.append(result.get('chapterInfo'))
    data = list()
    for dataset in iteration:
        datadict = dict()
        datadict['votes'] = dataset.get('@confirmations')
        datadict['type'] = dataset.get('source').get('type')
        datadict['title'] = dataset.get('title')
        datadict['duration'] = dataset.get('source').get('duration')
        chaplist = list()
        for chapter in dataset.get('chapters').get('chapter'):
            chaplist.append(chapter.get('@name').replace(',', '\,'))
                            
        datadict['chapters'] = chaplist
        if len(iteration) == 1:
            return datadict
        else: 
            data.append(datadict)

    return data


def get_chapters(chapter_id):
    return __chapter_get(None, chapter_id)


def search_chapters(name):
    return __chapter_get(name, None)

import tempfile


def get_temp_csv(csv_string):
    file_path = tempfile.mktemp('.csv', 'chapter')
    file = open(file_path, 'w+')
    file.write(csv_string)
    file.close()
    return file_path


def make_csv(data):
    data_string = ""
    for i in range(0, len(data['chapters'])):
        data_string += str(i + 1) + "," + data['chapters'][i]
        if i - 1 < len(data['chapters']):
            data_string += "\n"
    return data_string
