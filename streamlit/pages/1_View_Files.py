from st_ant_tree import st_ant_tree
import streamlit as st
import requests
from helper import build_tree
import json

a = requests.get('http://localhost:8080/s3_interactions/get_all_the_folders')
data = a.json()
paths = [folder['folder_path'] for folder in data]

tree = build_tree(paths)['children']


def receive_images_and_their_bytes(folder_path):
    a = requests.get(
        'http://localhost:8080/s3_interactions/get_all_the_images',
        params={'folder_path': folder_path})
    data = a.json()
    # images = {k: base64.b64decode(v) for k, v in data.items()}
    images = {k: v for k, v in data.items()}
    return images


def receive_markdown(folder_path):
    a = requests.get(
        'http://localhost:8080/s3_interactions/get_markdown_with_images',
        params={'folder_path': folder_path})
    data = a.json()
    return data


def receive_images_descriptions_paths(folder_path):
    a = requests.get(
        'http://localhost:8080/s3_interactions/get_images_explanations_paths',
        params={'folder_path': folder_path})
    data = a.json()
    return data


def receive_images_descriptions(folder_path, description_path):
    a = requests.get(
        'http://localhost:8080/s3_interactions/get_images_explanation',
        params={'folder_path': folder_path,
                'description_path': description_path})
    data = a.json()
    return data


def receive_json_parsings_paths(folder_path):
    a = requests.get(
        'http://localhost:8080/s3_interactions/receive_json_parsings_paths',
        params={'folder_path': folder_path})
    data = a.json()
    return data


def receive_json_parsings(folder_path, parsing_path):
    a = requests.get(
        'http://localhost:8080/s3_interactions/receive_json_parsings',
        params={'folder_path': folder_path,
                'parsing_path': parsing_path})
    data = a.json()
    return data


selected_values = st_ant_tree(
    treeData=tree,
    treeCheckable=True,
    # allowClear=True,
    only_children_select=True
)
if selected_values is None:
    selected_values = []

for selected_value in selected_values:
    with st.expander(selected_value):
        with st.popover("Parsed Markdown", icon="📄"):
            parsed_markdown = receive_markdown(selected_value)
            print(parsed_markdown)
            st.markdown(f"""{parsed_markdown}""",
                        unsafe_allow_html=True)
        with st.popover("Images", icon="🖼️"):
            images = receive_images_and_their_bytes(selected_value)
            for image_name, image_bytes in images.items():
                st.markdown(f"""## {image_name}

![{image_name}](data:image/{image_name.split('.')[-1]};base64,{image_bytes})

                            """,
                            unsafe_allow_html=True)
        with st.popover("Images To Text", icon="📝"):
            images_decriptions_paths = \
                receive_images_descriptions_paths(selected_value)
            if not images_decriptions_paths:
                st.write("There aren't any images descriptions yet")
            else:
                option = st.selectbox(
                    "Choose a prompt:",
                    images_decriptions_paths
                )
                if option:
                    image_description = \
                        receive_images_descriptions(selected_value,
                                                    option)
                    st.json(json.loads(image_description))
        with st.popover("JSON Parsings", icon="🗂️"):
            json_parsings_paths = \
                receive_json_parsings_paths(selected_value)
            if not json_parsings_paths:
                st.write("There aren't any parsing JSON yet")
            else:
                option = st.selectbox(
                    "Choose a prompt:",
                    json_parsings_paths
                )
                if option:
                    json_parsings = \
                        receive_json_parsings(selected_value,
                                              option)
                    st.json(json.loads(json_parsings))
