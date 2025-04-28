import streamlit as st
from helper import build_tree
from helper import get_from_backend, \
    remove_watermark
from st_ant_tree import st_ant_tree
from helper_view_files_tab import get_view_files_tab
from helper_parse_image_tab import get_parse_image_tab
from helper_parse_file_tab import get_parse_file_tab
from helper_find_common_schema_tab import get_find_common_schema_tab
from helper_view_common_schemas_tab import get_view_common_schemas_tab

remove_watermark()


def sort_by_title(data):
    if not isinstance(data, list):
        return data
    result = []
    for item in data:
        new_item = item.copy()
        if 'children' in new_item and isinstance(new_item['children'], list):
            new_item['children'] = sort_by_title(new_item['children'])
        result.append(new_item)
    return sorted(result, key=lambda x: x.get('title', '').lower())


paths = get_from_backend(backend_method='s3_interactions/get_all_the_folders')
paths = [folder['folder_path'] for folder in paths]
tree = build_tree(paths)['children']
tree = sort_by_title(tree)

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
    get_view_files_tab(selected_values)

with parse_image_tab:
    get_parse_image_tab(selected_values)

with parse_file_tab:
    get_parse_file_tab(selected_values)

with find_common_schema_tab:
    get_find_common_schema_tab(selected_values)

with view_common_schemas_tab:
    get_view_common_schemas_tab(selected_values)
