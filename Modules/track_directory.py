from __future__ import print_function
from __future__ import division 

import sys, os
import hashlib
import json

import paramiko
import time, datetime


# DEFINE THE NAMES OF THE CHECKS
LAST_EDIT = "last_edit"
MD5HASH = "md5"
NAME = "name"
FULL_PATH = "full_path"
MOD_TIME = "last_time"
TYPE = "file_type"
DIR_CONTENT = "the_content"

MONTHS = {"Jan" : 1, "Feb":2, "Mar" : 3, "Apr":4, "May":5, "Jun": 6, "Jul": 7, "Aug": 8, "Sep":9, "Oct":10, "Nov":11, "Dec":12}

class Directory:

    def __init__(self):
        """
        DIRECTORY 
        =========

        This function identifies a shared directory.
        It can compile the list of files, with last edit data, and md5hash. 
        In this way it is possible to create a script that initializes the directory.
        """

        self.path = ""
        self.total_info = {}

        self.exclude_hidden_files = True
        

    def setup_new_directory(self, path):
        """
        Setup a new directory for the sync with the NAS.

        The provided directory must already exists in the disk
        """

        # Extract the total path of the directory
        total_path = os.path.abspath(path)
        self.path = total_path

        self.track_files() 

    def save_config(self, filename):
        """
        Save the JSON configuration file of the anaylsis of the directory
        """

        with open(filename, "w") as fp:
            json.dump(self.total_info, fp, sort_keys= True, indent = 4)                

    def load_config(self, filename):
        """
        Load the JSON configuration file of the analysis of the directory.
        """

        with open(filename, "r") as fp:
            self.total_info = json.load(fp)

    def track_files(self):
        """
        TRACK THE CHANGES
        =================

        This subroutine tracks all the non hidden files inside the directory
        and prepare a report for the files that have been changed since the last time this method was run.
        
        If no previous track was runned, than all the files will be added.
        """

        current_data = analyze_file(self.path)
        current_data[DIR_CONTENT] = self._track_files(self.path)

        self.total_info = current_data
    
    def _track_files(self, relative_path):
        """
        This is a working iterative method of track_files
        """

        all_files = os.listdir(relative_path)

        # Exclude the hidden files
        if self.exclude_hidden_files:
            all_files = [x for x in all_files if not x.startswith(".")]

        if len(all_files) == 0:
            return

        data_in_dir = []

        for fname in all_files:
            full_path = os.path.join(relative_path, fname)

            file_data = analyze_file(full_path)

            # Iterate
            if os.path.isdir(full_path):
                file_data[DIR_CONTENT] = self._track_files(full_path)    
            
            data_in_dir.append(file_data)
        
        return data_in_dir


class RemoteDirectory(Directory):

    def __init__(self):
        # Initialize the directory
        Directory.__init__(self)

        # Initialize specific remote controls
        self.hostname = ""
        self.username = ""
        self.pwd = ""
        self.port = 22
        self.busybox = True

        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.load_system_host_keys()

    def configure_connection(self, **kwargs):
        """
        Configure the SSH connection.
        Beside hostname, password and port, you can specify extra keyword arguments to be passed to the SSHClient
        """
        
        self.ssh_client.connect(self.hostname, username= self.username, port = self.port, password = self.pwd, **kwargs)

    def track_files(self, absolute_path):
        """
        Tracks the files.
        """

        previous_dir = os.path.join(*os.path.split(absolute_path)[:-1])
        dir_name = os.path.split(absolute_path)[-1]

        # Produce the original matrix
        print("Analyzing:", previous_dir)
        total_info = analyze_directory_ssh(self.ssh_client, previous_dir, busybox= self.busybox)

        print(total_info)

        index = -1
        self.total_info = {}
        for i, value in enumerate(total_info):
            if value[FULL_PATH] == absolute_path:
                self.total_info = value
                break 

        if len(self.total_info) == 0:
            raise ValueError("Error, something went wrong!")

        self.total_info = self._track_files(self.total_info)

    def _track_files(self, current_info):
        """
        Working method
        """

        if current_info[TYPE] == "file":
            return current_info

        # Analyze the files
        new_info_list = analyze_directory_ssh(self.ssh_client, current_info[FULL_PATH], busybox= self.busybox)

        dir_content = []
        for i in range(len(new_info_list)):
            dir_content.append(self._track_files(new_info_list[i]))
        
        current_info[DIR_CONTENT] = dir_content 

        return current_info





