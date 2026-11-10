"""Remove everything the lab created.

Run from the lab folder:  python tests/cleanup_lab.py
It deletes starter/release-day/ and starter/origin.git/ (including any file you
added there) and the Python cache in tests/. It touches nothing outside this lab folder.
"""

from lab_support import reset_starter, restore_starter_files


def main():
    reset_starter()
    restore_starter_files()
    print("Lab cleaned: the lab repository, its local remote and your local work are removed.")
    print("The shipped starter files are restored. Run python tests/setup_lab.py to start again.")


if __name__ == "__main__":
    main()
