import os
import sys
import tempfile

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from line import Line


class Fstab(object):
    """An /etc/fstab file."""

    def __init__(self):
        self.lines = []

    def open_file(self, filespec, mode):
        if isinstance(filespec, str):
            return open(filespec, mode=mode)
        else:
            return filespec

    def close_file(self, f, filespec):
        if isinstance(filespec, str):
            f.close()

    def get_perms(self, filename):
        return os.stat(filename).st_mode  # pragma: no cover

    def chmod_file(self, filename, mode):
        os.chmod(filename, mode)  # pragma: no cover

    def link_file(self, oldname, newname):
        if os.path.exists(newname):
            os.remove(newname)
        os.link(oldname, newname)

    def rename_file(self, oldname, newname):
        os.rename(oldname, newname)  # pragma: no cover

    def read(self, filespec):
        """Read in a new file.

        If filespec is a string, it is used as a filename. Otherwise
        it is used as an open file.

        The existing content is replaced.

        """

        f = self.open_file(filespec, "r")
        lines = []
        for line in f:
            lines.append(Line(line))
        self.lines = lines
        self.close_file(filespec, f)

    def write(self, filespec):
        """Write out a new file.

        If filespec is a string, it is used as a filename. Otherwise
        it is used as an open file.

        """

        if isinstance(filespec, str):
            # We create the temporary file in the directory (/etc) that the
            # file exists in. This is so that we can do an atomic rename
            # later, and that only works inside one filesystem. Some systems
            # have /tmp and /etc on different filesystems, for good reasons,
            # and we need to support that.
            dirname = os.path.dirname(filespec)
            prefix = os.path.basename(filespec) + "."
            fd, tempname = tempfile.mkstemp(dir=dirname, prefix=prefix)
            os.close(fd)
        else:
            tempname = filespec

        f = self.open_file(tempname, "w")
        for line in self.lines:
            f.write(line.raw)
        self.close_file(filespec, f)

        if isinstance(filespec, str):
            self.chmod_file(tempname, self.get_perms(filespec))
            self.link_file(filespec, filespec + ".bak")
            self.rename_file(tempname, filespec)
