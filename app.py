from Super_Wicked_File_Sharing_Service import create_app

"""
This script provides the necessary application instance for uwsgi
"""
app = create_app()

if __name__ == "__main__":
    app.run()
