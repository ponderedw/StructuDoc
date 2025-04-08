import streamlit as st
from helper import get_from_backend, post_to_backend


with st.form("user_form"):
    file_to_upload = st.file_uploader("Upload File",
                                      type=['docx'])
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
            fine_to_delete = st.form_submit_button("Yes, I want to delete")
        else:
            fine_to_delete = True


if submitted or fine_to_delete:
    if file_to_upload:
        if fine_to_delete:
            output = post_to_backend(
                backend_method='s3_interactions/upload_source_file_to_s3',
                files={'file': file_to_upload},
                data={'path': path})
            st.write(output)
    else:
        st.warning("Please upload files before submitting")
