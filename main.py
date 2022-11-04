if __name__ == "__main__":
    import dearpygui.dearpygui as dpg
    import storage_api
    import sys

    dpg.create_context()

    def add_new_task(
        list_name,
        tasks,
        title,
        desc,
        create_task_window=None,
        primary_window=None,
        handle_window_mgmt=True,
        handle_storage_mgmt=True,
    ):  # copy new arguemnts to delete task and potentially use in task update
        tasks[list_name].append({"task_name": title, "task_desc": desc})
        if handle_storage_mgmt:
            storage_api.write_data(tasks)
        else:
            return tasks
        if handle_window_mgmt:
            if primary_window == None or create_task_window == None:
                raise ValueError(
                    "Tried to handle window management, but failed to pass a window!"
                )
            dpg.delete_item(create_task_window)
            dpg.delete_item(primary_window)
            setup_tasks_window(
                tasks
            )  # turns out this doesnt cause infinite recursion since setup_tasks_window exits - the callbacks are dealt with on a separate thread

    def create_new_task_window(list_name, tasks, primary_window):
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
        col, row, task_name, task_content, element_to_delete, tasks, primary_window
    ):
        dpg.delete_item(element_to_delete)
        tasks[col][row] = {"task_name": task_name, "task_desc": task_content}
        storage_api.write_data(tasks)
        dpg.delete_item(primary_window)
        setup_tasks_window(
            tasks
        )  # see above for why this does not cause overflow on stack

    def delete_task(col, row, edit_task_window, tasks, primary_window):
        dpg.delete_item(edit_task_window)
        tasks[col].pop(row)
        storage_api.write_data(tasks)
        dpg.delete_item(primary_window)
        setup_tasks_window(tasks)

    def move_task(
        col,
        row,
        task_name,
        task_content,
        task_window,
        task_list,
        primary_window,
        direction=False,
    ):
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
        col, row, task_name, task_content, task_list, primary_window
    ):
        # figure out how to size this properly
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
                    if col == "To Do":
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
                    dpg.add_text("Move")
                    if col == "Done":
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
                    # add a move task dialog that will move a task by getting it, adding it to the new list, and removing it from the old one

    def create_task_elem(col, row, finished, tasks, primary_window):
        if not finished[col]:
            try:
                task = tasks[col][row]["task_name"]
                content = tasks[col][row]["task_desc"]
            except IndexError:
                task = None
                content = None
            print(task)
            if task == None:
                element_uuid = dpg.add_button(
                    label="Add Task",
                    callback=lambda x, y: create_new_task_window(
                        x, tasks, primary_window
                    ),
                    tag=col,
                )
                finished[col] = True
            elif type(task) == type(str()):
                element_uuid = dpg.add_button(
                    label=task,
                    callback=lambda: create_task_dialog_window(
                        col, row, task, content, tasks, primary_window
                    ),
                )  # bring up modified version of create new task window for callback, access required task by name of list + index of task in list, as arguments to callback?
        else:
            element_uuid = dpg.add_spacer()
        print(finished)
        return (finished, element_uuid)

    def setup_tasks_window(data):
        primary_window = dpg.generate_uuid()

        with dpg.window(tag=primary_window):
            with dpg.table(header_row=True):
                dpg.add_table_column(label="To Do")
                dpg.add_table_column(label="In Progress")
                dpg.add_table_column(label="Done")

                finished = {"To Do": False, "In Progress": False, "Done": False}

                for row in range(
                    0, sorted([len(data[d]) for d in data], reverse=True)[0] + 1
                ):
                    with dpg.table_row():
                        for col in ("To Do", "In Progress", "Done"):
                            finished, elem = create_task_elem(
                                col, row, finished, data, primary_window
                            )
        dpg.set_primary_window(primary_window, True)

    def no_file_window_btn_callback(create_file: bool, window_tag):
        if create_file:
            storage_api.create_file()
            data = storage_api.json.loads(
                storage_api.DEFAULT_FILE_CONTENT
            )  # no need to read this off disk
            dpg.set_primary_window(window_tag, False)
            dpg.delete_item(window_tag)
            setup_tasks_window(data)
        else:
            sys.exit()

    try:
        data = storage_api.get_data()
        setup_tasks_window(data)
    except FileNotFoundError:
        with dpg.window() as no_file_window:
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
        dpg.create_viewport(title="Tasks", width=600, height=300)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()
