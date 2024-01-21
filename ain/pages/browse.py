import streamlit as st
from streamlit_file_browser import st_file_browser
from pathlib import Path

st.header('Default Options')
home = Path.home()
event = st_file_browser("../", key='A',
                        # use_static_file_server=True,
                        show_new_folder=True,
                        show_upload_file=True,
                        show_choose_file=True,
                        show_preview=False,
                        # extentions=['pdf'],
                        )
st.write(event)
