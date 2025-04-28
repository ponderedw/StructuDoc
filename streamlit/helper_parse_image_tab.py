import streamlit as st
from helper import get_from_backend, get_from_backend_streaming, \
    post_to_backend
import json
import tempfile


@st.fragment()
def get_parse_image_tab(selected_values):
    with st.form("parse_image_form"):
        prompt_value = ''
        with open('streamlit/default_images_prompt.txt', 'r') as f:
            prompt_value = f.read()
        prompt = st.text_area("Prompt",
                              value=prompt_value,
                              height=200)
        parse_image_submitted = st.form_submit_button("View Result")
        parse_image_submitted_save = st.form_submit_button("Save Result")

    if parse_image_submitted:
        if selected_values:
            st.session_state.images_parsing_succeeded = False
            st.session_state.images_description = {}
            for folder in selected_values:
                with st.expander(folder):
                    try:
                        backend_method = 's3_interactions/get_all_the_images'
                        images = get_from_backend(
                            backend_method=backend_method,
                            folder_path=folder)
                        images = {k: v for k, v in images.items()}
                        st.session_state.images_description[folder] = \
                            {'prompt': prompt,
                             'images': {}}
                        backend_mathod = \
                            'parse_data_with_llm/get_image_description'
                        for image_name, image_bytes in images.items():
                            st.markdown(f"""## {image_name}

![{image_name}](data:image/{image_name.split('.')[-1]};base64,{image_bytes})

                                    """,
                                        unsafe_allow_html=True)
                            image_description = st.write_stream(
                                get_from_backend_streaming(
                                    backend_method=backend_mathod,
                                    params={
                                        'prompt': prompt,
                                        'image_path': folder + '/images/'
                                        + image_name
                                    }
                                )
                                            )
                            st.session_state\
                                .images_description[folder]['images'][
                                    image_name] = image_description
                    except Exception as e:
                        st.error(e)
            st.session_state.images_parsing_succeeded = True
        else:
            st.warning('Please Choose At Least One Folder')

    if parse_image_submitted_save:
        if selected_values:
            if hasattr(st.session_state, 'images_parsing_succeeded') \
               and st.session_state.images_parsing_succeeded:
                st.write(st.session_state.images_description)
                backend_method = 's3_interactions/upload_parsed_file'
                for folder, desc in st.session_state\
                        .images_description.items():
                    with tempfile.NamedTemporaryFile(mode="w+", suffix=".json",
                                                     delete=False) as tmpfile:
                        json.dump(desc, tmpfile)
                        tmpfile.seek(0)
                        data = post_to_backend(backend_method=backend_method,
                                               data={
                                                   'folder_name': folder,
                                                   'subfolder_name':
                                                   'images_descriptions',
                                                   'file_template':
                                                   'images_description'
                                                    },
                                               files={'parsed_json_file':
                                                      tmpfile})
                        st.write(f'Load is finished for {folder}')
                        st.write(data)
            else:
                backend_method = 'parse_data_with_llm/load_images_descriptions'
                for folder in selected_values:
                    try:
                        data = post_to_backend(backend_method=backend_method,
                                               params={'prompt': prompt,
                                                       'folder_name': folder})
                        st.write(f'Load is finished for {folder}')
                        st.write(data)
                    except Exception as e:
                        st.write(f'Load failed for {folder}')
                        st.error(e)
        else:
            st.warning('Please Choose At Least One Folder')
