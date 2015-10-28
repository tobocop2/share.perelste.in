from flask import Blueprint, request, make_response, abort, jsonify
from flask import current_app as app
from ..extensions import db
from ..tasks import delete_file
from .models import File
import mimetypes
import os

api = Blueprint('api', __name__, url_prefix='/api/v1.0')


@api.route('/', methods=['GET', 'POST'])
def index():
    """Print available routes."""
    func_list = {}
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            func_list[rule.rule] = app.view_functions[rule.endpoint].__doc__
    return jsonify(func_list)


@api.route('/file', methods=['PUT'])
def upload_file():
    """This endpoint is used to upload a file via PUT request."""
    # @params:
    #     file *REQUIRED
    #     password *OPTIONAL
    # @Response JSON
    #

    # if no file is sent with the request, return Bad Request
    if not request.files:
        abort(400)

    password = request.form.get('password')

    try:
        file_key = list(request.files.keys())[0]
        new_file_obj = request.files[file_key]
    except IndexError:
        abort(400)

    # Add a file record to the database and set its password
    # if submitted with the request
    filename = new_file_obj.filename
    new_file_record = File.add_file(filename, password)

    # Build path based on the new filehash in order
    # to save on the filesystem
    new_path = '%s/%s' % (app.config['UPLOAD_FOLDER'],
                          new_file_record.filehash)
    if not os.path.exists(new_path):
        os.makedirs(new_path)

    new_file_obj.save(os.path.join(new_path, filename))

    response = {
        "status": "File Uploaded Successfully",
        "url": "%s%s/file/%s/%s" % (request.url_root,
                                    api.url_prefix.lstrip('/'),
                                    new_file_record.filehash,
                                    new_file_record.filename)
    }
    return jsonify(response), 201


@api.route('/file/<filehash>/<filename>', methods=['GET'])
def download_file(filehash, filename):
    """This endpoint is used to download a file via GET request."""
    # @url params:
    #     filehash *REQUIRED
    # @query params:
    #     password *OPTIONAL
    # @Response JSON
    #

    # Fine file record based on the filehash in the url
    file_obj = File.query.filter_by(filehash=filehash).first()
    password = request.args.get('password')

    # If the file doesn't exist, return not found error
    # If the file has been downloaded already, return Gone error
    # If the authentication is incorrect, return Unauthorized
    if not file_obj:
        abort(404)

    elif file_obj.status == 'Gone':
        abort(410)

    elif file_obj.password and not password:
        abort(401)

    elif password and not file_obj.validate_password(password):
        abort(401)

    # Set the file status to Gone for next request
    file_obj.status = 'Gone'
    db.session.commit()

    filename = file_obj.filename
    filehash = file_obj.filehash
    # Get mimetype of file so that nginx can serve it properly
    mimetype = mimetypes.guess_type(filename)[0]

    # specify nginx redirect path that is aliased to local directory
    redirect_path = "/api/v1.0/files/%s/%s" % (filehash, filename)

    response = make_response("")
    # Send redirect path with this header as well as calculated mimetype
    response.headers["X-Accel-Redirect"] = redirect_path
    response.headers["Content-Type"] = mimetype

    # Delete file asynchronously from the filesystem and return the file
    # Countdown param is set to delete the file from the system 10 seconds
    # after its in the Celery task queue.
    delete_file.apply_async(args=[filehash], countdown=10)

    return response
