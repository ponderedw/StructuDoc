import os
import io


class S3Handler:
    def __init__(self):
        self._login = os.environ.get('AWS_ACCESS_KEY_ID')
        self._password = os.environ.get('AWS_SECRET_ACCESS_KEY')
        self.s3_type, self.s3_bucket = os.environ.get('SOURCE_BUCKET')\
            .split('/', 1)

    @property
    def s3_client(self):
        if self.s3_type == 'minio':
            from minio import Minio
            _login = os.environ.get('MINIO_LOGIN',
                                    os.environ.get('AWS_ACCESS_KEY_ID'))
            _password = os.environ.get('MINIO_PASSWORD',
                                       os.environ.get('AWS_SECRET_ACCESS_KEY'))
            s3_client = Minio(
                os.environ['MINIO_HOST'],
                _login,
                _password,
                secure=os.environ['MINIO_SECURE'].lower()
                in (1, 'true', 't')
            )
        return s3_client

    def put_object(self, key, file_bytes):
        if self.s3_type == 'minio':
            file_stream = io.BytesIO(file_bytes)
            parameters = {
                'bucket_name': self.s3_bucket,
                'object_name': key,
                'data': file_stream,
                'length': len(file_bytes)
            }
        self.s3_client.put_object(**parameters)

    def list_objects(self, **kwargs):
        if self.s3_type == 'minio':
            parameters = {
                'bucket_name': self.s3_bucket,
            } | kwargs
        objects = self.s3_client.list_objects(**parameters)
        if self.s3_type == 'minio':
            return [o._object_name for o in objects]

    def remove_all_files_indir(self, path):
        objects_to_remove = self.list_objects(prefix=path,
                                              recursive=True)
        for object_to_remove in objects_to_remove:
            if self.s3_type == 'minio':
                parameters = {
                    'bucket_name': self.s3_bucket,
                    'object_name': object_to_remove
                }
            self.s3_client.remove_object(**parameters)

    def get_object(self, object_key, local_filename=None):
        if self.s3_type == 'minio':
            file_extension = object_key.split('.')[-1]
            file_name = object_key.split('/')[-1].split('.')[0] + '.' \
                + file_extension
            if local_filename:
                file_name = local_filename + '.' + file_extension
            parameters = {
                    'bucket_name': self.s3_bucket,
                    'object_name': object_key,
                    'file_path': file_name
                        }
            self.s3_client.fget_object(**parameters)
            return file_name

    def get_object_bytes(self, object_key):
        if self.s3_type == 'minio':
            parameters = {
                    'bucket_name': self.s3_bucket,
                    'object_name': object_key
                    }
            response = self.s3_client.get_object(**parameters)
            return response.read()
