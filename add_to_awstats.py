from datetime import timedelta
import os

__author__ = 'avbelkum'

from dateutil import parser


def create_log(date_string):
    cmd = "/usr/share/awstats/tools/logresolvemerge.pl /home/ubuntu/log/video/videoEFQ1SZJSIIMGH.%s.*.gz >> /home/ubuntu/log/video.log" % date_string
    print cmd
    os.system(cmd)


def run_awstat():
    os.system("sudo /usr/lib/cgi-bin/awstats.pl --config=video.kookse.tv -showdropped")


def remove_files(date_string):
    os.system("rm -f /home/ubuntu/log/video/videoEFQ1SZJSIIMGH.%s.*.gz" % date_string)


def clear():
    os.system("rm -f /home/ubuntu/log/video.log")
    pass


def main():
    start = "2014-02-10 14:00"
    end = "2014-03-10 15:00"
    end_date = parser.parse(end)
    date = parser.parse(start)

    clear()
    while date < end_date:
        date_string = date.strftime("%Y-%m-%d-%H")
        create_log(date_string)
        remove_files(date_string)
        prev = date
        date += timedelta(hours=1)
        if date.day != prev.day:
            print "next day"
            run_awstat()
            clear()


if __name__ == "__main__":
    main()
