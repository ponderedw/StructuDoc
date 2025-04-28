import streamlit as st
from helper import get_from_backend, post_to_backend, remove_watermark, \
    build_tree
from st_ant_tree import st_ant_tree


remove_watermark()

option = st.selectbox(
    "Do you want upload a new file or choose one from s3 bucket?",
    ("Upload New File", "Choose File to Parse")
)

if option == 'Upload New File':
    with st.form("user_form"):
        file_to_upload = st.file_uploader("Upload File",
                                          type=['docx', 'pdf'])
        path = st.text_input("S3 Path")
        submitted = st.form_submit_button("Submit")
        fine_to_delete = False
        if file_to_upload:
            does_exists = get_from_backend(
                backend_method='s3_interactions/is_folder_exists',
                file_name=file_to_upload.name,
                path=path)
            if does_exists['is_exist']:
                fine_to_delete = st.warning(f'''This folder already exists.
                                Are you sure you want to delete this item?
                                {does_exists['folder_path']}''')
                fine_to_delete = \
                    st.form_submit_button("Yes, I want to delete")
            else:
                fine_to_delete = True

    if submitted or fine_to_delete:
        if file_to_upload:
            if fine_to_delete:
                backend_method = 's3_interactions/upload_source_file_to_s3'
                output = post_to_backend(
                    backend_method=backend_method,
                    files={'file': file_to_upload},
                    data={'path': path})
                st.write(output)
        else:
            st.warning("Please upload files before submitting")

else:
    with st.form("user_form"):
        backend_method = 's3_interactions/get_files_list'
        paths = get_from_backend(backend_method=backend_method,
                                 extensions='.docx,.pdf')
        tree = build_tree(paths)['children']
        selected_values = st_ant_tree(
                treeData=tree,
                treeCheckable=True,
                allowClear=False,
                only_children_select=True,
                placeholder='Choose Files',
            )
        submit = st.form_submit_button('Submit')

    if submit:
        if selected_values:
            for file in selected_values:
                st.title(file)
                output = post_to_backend(
                    backend_method='s3_interactions/parse_s3_path',
                    params={'path': file})
                st.write(output)
        else:
            st.warning("Please upload files before submitting")
