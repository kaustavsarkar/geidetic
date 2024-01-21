
from typing import List
import os
from pathlib import Path
import sys
import streamlit as st
import shutil

# prefix components:
_SPACE = '    '
_BRANCH = '│   '
# pointers:
_TEE = '├── '
_LAST = '└── '

configs = {
    'APP_BASE_DIR': os.path.dirname(os.path.realpath(__file__))
}




def tree(dir_path: Path, prefix: str = ''):
    """A recursive generator, given a directory Path object
    will yield a visual tree structure line by line
    with each line prefixed by the same characters
    """
    contents = list(dir_path.iterdir())
    # contents each get pointers that are ├── with a final └── :
    pointers = [_TEE] * (len(contents) - 1) + [_LAST]
    for pointer, path in zip(pointers, contents):
        yield prefix + pointer + path.name
        if path.is_dir():  # extend the prefix and recurse:
            extension = _BRANCH if pointer == _TEE else _SPACE
            # i.e. space because last, └── , above so no more |
            yield from tree(path, prefix=prefix + extension)


def get_dirs_inside_dir(folder) -> List[str]:
    """Gets directories inside an existing directory"""
    return [my_dir for my_dir in list(map(lambda x: os.path.basename(x), sorted(Path(folder).iterdir(), key=os.path.getmtime, reverse=True))) if os.path.isdir(os.path.join(folder, my_dir))
            and my_dir != '__pycache__' and my_dir != '.ipynb_checkpoints' and my_dir != 'API']


def list_folders_in_folder(folder):
    return [file for file in os.listdir(folder) if os.path.isdir(os.path.join(folder, file))]


def show_dir_tree(folder):
    with st.expander(f"Show {os.path.basename(folder)} folder tree"):
        for line in tree(Path.home() / folder):
            st.write(line)


def delete_folder(folder, ask=True):
    if not ask:
        shutil.rmtree(folder)
    else:
        folder_basename = os.path.basename(folder)
        if len(os.listdir(folder)) > 0:
            st.warning(
                f"**{folder_basename} is not empty. Are you sure you want to delete it?**")
            show_dir_tree(folder)
            if st.button("Yes"):
                try:
                    shutil.rmtree(folder)
                except:
                    st.error(f"Couldn't delete {folder_basename}:")
                    e = sys.exc_info()
                    st.error(e)
        else:
            st.write(f"**Are you sure you want to delete {folder_basename}?**")
            if st.button("Yes"):
                try:
                    shutil.rmtree(folder)
                except:
                    st.error(f"Couldn't delete {folder_basename}:")
                    e = sys.exc_info()
                    st.error(e)


# Implementation

    col1_size = 10
    col1, col2 = st.columns((col1_size, 1))

    with col1:
        models_abs_dir = os.path.join(configs['APP_BASE_DIR'], configs['MODELS_DIR'])
        temp = []
        i = 0
        while temp != configs['CURRNET_FOLDER_STR'] and temp != configs['CREATE_FOLDER_STR']:
            i += 1
            state.files_to_show = get_dirs_inside_dir(models_abs_dir)
            temp = st.selectbox("Models' folder" + f": level {i}",
                                options=[configs['CURRNET_FOLDER_STR']] + state.files_to_show
                                        + [configs['CREATE_FOLDER_STR']] + [configs['DELETE_FOLDER_STR']],
                                key=models_abs_dir)
            if temp == configs['CREATE_FOLDER_STR']:
                new_folder = st.text_input(label="New folder name", value=str(state.dataset_name) + '_' +
                                                                          str(state.model) + '_models', key="new_folder")
                new_folder = os.path.join(models_abs_dir, new_folder)
                if st.button("Create new folder"):
                    os.mkdir(new_folder)
                    state.files_to_show = get_dirs_inside_dir(models_abs_dir)
            elif temp == configs['DELETE_FOLDER_STR']:
                if list_folders_in_folder(models_abs_dir):
                    chosen_delete_folder = st.selectbox(
                        label="Folder to delete",                        options=list_folders_in_folder(models_abs_dir), key="delete_folders")
                    chosen_delete_folder = os.path.join(models_abs_dir, chosen_delete_folder)
                    delete_folder(chosen_delete_folder)
                    state.files_to_show = get_dirs_inside_dir(models_abs_dir)
                else:
                    st.info('No folders found')
            elif not temp == configs['CURRNET_FOLDER_STR']:
                models_abs_dir = os.path.join(models_abs_dir, temp)
        try:
            show_dir_tree(models_abs_dir)
        except FileNotFoundError:
            pass
        table = st.empty()
        try:
            files_in_dir = os.listdir(models_abs_dir)
            if ".gitignore" in files_in_dir:
                files_in_dir.remove(".gitignore")
            table.write(models_table(files_in_dir))
        except FileNotFoundError:
            st.error("No 'saved_models' folder, you should change working dir.")
        except ValueError:
            pass
        except:
            e = sys.exc_info()
            st.info(e)