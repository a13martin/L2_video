import subprocess
import os
import csv
import time


def trim(ipt, output, start, end):
    """
    this function trims de video inputted, needed for exercise 2
    :param ipt: video path (string)
    :param output: output video path
    :param start: start point to be cut (format 00:00:00)
    :param end: end point to be cut (format 00:00:00)
    :return: void, the trimmed video is created with ffmpeg in the desired path
    """
    if os.path.exists(output):
        os.remove(output)
    subprocess.call("ffmpeg -i " + ipt + " -ss " +
                    start + " -to " + end + " -c:v copy -c:a copy " + output)


class Ffmpeg:

    def __init__(self, video):
        self.video = video

    def parse(self):
        if os.path.exists("metadata.txt"):
            os.remove("metadata.txt")

        subprocess.call("ffmpeg -i " + self.video + " -f ffmetadata metadata.txt")
        # In the line above we created a .txt file with some metadata
        lines = [6, 7, 8]
        with open('metadata.txt', 'r') as f:
            print("Printing Genre, Artist and Title: ")
            for i, line in enumerate(f):
                if i in lines:
                    print(line.strip())  # Reading the .txt final lines and printing its content
                elif i > 8:  # Avoiding reading the file after line 8
                    break

    def new_container(self):
        if os.path.exists("new_bbb.mp4"):
            os.remove("new_bbb.mp4")
        if os.path.exists("new_container.mp4"):
            os.remove("new_container.mp4")

        vidd = "bbb_1min.mp4"
        trim(self.video, vidd, "00:00:00", "00:01:00")

        subprocess.call("ffmpeg -i " + vidd + " -f mp3 -ab 192000 -vn bbb_audio.mp3")  # Exporting the audio in mp3
        subprocess.call("ffmpeg -y -i " + vidd + " -map 0:a:0 bbb_aac.m4a")  # Encoding audio in m4a (aac)
        subprocess.call("ffmpeg -i bbb_1min.mp4 -i bbb_audio.mp3 -i bbb_aac.m4a "
                        "-map 0:v -c:v copy -map 1:a -c:a copy -map 2:a -c:a copy new_container.mp4")
        # We are concatenating the video with the both audios in a new container,
        # avoiding re-encoding by copying the encoding format.

    def resize(self, x, y):
        resolution = str(x) + ":" + str(y)
        print("Resizing " + self.video + " to " + resolution)

        if os.path.exists("bbb_" + str(x) + "x" + str(y) + ".mp4"):
            os.remove("bbb_" + str(x) + "x" + str(y) + ".mp4")

        subprocess.call("ffmpeg -i " + self.video + " -vf scale=" + resolution +
                        " bbb_" + str(x) + "x" + str(y) + ".mp4")

    def audio_check(self):
        subprocess.call("ffprobe -loglevel 0 -print_format csv -show_format -show_streams "
                        + self.video + " > meta.csv ")
        # We created a csv file with all the metadata needed to check whether the source is and audio,
        # and extract its format
        print("Waiting until the file is generated...")
        time.sleep(15)

        meta = csv.reader(open('meta.csv', 'r', encoding='utf16'), delimiter=',')  # Reading csv
        audio_formats = []
        for row in meta:
            if row[5] == 'audio':  # Checking if the file in the container is an audio
                audio_formats.append(row[2])  # Adding to a list the audio formats (mp3, aac, etc)
        standards = []                        # of the audio files in the container
        for fmt in audio_formats:  # Depending on the format, we append to the list the supported standards
            if fmt == 'mp3':
                print("This video contains audio in MP3 format")
                standards.extend(["DVB", "DTMB"])
            elif fmt == 'aac':
                print("This video contains audio in AAC format")
                standards.extend(["DVB", "ISDB", "DTMB"])
            elif fmt == 'ac3':
                print("This video contains audio in AC-3 format")
                standards.extend(["DVB", "ATSC", "DTMB"])
            elif fmt == 'mp2':
                print("This video contains audio in MP2 format")
                standards.append("DTMB")
        standards = list(dict.fromkeys(standards))  # Removing duplicate standards in the list
        print("This video can fit in the following broadcast standard(s): ")
        for i in standards:
            print(i)


if __name__ == '__main__':
    vid = "bbb_short.mp4"
    bbb = Ffmpeg(vid)
    print("Type 1 for exercise 1 \nType 2 for exercise 2 \nType 3 for exercise 3 \n"
          "Type 4 for exercise 4 \nType 0 to exit")
    opt = int(input("Enter the exercise: "))

    match opt:
        case 1:
            bbb.parse()
        case 2:
            bbb.new_container()
        case 3:
            width = int(input("Enter the width of the video (X): "))
            height = int(input("Enter the height of the video (Y): "))
            bbb.resize(width, height)
        case 4:
            bbb.audio_check()
        case 0:
            print("Exiting...")
            pass
        case other:
            print("ERROR: Invalid option")
            print("Exiting...")
