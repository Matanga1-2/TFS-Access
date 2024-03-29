"""
The module is in charge of performing the tfs requested operations
"""

import requests.exceptions
from operations import get_objects


def copy_task(tfs_instance, original_task_data, target_pbi_data):
    """
    Function to copy a TFS task from one PBI to another PBI as a child
    :param tfs_instance: the TFS connection
    :param original_task_data: a TFS work item object of the task to copy
    :param target_pbi_data: the target PBI data
    :return: the new task ID
    """

    # Build the task fields
    original_task = original_task_data.fields

    # Only if type is "Task"
    if original_task["System.WorkItemType"] == "Task":
        target_task = ({})
        try:
            target_task["System.State"] = "To Do"
            target_task["System.AreaId"] = target_pbi_data["System.AreaId"]
            target_task["System.IterationId"] = target_pbi_data["System.IterationId"]
            target_task["System.Title"] = original_task["System.Title"]
            target_task["Microsoft.VSTS.Common.BacklogPriority"] = \
                original_task["Microsoft.VSTS.Common.BacklogPriority"]
            target_task["Microsoft.VSTS.Common.Activity"] = \
                original_task["Microsoft.VSTS.Common.Activity"]
            target_task["System.Description"] = original_task["System.Description"]
        except:
            pass

        # Add a new task to the target PBI with the source task fields
        try:
            new_task = tfs_instance.add_workitem(target_task,
                                                 target_pbi_data.id, workitem_type="Task")
            print("Task " +
                  str(new_task) +
                  " was copied to PBI " +
                  str(target_pbi_data.id) +
                  " successfully")
        except requests.exceptions.HTTPError as error:
            print(f'Oops.. there was an HTTP error: {error}')
            return


def copy_pbi_to_cleanup(tfs_instance, user_credentials, title_type):
    """
    Function to duplicate a PBI in the same feature if available
    :param tfs_instance: the TFS connection
    :param user_credentials: the credentials
    :param title_type: which title should be
    :return: the new PBI ID
    """

    # Get the original PBI ID
    print("Please enter the original PBI ID")
    original_pbi_id = get_objects.get_item_id()

    # Get the cleanup PBI tasks
    try:
        cleanup_pbi = get_objects.get_cleanup_pbi(tfs_instance,
                                                  original_pbi_id,
                                                  title_type)
    except get_objects.WorkitemDoesntMatchIDError:
        print("Workitem ID doesn't match a PBI")
        return

    # Add the cleanup PBI
    try:
        new_pbi = tfs_instance.add_workitem(item_fields=cleanup_pbi["data"],
                                            parent_item_id=cleanup_pbi["parent_id"],
                                            workitem_type="PBI")
        print(f'PBI {str(new_pbi)} was created successfully')
        new_pbi_data = tfs_instance.connection.get_workitem(new_pbi)
    except requests.exceptions.HTTPError as error:
        print("Oops.. there was an HTTP error: {0}".format(error))
        return

    # Add the related relation
    relation_url = 'https://tfs2018.net-bet.net/tfs/DefaultCollection/' \
                   '154f45b9-7e72-44b9-bd28-225c488dfde2/' \
                   '_apis/wit/workItems/'
    relations = ([])
    try:
        relations.append({'rel': 'System.LinkTypes.Related',
                          'url': relation_url + str(original_pbi_id)})
        relations.append({'rel': 'System.LinkTypes.Dependency-Reverse',
                          'url': relation_url + str(original_pbi_id)})
        new_pbi_data.add_relations_raw(relations)
    except:
        pass

    # Add cleanup tasks to the new PBI
    try:
        add_tasks_to_pbi(tfs_instance, user_credentials,
                         pbi_type="CleanupTasks", pbi_id=new_pbi)
    except requests.exceptions.HTTPError as error:
        print(f'Oops.. there was an HTTP error: {error}')
        return


def create_cleanup_pbi_to_feature(tfs_instance, user_credentials):
    """
    Function to create a cleanup PBI to a feature
    :param tfs_instance: the TFS connection
    :param user_credentials: the credentials
    :kwargs expected a dictionary with the feature ID
    :return: the new PBI ID
    """

    # Get the feature PBI ID
    print("Please enter the original PBI ID")
    original_pbi_id = get_objects.get_item_id()

    # Get the cleanup PBI tasks
    try:
        cleanup_pbi = get_objects.get_cleanup_pbi(tfs_instance, original_pbi_id)
    except get_objects.WorkitemDoesntMatchIDError:
        print("Workitem ID doesn't match a PBI")
        return

    # Add the cleanup PBI
    try:
        new_pbi = tfs_instance.add_workitem(item_fields=cleanup_pbi["data"],
                                            parent_item_id=cleanup_pbi["parent_id"],
                                            workitem_type="PBI")
        print(f'PBI {str(new_pbi)} was created successfully')
        new_pbi_data = tfs_instance.connection.get_workitem(new_pbi)
    except requests.exceptions.HTTPError as error:
        print(f'Oops.. there was an HTTP error: {error}')
        return

    # Add the related relation
    relation_url = 'https://tfs2018.net-bet.net/tfs/DefaultCollection/' \
                   '154f45b9-7e72-44b9-bd28-225c488dfde2/' \
                   '_apis/wit/workItems/'
    relations = ([])
    try:
        relations.append({'rel': 'System.LinkTypes.Related',
                          'url': relation_url + str(original_pbi_id)})
        relations.append({'rel': 'System.LinkTypes.Dependency-Reverse',
                          'url': relation_url + str(original_pbi_id)})
        new_pbi_data.add_relations_raw(relations)
    except:
        pass

    # Add cleanup tasks to the new PBI
    try:
        add_tasks_to_pbi(tfs_instance, user_credentials,
                         pbi_type="CleanupTasks", pbi_id=new_pbi)
    except requests.exceptions.HTTPError as error:
        print(f'Oops.. there was an HTTP error: {error}')
        return


