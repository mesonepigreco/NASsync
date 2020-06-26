from __future__ import print_function
from __future__ import division 

import sys, os
import md5hash


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
        

    def setup_new_directory(self, path):
        """
        Setup a new directory for the sync with the NAS.

        The provided directory must already exists in the disk
        """

        # Extract the total path of the directory
        total_path = os.path.abspath(path)
        self.path = total_path

        self.track_files() 

    def track_files(self):
        """
        TRACK THE CHANGES
        =================

        This subroutine tracks all the non hidden files inside the directory
        and prepare a report for the files that have been changed since the last time this method was run.
        
        If no previous track was runned, than all the files will be added.
        """

        pass 
    
    def _track_files(self, relative_path):
        """
        This is a working iterative method of track_files
        """

        all_files = os.listdir(relative_path)

        if len(all_files) == 0:
            return

        for fname in all_files:
            full_path = os.path.join(relative_path, fname)

            # TODO: Here perform the sync

            # Iterate
            if os.path.isdir(full_path):
                self._track_files(full_path)    
        

