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
        elif self.s3_type == 's3':
            import boto3
            s3_client = boto3.client(
                's3',
                region_name=os.environ['AWS_REGION']
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
        elif self.s3_type == 's3':
            parameters = {
                'Bucket': self.s3_bucket,
                'Key': key,
                'Body': file_bytes
            }
        self.s3_client.put_object(**parameters)

    def list_objects(self, **kwargs):
        if self.s3_type == 'minio':
            parameters = {
                'bucket_name': self.s3_bucket,
            } | kwargs
        elif self.s3_type == 's3':
            kwargs.pop('recursive', None)
            if kwargs.get('prefix'):
                kwargs['Prefix'] = kwargs.pop('prefix')
            parameters = {
                'Bucket': self.s3_bucket,
            } | kwargs
        objects = self.s3_client.list_objects(**parameters)
        if self.s3_type == 'minio':
            return [o.object_name for o in objects]
        elif self.s3_type == 's3':
            return [o['Key'] for o in objects.get('Contents', [])]
        return objects

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
            elif self.s3_type == 's3':
                parameters = {
                    'Bucket': self.s3_bucket,
                    'Key': object_to_remove
                }
                self.s3_client.delete_object(**parameters)

    def get_object(self, object_key, local_filename=None):
        file_extension = object_key.split('.')[-1]
        file_name = object_key.split('/')[-1].split('.')[0] + '.' \
            + file_extension
        if local_filename:
            file_name = local_filename + '.' + file_extension
        if self.s3_type == 'minio':
            parameters = {
                    'bucket_name': self.s3_bucket,
                    'object_name': object_key,
                    'file_path': file_name
                        }
            self.s3_client.fget_object(**parameters)
        elif self.s3_type == 's3':
            with open(file_name, 'wb') as data:
                self.s3_client.download_fileobj(
                    self.s3_bucket, object_key, data)
        return file_name

    def get_object_bytes(self, object_key):
        if self.s3_type == 'minio':
            parameters = {
                    'bucket_name': self.s3_bucket,
                    'object_name': object_key
                    }
            response = self.s3_client.get_object(**parameters)
            return response.read()
        elif self.s3_type == 's3':
            buffer = io.BytesIO()
            self.s3_client.download_fileobj(
                self.s3_bucket, object_key, buffer)
            buffer.seek(0)
            return buffer.read()
