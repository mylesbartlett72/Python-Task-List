# Python Task List

A task list application, written in Python3 using the dearpygui library

## Installation from source

It is suggested that a virtual environment is used, although this is not required.

To install dependencies, run
```shell
spam@eggs:~$ pip3 install -r /path/to/the/cloned/repository/requirements.txt
```
NOTE: You may need to substitute `pip3` for `pip` on Windows-based systems.  To use a specific version of python from your system: `/path/to/your/python -m pip` can be used instead of `pip3`

## To start
Run
```shell
spam@eggs:~$ cd /path/to/the/cloned/repository
spam@eggs:~$ /path/to/your/python src/task_list/__main__.py
```

In this case, data is stored in .tasks.json in the root of the cloned repository.  .tasks.json will be searched for and written to the current working directory.

## Building packages
Run
```shell
spam@eggs:~$ cd /path/to/the/cloned/repository
spam@eggs:~$ /path/to/your/python -m build .
```
Built packages will be output to the dist directory.
