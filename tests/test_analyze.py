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

def test_remote_analysis():
    total_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(total_path)

    RemoteDir = td.RemoteDirectory()
    RemoteDir.hostname = "192.168.1.102"
    RemoteDir.username = "sshd"
    RemoteDir.configure_connection()

    RemoteDir.track_files("/mnt/HD/HD_a2/Public/Lorenzo/Simulations/COVID/COVID/quarantine")

    RemoteDir.save_config("remote_dir.json")

if __name__ == "__main__":
    test_analisys()
    test_remote_analysis()