def analyze_file(path, get_md5 = True):
    """
    Provide the full dictionary that identifies the given file
    """

    if not os.path.exists(path):
        raise IOError("Error, the specified path '{}' does not exist".format(path))
    
    infofile = {}

    # Check if it is a directory
    if os.path.isdir(path):
        infofile[TYPE] = "directory"
    else:
        infofile[TYPE] = "file"
        
        # Get the md5hash
        if get_md5:
            md5_hash = hashlib.md5()
            fp = open(path, "rb")
            content = fp.read()
            fp.close()
            md5_hash.update(content)
            infofile[MD5HASH] = md5_hash.hexdigest()

        infofile[LAST_EDIT] = int(os.path.getmtime(path))


    # Get the file name
    path_split = os.path.split(path)
    infofile[NAME] = path_split[-1]
    
    # Get the absolute location
    abs_path = os.path.join(*path_split[:-1])
    infofile[FULL_PATH] = os.path.abspath(abs_path)


    return infofile


def analyze_directory_ssh(ssh_connect, path, pwd = None, busybox = False):
    """
    Get the info on the files through an ssh connection inside the directory.

    Parameters
    ----------
        ssh_connect: paramiko.SSHClient()
            A ssh client with the connection already opened.
        path: string
            The path to the directory in the server to be analyzed.
        pwd : string (or None)
            If a string, then the password is passed to the ssh command.
    
    Returns
        infodict : dict
            The dictionary with the analysis of the directory.
    """

    if not busybox:
        cmd = r"ls -l --time-style=+%s  " + path
    else:
        cmd = r"ls -l -e  " + path

    stdin, stdout, stderr = ssh_connect.exec_command(cmd)
    
    # Write the password
    if not pwd is None:
        stdin.write("{}\n".format(pwd))

    return analyze_with_ls(stdout.readlines(), stderr.readlines(), total_path = path, busybox= busybox)

def analyze_with_ls(stdout, stderr, total_path, busybox = False):
    """
    Analyze the output of 
    ls -l --time-style=+%s
    command from a unix shell

    Parameters
    ----------
        stdout : string
            The output that comes from a ls -lt command
        stderr : string
            The error that comes from a ls -lt command
        total_path : string
            The path of the directory that we are analyzing
        busybox : bool
            If true use the ls from busybox. In this case, it requires the ls -l -e options.
            This is usefull since some NAS have this limited version of ls that is not able
            to exploit the time-style option.
    
    Returns
    -------
        fileinfo : list
            The list of dictionaries with the files. Directories are just listed by names.
    """


    # TODO: Check if the directory exists, and it did not crashed    


    # Analyze the output
    all_components = []

    for line in stdout:
        line = line.strip()
        data = line.split()

        # Keep only good data
        if not busybox:
            if len(data != 7):
                continue 

        filedata = {}

        # Check if the line refers to a directory or a file
        if data[0][0] == "d":
            filedata[TYPE] = "directory"
        else:
            filedata[TYPE] = "file"
        
        try:
            # If busybox reshape the data
            if busybox:
                data[10] = " ".join(data[10:])
                data = data[:11]

            # Get the date
            if not busybox:
                filedata[LAST_EDIT] = int(data[-2])
            else:
                # Read the data with busybox
                year = int(data[-2])
                month = MONTHS[data[-5]]
                day = int(data[-4])
                hour = int(data[-3].split(":")[0])
                minute = int(data[-3].split(":")[1])
                second = int(data[-3].split(":")[2])

                date = datetime.datetime(year, month, day, hour, minute, second)
                filedata[LAST_EDIT] = int(date.timestamp())

            # Get the full path
            filedata[FULL_PATH] = os.path.join(total_path, data[-1])

            filedata[NAME] = data[-1]

            all_components.append(filedata)
        except:
            print("Unrecognized line:", line)
            raise

    return all_components

