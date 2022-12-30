"""Module handling GUI.

This is not supposed to be imported

This module does not take any arguments.
"""

# NOTICE TO MAINTAINERS
# PLEASE PUT '# noqa: E501' (w/o quotes) AT THE END OF DOCSTRINGS
# (on same line as terminating ''')
# THIS PREVENTS FLAKE8 FROM DEMANDING DOCSTRINGS TO BE FORMATTED BADLY

# prevent the program from doing anything if it is imported
# (either accidentally or on purpose)
if __name__ == "__main__":
    import sys

    import dearpygui.dearpygui as dpg

    try:
        # only works if running from source
        import storage_api

    except ModuleNotFoundError:
        # running from python -m with installed wheel
        import task_list.storage_api as storage_api

    dpg.create_context()

    def add_new_task(
        list_name: str,
        tasks: dict,
        title: str,
        desc: str,
        create_task_window: any = None,
        primary_window: any = None,
        # todo: update legacy code so that the defaults of the next two parameters do
        # not have to be mutually incompatible
        handle_window_mgmt: bool = True,
        handle_storage_mgmt: bool = True,
    ):  # copy new arguemnts to delete task and potentially use in task update
        """Add a new task to the task list.

        Arguments:
            list_name -- The name of the list to add a task to
            tasks -- The task data as a python object
            title -- Task title
            desc -- Task description

        Keyword Arguments:
            create_task_window -- dearpygui object tag for the task create/edit window, which is autodeleted by the function if handle_window_mgmt is True (default: {None})
            primary_window -- dearpygui object tag for primary window (tasks window) which is set up again (default: {None})
            handle_window_mgmt -- Automatically delete create_task_window and primary_window.  If this is to be done, their dearpygui tags must be passed to the function. (default: {True})

        Raises:
            ValueError: If incompatible arguments are passed.  WARNING: DEFAULT ARGUMENTS ARE CURRENTLY INCOMPATIBLE

        Returns:
            tasks (if not handling storage management) -- the Python object containing the task list (read from a file using storage_api.py abstractions)
                A dictionary of lists, each key is the name of the column.  Currently hardcoded to use columns "To Do", "In Progress", and "Done".
        """  # noqa: E501
        tasks[list_name].append({"task_name": title, "task_desc": desc})
        if handle_storage_mgmt:
            storage_api.write_data(tasks)
        if handle_window_mgmt:
            if primary_window is None or create_task_window is None:
                raise ValueError(
                    "Tried to handle window management, but failed to pass a window!"
                )
            dpg.delete_item(create_task_window)
            dpg.delete_item(primary_window)
            # turns out this doesnt cause infinite recursion since setup_tasks_window
            # exits - the callbacks are dealt with on a separate thread
            setup_tasks_window(tasks)
        # moved to allow handling window management but not storage management.
        if not handle_storage_mgmt:
            return tasks

    def create_new_task_window(list_name: str, tasks: dict, primary_window: any):
        """Create an "add task" window.

        Arguments:
            list_name -- Name of task list (hardcoded to one of "To Do", "In Progress", "Done" elsewhere)
            tasks -- Python object of tasks
            primary_window -- dearpygui object tag for primary window (used by callbacks to automatically recreate to allow updating)
        """  # noqa: E501
        with dpg.window(label=f"Create a Task in {list_name}") as create_task_window:
            title = dpg.add_input_text(label="Task Title")
            content = dpg.add_input_text(label="Task content", multiline=True)
            dpg.add_spacer()
            dpg.add_text(f"This task will be created in the {list_name} list.")
            with dpg.table(header_row=False):
                dpg.add_table_column()
                dpg.add_table_column()
                with dpg.table_row():
                    dpg.add_button(
                        label="Create New Task",
                        callback=lambda: add_new_task(
                            list_name,
                            tasks,
                            dpg.get_value(title),
                            dpg.get_value(content),
                            create_task_window,
                            primary_window,
                        ),
                    )
                    dpg.add_button(
                        label="Cancel",
                        callback=lambda: dpg.delete_item(create_task_window),
                    )

    def edit_task(
        col: str,
        row: int,
        task_name: str,
        task_content: str,
        element_to_delete: any,
        tasks: dict,
        primary_window: any,
    ):
        """Edit an existing task.

        Arguments:
            col -- The column name of the task to edit
            row -- The row of the task to edit
            task_name -- New name of task
            task_content -- New task content
            element_to_delete -- A dearpygui object tag for a dearpygui element to be removed (i.e. the task edit window)
            tasks -- Python object of tasks
            primary_window -- A dearpygui object tag for the primary window (which is removed and regenerated)
        """  # noqa: E501
        dpg.delete_item(element_to_delete)
        tasks[col][row] = {"task_name": task_name, "task_desc": task_content}
        storage_api.write_data(tasks)
        dpg.delete_item(primary_window)
        setup_tasks_window(
            tasks
        )  # see above for why this does not cause overflow on stack

    def delete_task(
        col: str, row: int, edit_task_window: any, tasks: dict, primary_window: any
    ):
        """Delete a task.

        Arguments:
            col -- Column of task
            row -- Row of task
            edit_task_window -- Window created when clicking on a task title as dearpygui object tag (object with this tag deleted)
            tasks -- Python object of task list file
            primary_window -- Primary window as dearpygui object tag (object with this tag deleted, primary window auto recreated)
        """  # noqa: E501
        dpg.delete_item(edit_task_window)
        tasks[col].pop(row)
        storage_api.write_data(tasks)
        dpg.delete_item(primary_window)
        setup_tasks_window(tasks)

    def move_task(
        col: str,
        row: int,
        task_name: str,
        task_content: str,
        task_window: any,
        task_list: dict,
        primary_window: any,
        direction: bool = False,
    ):
        """Move a task a column left or right.

        Arguments:
            col -- Initial column of task, can be one of ["To Do", "In Progress", "Done"]
            row -- Row of initial task
            task_name -- Name of task
            task_content -- Content (i.e. description or details) of task
            task_window -- Task window as dearpygui object tag.  Deleted automatically.
            task_list -- Task list file as python object.
            primary_window -- The primary window as a dearpygui object tag.  Deleted and automatically recreated.

        Keyword Arguments:
            direction -- False: column left, True: column right.  Only checked if col is "In Progress" (default: {False})
        """  # noqa: E501
        if col == "To Do":
            add_new_task(
                "In Progress",
                task_list,
                task_name,
                task_content,
                handle_storage_mgmt=False,
                handle_window_mgmt=False,
            )
        elif col == "In Progress" and direction:
            add_new_task(
                "Done",
                task_list,
                task_name,
                task_content,
                handle_storage_mgmt=False,
                handle_window_mgmt=False,
            )
        elif col == "In Progress" and not direction:
            add_new_task(
                "To Do",
                task_list,
                task_name,
                task_content,
                handle_storage_mgmt=False,
                handle_window_mgmt=False,
            )
        else:
            add_new_task(
                "In Progress",
                task_list,
                task_name,
                task_content,
                handle_storage_mgmt=False,
                handle_window_mgmt=False,
            )
        delete_task(col, row, task_window, task_list, primary_window)

    def create_task_dialog_window(
        col: str,
        row: int,
        task_name: str,
        task_content: str,
        # should use better nomenclature or however you spell it anyway
        task_list: dict,
        primary_window: any,
    ):
        """Create the dialog window for a task (created when a task is clicked on).

        Arguments:
            col -- Column of the task
            row -- Row of the task
            task_name -- Current task name
            task_content -- Current task description
            task_list -- The Python object containing the task list (read from a file using storage_api.py abstractions)
            primary_window -- The dearpygui object tag of the primary window
        """  # noqa: E501
        with dpg.window(
            label=col + "#" + str(row) + " - " + task_name, min_size=(300, 264)
        ) as edit_task_window:
            # not debug
            title = dpg.add_input_text(label="Task Title", default_value=task_name)
            content = dpg.add_input_text(
                label="Task content", multiline=True, default_value=task_content
            )
            with dpg.table(header_row=False):
                dpg.add_table_column()
                dpg.add_table_column()
                dpg.add_table_column()
                with dpg.table_row():
                    dpg.add_button(
                        label="Update Task",
                        callback=lambda: edit_task(
                            col,
                            row,
                            dpg.get_value(title),
                            dpg.get_value(content),
                            edit_task_window,
                            task_list,
                            primary_window,
                        ),
                    )
                    dpg.add_button(
                        label="Delete Task",
                        callback=lambda: delete_task(
                            col, row, edit_task_window, task_list, primary_window
                        ),
                    )
                    dpg.add_button(
                        label="Cancel",
                        callback=lambda: dpg.delete_item(edit_task_window),
                    )
                with dpg.table_row():
                    # while arrows do not look the nicest, dearpygui does not provide
                    # any way to pass unicode strings that I know of
                    if col == "To Do":
                        # cannot move task left as there is no column on the left
                        dpg.add_spacer()
                    else:
                        dpg.add_button(
                            arrow=True,
                            callback=lambda: move_task(
                                col,
                                row,
                                dpg.get_value(title),
                                dpg.get_value(content),
                                edit_task_window,
                                task_list,
                                primary_window,
                            ),
                        )
                    # fills the column in the middle
                    dpg.add_text("Move")
                    if col == "Done":
                        # cannot move task right as there is no column on the right
                        dpg.add_spacer()
                    else:
                        dpg.add_button(
                            arrow=True,
                            direction=1,
                            callback=lambda: move_task(
                                col,
                                row,
                                dpg.get_value(title),
                                dpg.get_value(content),
                                edit_task_window,
                                task_list,
                                primary_window,
                                True,
                            ),
                        )

    def create_task_elem(
        col: str, row: int, finished: dict, tasks: dict, primary_window: any
    ) -> tuple:
        """Create an element in the main window's table, either a button to bring up a task edit window, a "add new task" button, or a spacer.

        Arguments:
            col -- The column of the current task
            row -- The row of the current task
            finished -- A dictionary containing the completion status of each column from the task list in the format {column_str: finished_bool}
            tasks -- the Python object containing the task list (read from a file using storage_api.py abstractions)
            primary_window -- DearPyGUI object tag for primary window

        Returns:
            (
                finished, -- The argument "finished", now updated
                element_uuid -- The dearpygui object tag of the task element
            )
        """  # noqa: E501
        if not finished[col]:
            try:
                task = tasks[col][row]["task_name"]
                content = tasks[col][row]["task_desc"]
            except IndexError:
                task = None
                content = None
            if task is None:
                element_uuid = dpg.add_button(
                    label="Add Task",
                    callback=lambda x, y: create_new_task_window(
                        x, tasks, primary_window
                    ),
                    tag=col,
                )
                finished[col] = True
            elif isinstance(task, str):
                # bring up modified version of create new task window for callback,
                # access required task by name of list + index of task in list,
                # as arguments to callback?
                element_uuid = dpg.add_button(
                    label=task,
                    callback=lambda: create_task_dialog_window(
                        col, row, task, content, tasks, primary_window
                    ),
                )
        else:
            element_uuid = dpg.add_spacer()
        return (finished, element_uuid)

    def setup_tasks_window(data: dict):
        """Create the main "window" that lists tasks and contains main user interface elements.

        Arguments:
            data -- the Python object containing the task list (read from a file using storage_api.py abstractions)
                A dictionary of lists, each key is the name of the column.  Currently hardcoded to use columns "To Do", "In Progress", and "Done".
        """  # noqa: E501  # todo: document data format more extensively
        # cannot be generated using with as syntax, because it is used outside the with
        # block
        primary_window = dpg.generate_uuid()

        with dpg.window(tag=primary_window):
            with dpg.table(header_row=True):
                dpg.add_table_column(label="To Do")
                dpg.add_table_column(label="In Progress")
                dpg.add_table_column(label="Done")

                finished = {"To Do": False, "In Progress": False, "Done": False}

                # EXPLANATION OF FOLLOWING SPHAGETTI IN RANGE() CALL
                # To ensure enough rows are created for each table column, gets the
                # number of elements in each column and adds this to a list, sort this
                # in descending order, get the largest element as it is now at index 0,
                # and add 1 to it (for add task button)
                for row in range(
                    0,
                    sorted([len(data[d]) for d in data], reverse=True)[0] + 1,
                ):
                    with dpg.table_row():
                        for col in ("To Do", "In Progress", "Done"):
                            finished, elem = create_task_elem(
                                col, row, finished, data, primary_window
                            )
        dpg.set_primary_window(primary_window, True)

    def no_file_window_btn_callback(create_file: bool, window_tag: any):
        """Run callback for buttons in the "file not found" window.

        Arguments:
            create_file -- Which button was clicked i.e. do we create a file or just quit?
            window_tag -- dearpygui object tag for no file window, object with this tag is deleted.
        """  # noqa: E501
        if create_file:
            storage_api.create_file()
            # no need to read this off disk, using json from storage_api so that it can
            # be overriden in one file by importing a compatible module as json.
            data = storage_api.json.loads(storage_api.DEFAULT_FILE_CONTENT)
            dpg.set_primary_window(window_tag, False)
            dpg.delete_item(window_tag)
            setup_tasks_window(data)  # create the actual main windoww
        else:
            # cannot continue without file currently as there is no mechanism for manual
            # saving (yet)
            sys.exit()

    try:
        data = storage_api.get_data()  # get the current tasks
        setup_tasks_window(data)  # create the main window
    except FileNotFoundError:  # the tasks file does not exist
        with dpg.window() as no_file_window:  # initialise a prompt to create a new file
            dpg.add_text("The tasks file does not exist.  Create it?")
            with dpg.table(header_row=False):
                dpg.add_table_column()
                dpg.add_table_column()
                with dpg.table_row():
                    dpg.add_button(
                        label="Yes",
                        callback=lambda: no_file_window_btn_callback(
                            True, no_file_window
                        ),
                    )
                    dpg.add_button(
                        label="No",
                        callback=lambda: no_file_window_btn_callback(
                            False, no_file_window
                        ),
                    )
                    dpg.set_primary_window(no_file_window, True)
    finally:
        # this is the window seen by the window manager, which dearpygui creates its own
        # virtual "windows" in.
        dpg.create_viewport(title="Tasks", width=600, height=300)
        # init dearpygui
        dpg.setup_dearpygui()
        # actually show the window seen by the wm
        dpg.show_viewport()
        # starts render loop (handled by dearpygui), blocks until window closed
        dpg.start_dearpygui()
        # clean up
        dpg.destroy_context()
