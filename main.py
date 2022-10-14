import dearpygui.dearpygui as dpg
import storage_api
import sys

dpg.create_context()

if 0: # debug mode
    dpg.show_documentation()
    dpg.show_style_editor()
    dpg.show_debug()
    dpg.show_about()
    dpg.show_metrics()
    dpg.show_font_manager()
    dpg.show_item_registry()

def add_new_task(list_name, tasks, title, desc, create_task_window, primary_window):
    tasks[list_name].append({"task_name":title,"task_desc":desc})
    storage_api.write_data(tasks)
    dpg.delete_item(create_task_window)
    dpg.delete_item(primary_window)
    setup_tasks_window(tasks) # turns out this doesnt cause infinite recursion since setup_tasks_window exits - the callbacks are dealt with on a separate thread

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
                dpg.add_button(label="Create New Task",callback=lambda:add_new_task(list_name, tasks, dpg.get_value(title), dpg.get_value(content), create_task_window, primary_window)) # todo:build callback
                dpg.add_button(label="Cancel",callback=lambda:dpg.delete_item(create_task_window))

def create_task_elem(col, row, finished, tasks, primary_window):
    if not finished[col]:
        #tasks = storage_api.json.loads('{"To Do": [{"task_name":"spam","task_desc":""},{"task_name":"spam","task_desc":""}],"In Progress":[{"task_name":"ham","task_desc":""}],"Done":[{"task_name":"eggs","task_desc":""},{"task_name":"eggs","task_desc":""},{"task_name":"eggs","task_desc":""}]}')
#        tasks = [
#            ["spam", "ham", "eggs"],
#            ["spam", None, "eggs"],
#            [None, None, "eggs"]
#            ]
        try:
            task = tasks[col][row]["task_name"]
        except IndexError:
            task = None
        print(task)
        if task == None:
            element_uuid = dpg.add_button(label="Add Task", callback=lambda x,y:create_new_task_window(x,tasks, primary_window), tag=col)
            finished[col] = True
        elif type(task) == type(str()):
            element_uuid = dpg.add_button(label=task) # bring up modified version of create new task window for callback, access required task by name of list + index of task in list, as arguments to callback?
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

            finished={"To Do":False, "In Progress":False, "Done":False}

            for row in range(0,sorted([len(data[d]) for d in data], reverse=True)[0]+1):
                with dpg.table_row():
                    for col in ("To Do", "In Progress", "Done"):
                        finished, elem = create_task_elem(col, row, finished, data, primary_window) # todo: put elem in a list somewhere so elements can be overwritten in future
    dpg.set_primary_window(primary_window, True)



def no_file_window_btn_callback(create_file: bool, window_tag):
    if create_file:
        storage_api.create_file()
        data = storage_api.json.loads(storage_api.DEFAULT_FILE_CONTENT) # no need to read this off disk
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
                dpg.add_button(label="Yes", callback=lambda:no_file_window_btn_callback(True, no_file_window))
                dpg.add_button(label="No", callback=lambda:no_file_window_btn_callback(False, no_file_window))
                dpg.set_primary_window(no_file_window, True)
finally:
    dpg.create_viewport(title='Custom Title', width=600, height=200)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()