def add_task_to_pbi(tfs_instance, task, pbi_data):
    """
    Add a new task to a specific PBI (with correct area and iteration)
    :param tfs_instance: the TFS connection
    :param task: a task fields dictionary
    :param pbi_data: a PBI object
    :return: nothing
    """
    task['System.AreaId'] = pbi_data['System.AreaId']  # Area Path
    task['System.IterationId'] = pbi_data['System.IterationId']  # Iteration Path
    try:
        new_task = tfs_instance.add_workitem(task,
                                             pbi_data.id,
                                             workitem_type="Task")  # Add a new task
    except requests.exceptions.HTTPError as error:
        print(f'Oops.. there was an HTTP error: {error}')
        return
    print(f'Task {str(new_task)} was added successfully')


def add_tasks_to_pbi(tfs_instance, user_credentials, pbi_id=None, pbi_type="regular"):
    """
    Add all of the required tasks to a PBI, based on a given type
    :param tfs_instance: the TFS connection
    :param user_credentials: the user credentials dictionary
    :param pbi_id: a given PBI to add the tasks to
    :param pbi_type: the type of tasks to add
    :return: nothing
    """

    # Ask for PBI ID
    if pbi_id is None:
        pbi_id = get_objects.get_item_id()

    # Get the PBI data
    try:
        pbi_data = tfs_instance.connection.get_workitem(pbi_id)
    except requests.exceptions.HTTPError as error:
        print(f'An HTTP error: {error}')
        return
    except:
        return

    # Get tasks to add
    tasks = get_objects.get_tasks(user_credentials, pbi_type=pbi_type)

    # Add tasks
    for task in tasks:
        add_task_to_pbi(tfs_instance, task, pbi_data)


def clone_pbi_tasks(tfs_instance):
    """
    Copies a specific PBI tasks to another PBI
    :param tfs_instance: the TFS connection
    :return: nothing
    """

    # Ask for the first PBI ID
    print("You need to specify the source PBI ID")
    source_pbi_id = get_objects.get_item_id()

    # Get the first PBI data
    try:
        source_pbi_data = tfs_instance.connection.get_workitem(source_pbi_id)
    except requests.exceptions.HTTPError as error:
        print(f'An HTTP error: {error}')
        return
    except:
        return

    # Ask for the second PBI ID
    print("You need to specify the target PBI ID")
    target_pbi_id = get_objects.get_item_id()

    # Get the second PBI data
    try:
        target_pbi_data = tfs_instance.connection.get_workitem(target_pbi_id)
    except requests.exceptions.HTTPError as error:
        print('An HTTP error: {0}'.format(error))
        return
    except:
        return

    # Copy tasks
    for task_id in source_pbi_data.child_ids:
        task = tfs_instance.connection.get_workitem(task_id)
        copy_task(tfs_instance, task, target_pbi_data)


def remove_pbi_with_tasks(tfs_instance, user_credentials):
    """
    The function will get a PBI number and remove it and its tasks.
    Remove is changing the state, area, and iteration.
    :param tfs_instance: the TFS connection
    :param user_credentials: the user credentials
    :return: nothing
    """

    # Ask for the PBI ID
    pbi_id = get_objects.get_item_id()

    # Get the PBI data
    try:
        pbi_data = tfs_instance.connection.get_workitem(pbi_id)
    except requests.exceptions.HTTPError as error:
        print('An HTTP error: {0}'.format(error))
        return
    except:
        return

    # Remove tasks
    for task_id in pbi_data.child_ids:
        try:
            remove_task(tfs_instance, user_credentials, task_id)
        except requests.exceptions.HTTPError as error:
            print('An HTTP error: {0}'.format(error))
            return
        except:
            print('Oops.. Something went wrong. Please try again')
            return

    # Remove the PBI
    update_data = get_objects.get_removed_task_data(user_credentials)
    try:
        tfs_instance.connection.update_workitem(pbi_id, update_data)
        print(f'PBI {pbi_id} was removed successfully')
    except requests.exceptions.HTTPError as error:
        print('An HTTP error: {0}'.format(error))
        return
    except:
        print('Oops.. Something went wrong. Please try again')
        return


def remove_task(tfs_instance, user_credentials, task_id):
    """
    The function will get a Task number and remove it and its tasks.
    Remove is changing the state, area, and iteration.
    :param tfs_instance: the TFS connection
    :param user_credentials: the user credentials
    :param task_id: the ID of the task to be removed
    :return: nothing
    """
    task_data = tfs_instance.connection.get_workitem(task_id)
    relations = task_data.data.get('relations')
    for _ in range(len(relations)):
        update_data = get_objects.get_removed_task_data(user_credentials, rel_count=1)
        try:
            tfs_instance.connection.update_workitem(work_item_id=task_id, update_data=update_data)
            print(f'Task {task_id} was removed successfully')
        except requests.exceptions.HTTPError as error:
            print('An HTTP error: {0}'.format(error))
            return
        except:
            print('Oops.. Something went wrong. Please try again')


def remove_task_from_pbi(tfs_instance, user_credentials):
    """
    The function will ask for a Task number from the user, and remove it.
    :param tfs_instance: the TFS connection
    :param user_credentials: the user credentials
    :return: nothing
    """
    # Ask for the task ID
    task_id = get_objects.get_item_id()

    # Remove the task
    try:
        remove_task(tfs_instance, user_credentials, task_id)
    except requests.exceptions.HTTPError as error:
        print(f'An HTTP error: {error}')
        return
    except:
        print('Oops.. Something went wrong. Please try again')
        return
