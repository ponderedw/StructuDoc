from st_ant_tree import st_ant_tree
import streamlit as st
from helper import build_tree, get_from_backend_streaming
from helper import get_from_backend, post_to_backend
import json

paths = get_from_backend(backend_method='s3_interactions/get_all_the_folders')
paths = [folder['folder_path'] for folder in paths]
tree = build_tree(paths)['children']


with st.form("user_form"):
    selected_values = st_ant_tree(
        treeData=tree,
        treeCheckable=True,
        allowClear=True,
        only_children_select=True,
        placeholder='Choose Files You Want to Parse'
    )
    prompt_value = ''
    with open('streamlit/default_common_schema_prompt.txt', 'r') as f:
        prompt_value = f.read()
    prompt = st.text_area("Prompt",
                          value=prompt_value,
                          height=200)
    submitted = st.form_submit_button("View Result")
    submitted_save = st.form_submit_button("Save Result")

if submitted:
    if selected_values:
        backend_method = 'parse_data_with_llm/get_common_schema'
        parsed_json_stream = st.write_stream(
            get_from_backend_streaming(
                backend_method=backend_method,
                params={
                    'prompt': prompt,
                    'folders': ','.join(selected_values)
                }
            )
                        )
        st.json(json.loads(parsed_json_stream[
                    parsed_json_stream.find('{'):]))
    else:
        st.warning('Please Choose At Least One Folder')

if submitted_save:
    if selected_values:
        backend_method = 'parse_data_with_llm/load_common_schema'
        data = post_to_backend(backend_method=backend_method,
                               params={'prompt': prompt,
                                       'folders': ','.join(selected_values)})
        st.write(data)
    else:
        st.warning('Please Choose At Least One Folder')
