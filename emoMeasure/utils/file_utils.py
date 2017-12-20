from os import path, makedirs
import glob


def get_directory_name(file_name):
    return path.dirname(file_name)


def make_directory(dir_name, folder_path):
    """
    Creates a directory in the given folder
    :param dir_name: name of the new folder
    :param folder_path: path of the new folder
    :returns full path of the newly created directory
    """
    directory = path.join(folder_path, dir_name)

    if path.exists(directory):
        return

    makedirs(directory)

    return directory


def get_file_names(directory_path, extension="*", recursive=False):
    """
    Gets all files in a given directory that matches an optional extension
    :param directory_path: Path of the directory
    :param extension: Desired extension
    :param recursive: Shall we do it recursively? (may take time)
    :returns file list matching the above options
    """
    if extension == "*":
        path_list = glob.glob(path.join(directory_path, "*"), recursive=recursive)
    else:
        path_list = glob.glob(path.join(directory_path, "*." + extension), recursive=recursive)

    return filter(lambda x: path.isfile(x), path_list)


def get_file_name(file_path):
    """
    Rturns the file name of the supplied path without extension
    ex: '/root/dir/sub/toto.ext' returns 'toto'
    :param file_path: path of the target file
    """
    basename = path.basename(file_path)
    return path.splitext(basename)[0]


def create_file_path(file_name, directory_path, extension=".txt"):
    return path.join(directory_path, (file_name + extension))
