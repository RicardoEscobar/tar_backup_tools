"""
main file for the application
"""
from threading import Thread

from archiver import Archiver


def progress(current, bytes, total):
    print(f"Progress: {current}/{total}")

def completed(total, elapsed):
    print(f"Completed: {total} files in {elapsed:.2f} seconds")


def main():
    source = "data"
    destination = "archive.tar"

    archiver = Archiver(source, destination, progress, completed)
    archiver.archive()


if __name__ == "__main__":
    main()
