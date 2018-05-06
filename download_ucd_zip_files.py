#!/usr/bin/env python3

import ftplib
import os
import sys
import zipfile


FTP_SERVER = "ftp.unicode.org"
REMOTE_PATH = "/Public/UCD/latest/ucd/"


def main():
    with ftplib.FTP(FTP_SERVER) as ftp:
        ftp.login()  # Anonymous login
        ftp.cwd(REMOTE_PATH)
        for zip_filename in [filename for filename in ftp.nlst() if filename.lower().endswith("zip")]:
            block_size = 4096
            with open(zip_filename, "wb") as dest_file_obj:
                print("Starting download: {0}".format(zip_filename))
                ftp.retrbinary("RETR " + zip_filename, dest_file_obj.write, block_size)
                print("Finished downloading: {0}".format(zip_filename))
            print("Testing zip file: {0}".format(zip_filename))
            test_result = zipfile.is_zipfile(zip_filename)
            if not test_result:
                print("Error, invalid zip file: {0}".format(zip_filename))
                print("Exiting...")
                sys.exit(1)
            zip_file = zipfile.ZipFile(zip_filename)
            test_result = zip_file.testzip()
            if test_result:
                print("Error, the following entry is corrupt: {0}".format(test_result))
                print("Exiting...")
                sys.exit(1)
            else:
                print("Successfully tested zip file: {0}".format(zip_filename) + os.linesep)


if __name__ == "__main__":
    main()
