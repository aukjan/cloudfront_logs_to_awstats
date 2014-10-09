import gzip
import os
import re
from boto.s3.key import Key
from StringIO import StringIO

__author__ = 'Aukjan van Belkum'
__version__ = "0.0.1"
__date__ = "01 Oct 2014"

import getopt
import sys
import boto


class AwstatsLog:
		# And yes, not very user friendly
    AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']

    def __init__(self, log_base='logfile', bucket_name=None, prefix=None, delete=False):
        self.delete = delete
        self.log_base = log_base
        self.s3_conn = None
        self.bucket_list = None
        self.bucket_name = bucket_name
        self.prefix = prefix
        self.init()

    def init(self):
        print "Initializing"
        if not self.prefix or not self.bucket_name:
            print "Not all parameters set,..."
            sys.exit(1)

        self.s3_conn = boto.connect_s3(self.AWS_ACCESS_KEY_ID, self.AWS_SECRET_ACCESS_KEY)
        bucket = self.s3_conn.get_bucket(self.bucket_name)
        self.bucket_list = bucket.list(self.prefix)

    def get_file_data(self, key_list):
        data = key_list.get_contents_as_string()
        return data

    def append_to_log(self, key_list, logfile, name):
        print "Appending %s" % name
        try:
            # Get unzipped data
            #  read gz => unzip => append to zip
            data = gzip.GzipFile(fileobj=StringIO(self.get_file_data(key_list)))

            # And append to gzipped file
            print "writing to %s" % logfile
            with gzip.open(logfile, 'ab') as destination:
                destination.write(data.read())

            if self.delete:
                self.remote_delete(key_list)

        except Exception as e:
            print "Failed to download: %s, because: %s" % (name, e.message)
            sys.exit(1)

    def create_logfiles(self):
        print "Creating logfiles"
        for key_list in self.bucket_list:
            assert isinstance(key_list,Key)
            name = self.filename_from_key(key_list.key)
            logfile = self.logfile_from_name(name)
            self.append_to_log(key_list, logfile, name)


    def filename_from_key(self, key):
        return str(key).split('/')[-1]

    def remote_delete(self, key_list):
        key_list.delete()
        if _debug:
            print "Deleted from bucket:    " + filename

    def logfile_from_name(self, name):
        """
        Name is in format: videoEFQ1SZJSIIMGH.2014-03-05-08.nLJVWYaD.gz
        and we'll need '2014-03-08'
        """
        p = re.compile('\.(\d+-\d+-\d+)-')
        return "%s-%s.log.gz" % (self.log_base, p.findall(name)[0])


def usage():
    print __doc__


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hb:p:l:d", ["help", "bucket=", "prefix=", "logbase=", "debug"])
    except getopt.GetoptError as e:
        print e.message
        usage()
        sys.exit(2)

    args = {}
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt == '-d':
            global _debug
            _debug = 1
        elif opt in ("-b", "--bucket"):
            args['bucket_name'] = arg
        elif opt in ("-p", "--prefix"):
            args['prefix'] = arg
        elif opt in ("-l", "--log_base"):
            args['log_base'] = arg

    print "Starting with: %s" % args
    logs = AwstatsLog(**args)
    logs.create_logfiles()


if __name__ == "__main__":
    main(sys.argv[1:])
