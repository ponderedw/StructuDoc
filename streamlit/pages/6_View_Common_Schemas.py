from helper import get_from_backend, build_tree
import streamlit as st
from st_ant_tree import st_ant_tree


paths = get_from_backend(backend_method='s3_interactions/get_all_the_folders')
paths = [folder['folder_path'] for folder in paths]
tree = build_tree(paths)['children']

selected_values = st_ant_tree(
    treeData=tree,
    treeCheckable=True,
    allowClear=True,
    only_children_select=True,
    placeholder='Choose Files You Want to Parse'
)
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
            parsed_markdown = get_from_backend(backend_method=backend_method,
                                               folder_path=folder)
            st.markdown(f"""{parsed_markdown}""",
                        unsafe_allow_html=True)
    st.title('Common Schema')
    st.json(common_schema_json['schema'])
