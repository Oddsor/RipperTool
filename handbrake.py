from OddTools import oddconfig

__author__ = 'Odd'

import re


def parse_handbrake(output):
    tracks = list()
    output_split = output.splitlines()
    line = None if not output_split else output_split.pop(0)
    while line is not None:
        if line.startswith('+ title'):
            track_info = dict()
            track_info['track_number'] = re.search("[0-9]{1,3}", line).group(0)
            line = None if not output_split else output_split.pop(0)
            while line is not None and not line.startswith("+ title"):
                if "+ Main Feature" in line:
                    track_info['main_feature'] = True
                if "+ duration" in line:
                    track_info['duration'] = \
                        re.search("[0-9]{1,2}:[0-9]{2}:[0-9]{2}", line).group(0)
                    line = None if not output_split else output_split.pop(0)
                elif "audio tracks" in line:
                    audio = list()
                    line = None if not output_split else output_split.pop(0)
                    while line is not None and re.search("\+ \d{1,2}", line) is not None:
                        audio.append(re.search("(?<=\d\,\s)\w+\s\(.*?\)\s\(.*?\)", line).group(0))
                        line = None if not output_split else output_split.pop(0)
                    track_info["audio"] = audio
                elif "subtitle tracks" in line:
                    subtitles = list()
                    line = None if not output_split else output_split.pop(0)
                    while line is not None and re.search("\+ \d{1,2}", line) is not None:
                        subtitles.append(re.search("(?<=\d\,\s)\w+", line).group(0))
                        line = None if not output_split else output_split.pop(0)
                    track_info["subtitles"] = subtitles
                else:
                    line = None if not output_split else output_split.pop(0)

            tracks.append(track_info)
        else:
            line = None if not output_split else output_split.pop(0)
    return tracks

def consolidate_languages(list_of_lists):
    '''

    >>> consolidate_languages([['Eng', 'Nor'], ['Eng', 'Nor', 'Eng', 'Eng2'], ['Eng', 'Nor']])
    [(1, 'Eng'), (1, 'Nor'), (0, 'Eng'), (0, 'Eng2')]
    >>> consolidate_languages([['Eng', 'Nor'], ['Eng', 'Nor'], ['Eng', 'Eng', 'Nor']])
    [(1, 'Eng'), (0, 'Eng'), (1, 'Nor')]

    :param list_of_lists:
    :return:
    '''
    if len(list_of_lists) == 0:
        return list()
    output_list = list()
    #Populate first
    for item in list_of_lists[0]:
        output_list.append((1, item))

    for i in range(1, len(list_of_lists)):
        output_index = 0
        data_index = 0
        while output_index != len(output_list) and data_index != len(list_of_lists[i]):
            if output_list[output_index][1] != list_of_lists[i][data_index]:
                if len(output_list) < len(list_of_lists[i]):
                    output_list.insert(output_index, (0, list_of_lists[i][data_index]))
                    output_index += 1
                    data_index += 1
                else:
                    output_list[output_index][0] = 0
                    output_index += 1
            else:
                output_index += 1
                data_index += 1
        data_index = len(output_list)
        while len(output_list) < len(list_of_lists[i]):
            output_list.append((0, list_of_lists[i][data_index]))
            data_index += 1

    return output_list

import subprocess


def run_encode(drive, track, output, animation):
    cli_path = oddconfig.get_setting("handbrakecli_path")
    if cli_path is not None:
        process = subprocess.Popen('"' + oddconfig.get_setting("handbrakecli_path") +
                                    '" -i ' + drive + " -t " + str(track) +
                                    ' --angle 1 -o "' + output + '" -f mkv --loose-anamorphic'
                                    + ' --modulus 2 -e x264 -q 20 --vfr -a 1,2,4 -E av_aac,av_aac,av_aac -6 5point1,5point1,none -R Auto,48,48 -B 384,384,160 -D 0,0,0 --gain 0,0,0 --audio-fallback ac3 --subtitle 1 --markers="C:/Users/Odd/AppData/Local/Temp/Korra - Change 1-13-chapters.csv" --encoder-preset=veryfast  --encoder-tune="animation"  --encoder-level="5.2"  --encoder-profile=high  --verbose=1',
                         stdout=subprocess.PIPE, universal_newlines=True)
        while process.poll() != 0:
            out = process.communicate()
            print(out)

        #return subprocess.getoutput('"' + oddconfig.get_setting("handbrakecli_path") + '" -i ' + input + " -t " + str(track) +
        #                            ' --angle 1 -c 1-5 -o "' + output + '" -f mkv  -w 1920 --crop 0:0:0:0 --loose-anamorphic'
        #                            + ' --modulus 2 -e x264 -q 20 --vfr -a 1,2,4 -E av_aac,av_aac,av_aac -6 5point1,5point1,none -R Auto,48,48 -B 384,384,160 -D 0,0,0 --gain 0,0,0 --audio-fallback ac3 --subtitle 1 --markers="C:/Users/Odd/AppData/Local/Temp/Korra - Change 1-13-chapters.csv" --encoder-preset=veryfast  --encoder-tune="animation"  --encoder-level="5.2"  --encoder-profile=high  --verbose=1')

if __name__ == '__main__':
    print(parse_handbrake(open("handbrake_example.txt").read()))
    print(parse_handbrake(open("handbrake_example2.txt").read()))
    #print(run_encode("D:\\", 14, "F:\Video\Korra - Change 2.mkv", 0))
    import doctest
    doctest.testmod()