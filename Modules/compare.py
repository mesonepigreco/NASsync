import NASsync.track_directory as track_directory

import numpy as np
import sys, os


def get_sync_operation(source, dest):
    """
    GET THE SYNC OPERATION
    ======================

    By comparing the two dictionary of the file tree of source and dest, 
    this function identifies the files in source that needs to be copied into dest for a complete sync.
    The files are identified by the last modified date

    Parameters
    ----------
        source : dict
            The tree of the source directory
        dest : dict
            The tree of the destination directory

    Resuts
    ------
        update_files : list
            A list of truples [(source_file, destination, type), ...].
            For each element, the source_file is the file in the source database, destination is
            the path into the destination that needs to be updated. Type is the type of the operation.
            N is for new file, M is for a modified file and D is for a deleated file (in this case source_file is Null)

    """
    pass
