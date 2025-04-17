import streamlit as st
from helper import build_tree
from helper import get_from_backend, post_to_backend, \
    get_from_backend_streaming, remove_watermark
from st_ant_tree import st_ant_tree
import json

remove_watermark()

paths = get_from_backend(backend_method='s3_interactions/get_all_the_folders')
paths = [folder['folder_path'] for folder in paths]
tree = build_tree(paths)['children']

selected_values = []
with st.sidebar.container():
    selected_values = st_ant_tree(
        treeData=tree,
        treeCheckable=True,
        allowClear=True,
        only_children_select=True,
        placeholder='Choose Files You Want to See'
    )


view_files_tab, parse_image_tab, \
    parse_file_tab, find_common_schema_tab, \
    view_common_schemas_tab = st.tabs(["View Files",
                                       "Parse Image With LLM",
                                       "Parse File With LLM",
                                       "Find Common Schema",
                                       "View Common Schemas"])


with view_files_tab:
    folders = selected_values if selected_values else []
    for selected_value in folders:
        with st.expander(selected_value):
            with st.popover("Parsed Markdown", icon="📄"):
                backend_method = 's3_interactions/get_markdown_with_images'
                parsed_markdown = get_from_backend(
                    backend_method=backend_method,
                    folder_path=selected_value)
                st.markdown(f"""{parsed_markdown}""",
                            unsafe_allow_html=True)
            with st.popover("Images", icon="🖼️"):
                backend_method = 's3_interactions/get_all_the_images'
                images = get_from_backend(backend_method=backend_method,
                                          folder_path=selected_value)
                images = {k: v for k, v in images.items()}
                for image_name, image_bytes in images.items():
                    st.markdown(f"""## {image_name}

![{image_name}](data:image/{image_name.split('.')[-1]};base64,{image_bytes})

                                """,
                                unsafe_allow_html=True)
            with st.popover("Images To Text", icon="📝"):
                backend_method = \
                    's3_interactions/get_images_explanations_paths'
                images_decriptions_paths = \
                    images = get_from_backend(
                        backend_method=backend_method,
                        folder_path=selected_value)
                if not images_decriptions_paths:
                    st.write("There aren't any images descriptions yet")
                else:
                    option = st.selectbox(
                        f"Choose a prompt for {selected_value}:",
                        images_decriptions_paths
                    )
                    if option:
                        backend_method = \
                            's3_interactions/get_images_explanation'
                        image_description = \
                            get_from_backend(backend_method=backend_method,
                                             folder_path=selected_value,
                                             description_path=option)
                        st.json(json.loads(image_description))
            with st.popover("JSON Parsings", icon="🗂️"):
                backend_method = 's3_interactions/receive_json_parsings_paths'
                json_parsings_paths = \
                    get_from_backend(backend_method=backend_method,
                                     folder_path=selected_value)
                if not json_parsings_paths:
                    st.write("There aren't any parsing JSON yet")
                else:
                    option = st.selectbox(
                        f"Choose a prompt for {selected_value}:",
                        json_parsings_paths
                    )
                    if option:
                        backend_method = \
                            's3_interactions/receive_json_parsings'
                        json_parsings = \
                            get_from_backend(backend_method=backend_method,
                                             folder_path=selected_value,
                                             parsing_path=option)
                        json_parsings = json.loads(json_parsings)
                        st.json(json_parsings)

with parse_image_tab:
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
            for folder in selected_values:
                with st.expander(folder):
                    backend_method = 's3_interactions/get_all_the_images'
                    images = get_from_backend(backend_method=backend_method,
                                              folder_path=folder)
                    images = {k: v for k, v in images.items()}
                    backend_mathod = \
                        'parse_data_with_llm/get_image_description'
                    for image_name, image_bytes in images.items():
                        st.markdown(f"""## {image_name}

![{image_name}](data:image/{image_name.split('.')[-1]};base64,{image_bytes})

                                """,
                                    unsafe_allow_html=True)
                        st.write_stream(get_from_backend_streaming(
                            backend_method=backend_mathod,
                            params={
                                'prompt': prompt,
                                'image_path': folder + '/images/' + image_name
                            }
                        )
                                        )
        else:
            st.warning('Please Choose At Least One Folder')

    if parse_image_submitted_save:
        if selected_values:
            backend_method = 'parse_data_with_llm/load_images_descriptions'
            for folder in selected_values:
                data = post_to_backend(backend_method=backend_method,
                                       params={'prompt': prompt,
                                               'folder_name': folder})
                st.write(f'Load is finished for {folder}')
                st.write(data)
        else:
            st.warning('Please Choose At Least One Folder')


with parse_file_tab:
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
            for folder in selected_values:
                with st.expander(folder):
                    backend_method = \
                        's3_interactions/get_images_explanations_paths'
                    images_decriptions_paths = \
                        images = get_from_backend(
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
                    st.json(json.loads(parsed_json_stream[
                        parsed_json_stream.find('{'):]))
        else:
            st.warning('Please Choose At Least One Folder')

    if parse_file_submitted_save:
        if selected_values:
            for folder in selected_values:
                backend_method = \
                        's3_interactions/get_images_explanations_paths'
                images_decriptions_paths = \
                    images = get_from_backend(
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


with find_common_schema_tab:
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

    if find_common_schema_submitted_save:
        if selected_values:
            backend_method = 'parse_data_with_llm/load_common_schema'
            data = post_to_backend(backend_method=backend_method,
                                   params={'prompt': prompt,
                                           'folders': ','.join(selected_values)
                                           })
            st.write(data)
        else:
            st.warning('Please Choose At Least One Folder')


with view_common_schemas_tab:
    all_the_common_schemas_paths = \
        get_from_backend('s3_interactions/get_all_the_common_schemas',
                         folders=None if not selected_values
                         else ','.join(selected_values))
    common_schema_file = st.selectbox('Choose Common Schema File',
                                      all_the_common_schemas_paths)

    if st.button('See Common Schema'):
        common_schema_json = \
            get_from_backend('s3_interactions/get_common_schema_json',
                             common_schema_path=common_schema_file)
        st.title('Prompt')
        st.markdown(common_schema_json['prompt'])
        st.title('Files')
        for folder in common_schema_json['files']:
            st.write(folder)
            with st.popover("Parsed Markdown", icon="📄"):
                backend_method = 's3_interactions/get_markdown_with_images'
                parsed_markdown = get_from_backend(
                    backend_method=backend_method,
                    folder_path=folder)
                st.markdown(f"""{parsed_markdown}""",
                            unsafe_allow_html=True)
        st.title('Common Schema')
        st.json(common_schema_json['schema'])
