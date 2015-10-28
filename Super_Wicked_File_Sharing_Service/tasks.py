from .extensions import celery
from .config import DefaultConfig
import shutil


@celery.task
def delete_file(filehash):
    """
    Given the filehash parameter, the directory with the filehash is
    recursively deleted. This is called asynchronously so that the download
    request is not blocked by this operation
    """
    delete_path = '%s/%s' % (DefaultConfig.UPLOAD_FOLDER,
                             filehash)
    shutil.rmtree(delete_path)
