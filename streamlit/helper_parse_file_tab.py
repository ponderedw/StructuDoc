import streamlit as st
from helper import get_from_backend, get_from_backend_streaming, \
    post_to_backend
import json
import tempfile


@st.fragment()
def get_parse_file_tab(selected_values):
    with st.form("parse_file_form"):
        prompt_value = ''
        with open('streamlit/default_parsing_prompt.txt', 'r') as f:
            prompt_value = f.read()
        prompt = st.text_area("Prompt",
                              value=prompt_value,
                              height=200)
        parse_file_submitted = st.form_submit_button("View Result")
        parse_file_submitted_save = st.form_submit_button("Save Result")

    if parse_file_submitted:
        if selected_values:
            st.session_state.file_parsing_succeeded = False
            st.session_state.file_description = {}
            for folder in selected_values:
                with st.expander(folder):
                    backend_method = \
                        's3_interactions/get_images_explanations_paths'
                    images_decriptions_paths = get_from_backend(
                            backend_method=backend_method,
                            folder_path=folder)
                    if not images_decriptions_paths:
                        st.write("There aren't any images descriptions yet")
                    backend_method = 'parse_data_with_llm/get_parsed_file'
                    parsed_json_stream = st.write_stream(
                        get_from_backend_streaming(
                            backend_method=backend_method,
                            params={
                                'prompt': prompt,
                                'folder_name': folder
                            }
                        )
                                    )
                    parsed_json = json.loads(parsed_json_stream[
                        parsed_json_stream.find('{'):])
                    st.json(parsed_json)
                    backend_method = \
                        's3_interactions/get_last_image_file_name'
                    file_name = get_from_backend(backend_method=backend_method,
                                                 folder_name=folder)
                    st.session_state.file_description[folder] = {
                        'data': parsed_json,
                        'prompt': prompt,
                        'images_description_path': file_name
                    }
            st.session_state.file_parsing_succeeded = True
        else:
            st.warning('Please Choose At Least One Folder')

    if parse_file_submitted_save:
        if selected_values:
            if hasattr(st.session_state, 'file_parsing_succeeded') \
               and st.session_state.file_parsing_succeeded:
                st.write(st.session_state.file_description)
                backend_method = 's3_interactions/upload_parsed_file'
                for folder, desc in st.session_state\
                        .file_description.items():
                    with tempfile.NamedTemporaryFile(mode="w+", suffix=".json",
                                                     delete=False) as tmpfile:
                        json.dump(desc, tmpfile)
                        tmpfile.seek(0)
                        data = post_to_backend(backend_method=backend_method,
                                               data={
                                                   'folder_name': folder,
                                                   'subfolder_name':
                                                   'parsed_document',
                                                   'file_template':
                                                   'parsed_document'
                                                    },
                                               files={'parsed_json_file':
                                                      tmpfile})
                        st.write(f'Load is finished for {folder}')
                        st.write(data)
            else:
                for folder in selected_values:
                    backend_method = \
                            's3_interactions/get_images_explanations_paths'
                    images_decriptions_paths = get_from_backend(
                            backend_method=backend_method,
                            folder_path=folder)
                    if not images_decriptions_paths:
                        st.write("There aren't any images descriptions yet")
                    backend_method = 'parse_data_with_llm/load_parsed_file'
                    data = post_to_backend(backend_method=backend_method,
                                           params={'prompt': prompt,
                                                   'folder_name': folder})
                    st.write(f'Load is finished for {folder}')
                    st.write(data)
        else:
            st.warning('Please Choose At Least One Folder')
