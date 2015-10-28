README
===================

About
-----
I wanted to build an application that lets users anonymously share files without any sort of account registration.
This started off simply as an upload server for a coding challenge, but I wound up having a lot of fun with it and decided that it was 
time to make my idea a reality. At the moment the application works like Snapchat where all files are deleted after they are downloaded.
I may change files to have expiration times or maybe maximum download times. Files can be password protected by the api, but this functionality is
not currently implemented in the user facing application.

Production
-------------
The application is currently a WIP and is available for testing with BASE URL:

[http://tobias.perelste.in:8002](http://tobias.perelste.in:8002)

For those that would like to use the api, the base url is here:

[http://tobias.perelste.in:8002/api/v1.0/](http://tobias.perelste.in:8002/api/v1.0/)

Overall API usage is documented at the bottom of this README.


Specs/Tech
-------------

The api is built with python on top of flask. It is served with uwsgi under nginx. 
I used PostgreSQL for persistent  data storage and Redis caching all 4XX status code responses. I used Postgres to set up simple single table database which stores all information relevant to a file upload such as filename, filehash, password if supplied, created date.

Additionally, I am using a Celery as a task queue for handling file deletion asynchronously so that the download requests are faster. In addition to the Redis instance I'm using for caching, I also set up a Redis instance as a backend for the Celery task queue which is used for permanently removing files off of the file system after they are downloaded. 

I used both Flask Sql Alchemy and Flask Migrate (built on top of Alembic) flask extensions to build and manage the database migrations as well. 

I configured the flask app to be run with Uwsgi and Nginx.  

Design/Decisions
-------------------
I chose the factory pattern for creating the flask app instantiation due to
its ease of flexibilty, extensibility and modularity. I know that this application only
has two endpoints at the moment, but I designed it with big things in mind. Currently, the application is divided into two modules (api and frontend). The api module contains the database models and api controllers and the frontend module controller simply renders the main page and all static content.

The main module exposes all the extensions that are used throughout the application.

All files are not served by Flask but by nginx since nginx is tremendously faster than flask and is much better for serving static content.  In order to do this, I needed flask to send a specific header which provides a redirect to nginx, which in turn is aliases to a directory on the filesystem. This way, flask does not have anything to do with the file serving and is only used for application logic. 

Models
----------------
**File**

The File model represents the file that is being uploaded/downloaded. The file model provides information such as the filename, unique filehash, creation time, and status (whether it's available for download or gone). In order to be able to store a file uniquely for each request, I hashed each file name with its creation time using the MD5 hash algorithm and I then created a folder on the filesystem with this hash. Inside this folder, I store the original file with its original name
intact for download. This hash is also used for retrieving the file from the file system when visiting the download endpoint. 

The file model contains several methods as well, mainly for password hashing/verification, and file hashing. IF a user supplies a password, this password is hashed using sha256. If a user needs to download a password protected file, the password they supply with the GET request is validated by the validate_password method in the file class 



API Controllers
--------------
The main api controller is where the bulk of the application logic occurs. 

A request comes into my api. The parameters get processed by the
/file endpoints. The allowed methods for the api are PUT and GET 

Upon sending a PUT request, I verify to see if there is a file sent with the request at all. If not, I return a 400 Bad Request error.

Regardless of whether or not a password is sent, I take the form value for the password key and send it off to the add_file method of the File class which is a static method. This method creates a new file record in the database and performs all the necessary options such as hashing the password if it exists, creating the filehash, etc. The file is then written to the filesystem and a 201 success response is returned containing a success message as well as a download url for the GET
request

Upon sending a GET request to the url that is returned from the PUT, the filehash in the url is verified and the password is validated if the file is password protected. If the file is not found a 404 response is returned. If, the file is no longer available, a 410 response is returned. if the file is password protected but no password was sent, a 401 response is returned, and if the password is incorrect, a 401 response is returned. If all goes well, the file hash is verified
against the database and the file is found on the filesystem. The mimetype is found from the file using the built in python mimetype library and the response is returned. 

API OVERVIEW
------------
# API BASE URL
http://tobias.perelste.in:8002/api/v1.0/

# PUT
## Upload File [/file] 
This endpoint allows you to upload a file with an optional password. Only allowed method is PUT so a 405 will be returned for other request methods.
* NOTE: The endpoint allows for a maximum file size of 16 megs. The web server will return a 413: Request Entity too Large for anything larger. 

### params
        file - the file being sent *REQUIRED
        password - the password for the file *OPTIONAL


#### Python example request to upload a photo
```python
import requests

# If no password is set during upload, do not have to send data dictionary
# with the request. The data dictionary acts as the form data

url = 'http://tobias.perelste.in:8002/api/v1.0/file'

files = {'file': open('report.xls', 'rb')}
data = {'password': 'hello world'}
res = requests.put(url, files=files, data=data)
```
### Upload photo [PUT]

### Possible Responses

+ Response 201 (application/json)

        {
            "status": "File Uploaded Successfully",
            "url": "http://tobias.perelste.in:8002/api/v1.0/file/d1c5b168e5782c80fe36f601a9df3b47"
        }
+ Response 400 (application/json)

        {
            "error" : "Bad Request"
        }

+ Response 404 (application/json)

        {
            "error" : "Not Found"
        }
+ Response 405 (application/json)

        {
            "error" : "Method not Allowed"
        }

# GET
## Download File[/file/filehash]
This endpoint allows you to retrieve a file based on its hash. 


### url params
        filehash - the MD5 hash generated from the PUT request.
### query string params
        password - the password for the file *OPTIONAL

#### Python example request to download a file
```python
import requests
# If no password was set during upload, do not have to send params dictionary
# with the request

url = 'http://tobias.perelste.in:8002/api/v1.0/file/d1c5b168e5782c80fe36f601a9df3b47'

params = {'password': 'hello world'}

res = requests.get(url, params=params)
```
### Download File[GET]

### Possible Responses

+ Response 200 (original content type)

+ Response 400 (application/json)

        {
            "error" : "Bad Request"
        }

+ Response 404 (application/json)

        {
            "error" : "Not Found"
        }
+ Response 405 (application/json)

        {
            "error" : "Method not Allowed"
        }
        
+ Response 410 (application/json)

        {
            "error" : "Gone"
        }
        
To Do
-----
Need to implement asynchronous file saving as well as web socket communication with the client to
monitor file saving progress.
