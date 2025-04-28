import streamlit as st
from helper import get_from_backend_streaming, \
    post_to_backend
import json
import tempfile


@st.fragment()
def get_find_common_schema_tab(selected_values):
    with st.form("find_common_schema_form"):
        prompt_value = ''
        with open('streamlit/default_common_schema_prompt.txt', 'r') as f:
            prompt_value = f.read()
        prompt = st.text_area("Prompt",
                              value=prompt_value,
                              height=200)
        find_common_schema_submitted = st.form_submit_button("View Result")
        find_common_schema_submitted_save = \
            st.form_submit_button("Save Result")

    if find_common_schema_submitted:
        if selected_values:
            st.session_state.common_schema_succeeded = False
            backend_method = 'parse_data_with_llm/get_common_schema'
            with st.empty():
                parsed_json_stream = st.write_stream(
                    get_from_backend_streaming(
                        backend_method=backend_method,
                        params={
                            'prompt': prompt,
                            'folders': ','.join(selected_values)
                        }
                    )
                                )
                parsed_common_json = json.loads(parsed_json_stream[
                            parsed_json_stream.find('{'):])
                st.json(parsed_common_json)
            st.session_state.common_schema = {
                'prompt': prompt,
                'schema': parsed_common_json,
                'files': selected_values,
            }
            st.session_state.common_schema_succeeded = True
        else:
            st.warning('Please Choose At Least One Folder')

    if find_common_schema_submitted_save:
        if selected_values:
            if hasattr(st.session_state, 'common_schema_succeeded') \
               and st.session_state.common_schema_succeeded:
                st.write(st.session_state.common_schema)
                backend_method = 's3_interactions/upload_parsed_file'
                with tempfile.NamedTemporaryFile(mode="w+", suffix=".json",
                                                 delete=False) as tmpfile:
                    json.dump(st.session_state.common_schema, tmpfile)
                    tmpfile.seek(0)
                    data = post_to_backend(backend_method=backend_method,
                                           data={
                                            'folder_name': 'common_schemas',
                                            'subfolder_name':
                                            'common_schemas_jsons',
                                            'file_template':
                                            'common_schema'
                                                },
                                           files={'parsed_json_file':
                                                  tmpfile})
                    st.write('Load is finished')
                    st.write(data)
            else:
                backend_method = 'parse_data_with_llm/load_common_schema'
                data = post_to_backend(backend_method=backend_method,
                                       params={'prompt': prompt,
                                               'folders': ','.join(
                                                   selected_values)
                                               })
                st.write(data)
        else:
            st.warning('Please Choose At Least One Folder')
