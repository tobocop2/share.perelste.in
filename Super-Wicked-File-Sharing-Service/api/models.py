from ..extensions import db
from hashlib import sha256, md5
import datetime
import os


class File(db.Model):

    __tablename__ = 'file'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255))
    filehash = db.Column(db.String(128))
    password = db.Column(db.String(255))
    created_at = db.Column(db.DateTime,
                           default=datetime.datetime.utcnow)
    status = db.Column(db.Enum('Gone', 'Available', name='statuses'),
                       default='Available')

    @staticmethod
    def add_file(filename, password=None):
        """
        Creates a new file record with hashed password if
        set and hashes the filename
        """
        new_file = File(filename=filename)

        if password:
            new_file._set_password(password)

        new_file._set_filehash(filename)

        db.session.add(new_file)
        db.session.commit()
        return new_file

    @classmethod
    def _hash_password(cls, password):
        """
        Creates password hash using sha256 + original password
        """
        salt = sha256()
        salt.update(os.urandom(60))
        salt = salt.hexdigest()

        hash = sha256()
        # Make sure password is a str because we cannot hash unicode objects
        hash.update((password + salt).encode('utf-8'))
        hash = hash.hexdigest()

        password = salt + hash

        return password

    @classmethod
    def _hash_filename(cls, filename):
        """
        Creates filename hash using md5 + current utc time
        """

        hash = md5()
        hash.update(filename.encode('utf-8')+str(datetime.datetime.utcnow()))
        hash = hash.hexdigest()
        return hash

    def _set_password(self, password):
        """
        Setter for the hashed password
        """
        self.password = self._hash_password(password)
        db.session.commit()

    def _get_password(self):
        """
        Getter for the hashed password
        """
        return self.password

    def validate_password(self, password):
        """
        Check the password against existing credentials.
        Using the password param, a hash is generated and
        a comparison is made between the last 64 characters
        of the files password hash and the first 64 characters of
        the newly created hash

        """
        hash = sha256()
        hash.update((password + self.password[:64]).encode('utf-8'))
        return self.password[64:] == hash.hexdigest()

    def _set_filehash(self, filename):
        """
        Setter for the hashed filename
        """
        self.filehash = self._hash_filename(filename)
        db.session.commit()

    def _get_filehash(self):
        """
        Getter for the hashed filename
        """
        return self.filehash

    def __repr__(self):
        return '<File ID%r>' % self.id
