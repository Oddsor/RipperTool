from OddTools import oddconfig

__author__ = 'Odd'

import re
import os

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


def run_encode(drive, track, output, audio_tracks, subtitles, optimization=None):
    cli_path = oddconfig.get_setting("handbrakecli_path")
    if True:
        audio_tracks_string = "-a " + ",".join(map(str, audio_tracks))
        audio_encode_string = " -E " + ",".join(map(str, ['av_aac']*len(audio_tracks)))
        audio_channels_string = " -6 " + ",".join(map(str, ['dpl2']*len(audio_tracks)))
        audio_bitrate_string = " -B " + ",".join(map(str, ['320']*len(audio_tracks)))

        #TODO make audio tracks and subtitles pass into run_encode as dict containing title, codec, bitrate, etc
        #audio_tracks_string = "-a " + ",".join(map(str, [x['track'] for x in audio_tracks]))
        #audio_encode_string = " -E " + ",".join(map(str, [x['codec'] for x in audio_tracks]))
        #audio_bitrate_string = " -B " + ",".join(map(str, [x['bitrate'] for x in audio_tracks]))

        subtitle_string = " --subtitle " + ",".join(map(str, subtitles))
        print('"a path" -i ' + drive + " -t " + str(track) +
                                    ' --angle 1 -o "' + output + '" -f mkv --loose-anamorphic'
                                    + ' --modulus 2 -e x264 -q 20 --vfr ' + audio_tracks_string + audio_bitrate_string +
                                   ' --audio-fallback ac3 ' + subtitle_string +
                                   ' --markers="C:/Users/Odd/AppData/Local/Temp/' + os.path.splitext(os.path.basename(output))[0] +
                                   '.csv --encoder-preset=veryfast   --encoder-level="5.2"  --encoder-profile=high  --verbose=1')

        process = subprocess.Popen('"' + oddconfig.get_setting("handbrakecli_path") +
                                '" -i ' + drive + " -t " + str(track) +
                                ' --angle 1 -o "' + output + '" -f mkv --loose-anamorphic'
                                + ' --modulus 2 -e x264 -q 20 --vfr ' + audio_tracks_string + audio_bitrate_string +
                                ' --audio-fallback ac3 ' + subtitle_string +
                                ' --markers="C:/Users/Odd/AppData/Local/Temp/' +
                                os.path.splitext(os.path.basename(output))[0] +
                                '.csv --encoder-preset=veryfast   --encoder-level="5.2"' +
                                '  --encoder-profile=high  --verbose=1',
                                stdout=subprocess.PIPE, universal_newlines=True)
        while process.poll() != 0:
            out = process.communicate()
            print(out)



if __name__ == '__main__':
    print(parse_handbrake(open("handbrake_example.txt").read()))
    print(parse_handbrake(open("handbrake_example2.txt").read()))
    import doctest
    doctest.testmod()