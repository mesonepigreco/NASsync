import sys, os
import NASsync
import NASsync.track_directory as td 


def test_analisys():
    total_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(total_path)

    # Analyze this directory
    Dir = td.Directory()
    Dir.setup_new_directory("..")

    # Save the json
    Dir.save_config("this_project.json")

if __name__ == "__main__":
    test_analisys()