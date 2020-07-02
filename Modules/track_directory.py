from __future__ import print_function
from __future__ import division 

import sys, os
import hashlib
import json

import time, datetime


# DEFINE THE NAMES OF THE CHECKS
LAST_EDIT = "last_edit"
MD5HASH = "md5"
NAME = "name"
FULL_PATH = "full_path"
MOD_TIME = "last_time"
TYPE = "file_type"
DIR_CONTENT = "the_content"

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


def analyze_directory_ssh(ssh_connect, path, pwd = None):
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

    stdin, stdout, stderr = ssh_connect.exec_command(r"ls -l --time-style=+%s  " + path)
    
    # Write the password
    if not pwd is None:
        stdin.write("{}\n".format(pwd))

    return analyze_with_ls(stdout, stderr, total_path = path)

def analyze_with_ls(stdout, stderr, total_path):
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
    
    Returns
    -------
        fileinfo : list
            The list of dictionaries with the files. Directories are just listed by names.
    """


    # TODO: Check if the directory exists, and it did not crashed    


    # Analyze the output
    lines = stdout.split("\n")
    
    all_components = []

    for line in lines:
        data = line.split()

        # Keep only good data
        if len(data != 7):
            continue 

        filedata = {}

        # Check if the line refers to a directory or a file
        if data[0][0] == "d":
            filedata[TYPE] = "directory"
        else:
            filedata[TYPE] = "file"
        
        try:
            # Get the date
            filedata[LAST_EDIT] = int(data+[-2])

            # Get the full path
            filedata[FULL_PATH] = total_path

            filedata[NAME] = data[-1]

            all_components.append(filedata)
        except:
            print("Unrecognized line:", line)
            raise ValueError("Error while parsing ls output.")

    return all_components