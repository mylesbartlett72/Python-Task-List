# Python Task List

A task list application, written in Python3 using the dearpygui library

## Installing as a binary (PyPI)

NOTE: While binary packages should work, the dependency management has not been tested!  Please file an issue report if you encounter problems.

Run
```shell
spam@eggs:~$ pip3 install dearpygui-task-list
```
NOTE: You may need to substitute `pip3` for `pip` on Windows-based systems.  To use a specific version of python from your system: `/path/to/your/python -m pip` can be used instead of `pip3`

## Installing as a binary (downloaded)

NOTE: While binary packages should work, the dependency management has not been tested!  Please file an issue report if you encounter problems.

Run
```shell
spam@eggs:~$ pip3 install /path/to/the/downloaded/wheel.whl
```
NOTE: You may need to substitute `pip3` for `pip` on Windows-based systems.  To use a specific version of python from your system: `/path/to/your/python -m pip` can be used instead of `pip3`

### To start (installation as a binary) (any binary source)
Run
```shell
spam@eggs:~$ /path/to/your/python -m task_list
```
.tasks.json will be searched for and written to the current working directory.

## Installation from source

It is suggested that a virtual environment is used, although this is not required.

To install dependencies, run
```shell
spam@eggs:~$ pip3 install -r /path/to/the/cloned/repository/requirements.txt
```
NOTE: You may need to substitute `pip3` for `pip` on Windows-based systems.  To use a specific version of python from your system: `/path/to/your/python -m pip` can be used instead of `pip3`

### To start (installation from source)
Run
```shell
spam@eggs:~$ cd /path/to/the/cloned/repository
spam@eggs:~$ /path/to/your/python src/task_list/__main__.py
```

In this case, data is stored in .tasks.json in the root of the cloned repository.  .tasks.json will be searched for and written to the current working directory.

## Building packages from source
Run
```shell
spam@eggs:~$ cd /path/to/the/cloned/repository
spam@eggs:~$ /path/to/your/python -m build .
```
Built packages will be output to the dist directory.
