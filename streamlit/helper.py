import requests
import os
import streamlit as st


def remove_watermark():
    st.markdown("""
            <style>
                .stAppDeployButton {display:none; visibility: hidden;}
            </style>
        """, unsafe_allow_html=True)
    css = '''
    <style>
        [data-testid="stSidebar"]{
            min-width: 100px;
            max-width: 1200px;
            default-width: 600px;
        }
    </style>
    '''
    st.markdown(css, unsafe_allow_html=True)


def insert_path(tree, parts, path):
    node = tree
    for idx, part in enumerate(parts):
        found = next((
            child for child in node.get("children", [])
            if child["title"] == part),
                     None)
        if not found:
            found = {"title": part, "value": part
                     if idx+1 != len(parts) else path}
            node["children"] = node.get("children", [])
            node["children"].append(found)
        node = found


def build_tree(paths):
    tree = {"title": "root", "children": []}
    for path in paths:
        parts = path.strip().split("/")
        insert_path(tree, parts, path)
    return tree


def get_from_backend(backend_method: str,
                     **kwargs):
    response = requests.get(
        f'http://fastapi:8080/{backend_method}',
        headers={"x-access-token":
                 os.environ.get('FAST_API_ACCESS_SECRET_TOKEN')},
        params=kwargs)
    response.raise_for_status()
    data = response.json()
    return data


def get_from_backend_streaming(backend_method: str,
                               **kwargs):
    with requests.get(
        f'http://fastapi:8080/{backend_method}',
        stream=True,
        headers={"x-access-token":
                 os.environ.get('FAST_API_ACCESS_SECRET_TOKEN')},
        **kwargs
         ) as response:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                parsed_chunk = str(chunk, encoding="utf-8")
                yield parsed_chunk


def post_to_backend(backend_method: str,
                    **kwargs):
    response = requests.post(f'http://fastapi:8080/{backend_method}',
                             headers={
                                 "x-access-token":
                                     os.environ.get(
                                         'FAST_API_ACCESS_SECRET_TOKEN')},
                             stream=True, **kwargs)
    response.raise_for_status()
    data = response.json()
    return data
