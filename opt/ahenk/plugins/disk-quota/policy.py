#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:Mine DOGAN <mine.dogan@agem.com.tr>

import os
import re
import tempfile
import json

from base.plugin.abstract_plugin import AbstractPlugin


class DiskQuota(AbstractPlugin):
    def __init__(self, data, context):
        super(AbstractPlugin, self).__init__()
        self.data = data
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

        self.username = self.context.get('username')

        self.mount = 'mount -o remount {}'
        self.quotaon_all = 'quotaon --all'
        self.quotaon_avug = 'quotaon -avug'
        self.set_quota = 'setquota --always-resolve -u {0} {1} {2} 0 0 --all'

        self.parameters = json.loads(self.data)

        self.soft_quota = str(int(self.parameters['soft-quota']) * 1024)
        self.hard_quota = str(int(self.parameters['hard-quota']) * 1024)

        self.logger.debug('Parameters were initialized.')

    def handle_policy(self):
        self.logger.debug('Policy handling...')
        try:
            # Check fstab & append 'usrquota' option if not exists
            fs = Fstab()
            fs.read('/etc/fstab')
            fstab_entries = []
            fslines = fs.lines
            for line in fslines:
                if line.has_filesystem() and 'usrquota' not in line.options:
                    if line.dict['directory'] == '/' or line.dict['directory'] == '/home/':
                        self.logger.debug('Appending \'usrquota\' option to {}'.format(line.dict['directory']))
                        line.options += ['usrquota']
                        fstab_entries.append(line.dict['directory'])
            fs.write('/etc/fstab')

            # Re-mount necessary fstab entries
            for entry in fstab_entries:
                self.execute(self.mount.format(entry))
                self.logger.debug('Remounting fstab entry {}'.format(entry))

            self.execute(self.quotaon_all)
            self.logger.debug('{}'.format(self.quotaon_all))

            self.execute(self.quotaon_avug)
            self.logger.debug('{}'.format(self.quotaon_avug))

            self.execute(self.set_quota.format(self.username, self.soft_quota, self.hard_quota))
            self.logger.debug(
                'Set soft and hard quota. Username: {0}, Soft Quota: {1}, Hard Quota: {2}'.format(self.username,
                                                                                                  self.soft_quota,
                                                                                                  self.hard_quota))

            self.context.create_response(code=self.get_message_code().POLICY_PROCESSED.value,
                                         message='Kotalar başarıyla güncellendi.')

        except Exception as e:
            self.logger.error('[DiskQuota] A problem occurred while handling browser profile: {0}'.format(str(e)))
            self.context.create_response(code=self.get_message_code().POLICY_ERROR.value,
                                         message='Disk Quota profili uygulanırken bir hata oluştu.')


class Line(object):
    """A line in an /etc/fstab line.

      Lines may or may not have a filesystem specification in them. The
      has_filesystem method tells the user whether they do or not; if they
      do, the attributes device, directory, fstype, options, dump, and
      fsck contain the values of the corresponding fields, as instances of
      the sub-classes of the LinePart class. For non-filesystem lines,
      the attributes have the None value.

      Lines may or may not be syntactically correct. If they are not,
      they are treated as as non-filesystem lines.

      """

    # Lines split this way to shut up coverage.py.
    attrs = ("ws1", "device", "ws2", "directory", "ws3", "fstype")
    attrs += ("ws4", "options", "ws5", "dump", "ws6", "fsck", "ws7")

    def __init__(self, raw):
        self.dict = {}
        self.raw = raw

    def __getattr__(self, name):
        if name in self.dict:
            return self.dict[name]
        else:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        forbidden = ("dict", "dump", "fsck", "options")
        if name not in forbidden and name in self.dict:
            if self.dict[name] is None:
                raise Exception("Cannot set attribute %s when line dies not "
                                "contain filesystem specification" % name)
            self.dict[name] = value
        else:
            object.__setattr__(self, name, value)

    def get_dump(self):
        return int(self.dict["dump"])

    def set_dump(self, value):
        self.dict["dump"] = str(value)

    dump = property(get_dump, set_dump)

    def get_fsck(self):
        return int(self.dict["fsck"])

    def set_fsck(self, value):
        self.dict["fsck"] = str(value)

    fsck = property(get_fsck, set_fsck)

    def get_options(self):
        return self.dict["options"].split(",")

    def set_options(self, list):
        self.dict["options"] = ",".join(list)

    options = property(get_options, set_options)

    def set_raw(self, raw):
        match = False

        if raw.strip() != "" and not raw.strip().startswith("#"):
            pat = r"^(?P<ws1>\s*)"
            pat += r"(?P<device>\S*)"
            pat += r"(?P<ws2>\s+)"
            pat += r"(?P<directory>\S+)"
            pat += r"(?P<ws3>\s+)"
            pat += r"(?P<fstype>\S+)"
            pat += r"(?P<ws4>\s+)"
            pat += r"(?P<options>\S+)"
            pat += r"(?P<ws5>\s+)"
            pat += r"(?P<dump>\d+)"
            pat += r"(?P<ws6>\s+)"
            pat += r"(?P<fsck>\d+)"
            pat += r"(?P<ws7>\s*)$"

            match = re.match(pat, raw)
            if match:
                self.dict.update((attr, match.group(attr)) for attr in self.attrs)

        if not match:
            self.dict.update((attr, None) for attr in self.attrs)

        self.dict["raw"] = raw

    def get_raw(self):
        if self.has_filesystem():
            return "".join(self.dict[attr] for attr in self.attrs)
        else:
            return self.dict["raw"]

    raw = property(get_raw, set_raw)

    def has_filesystem(self):
        """Does this line have a filesystem specification?"""
        return self.device is not None


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


def handle_policy(profile_data, context):
    dq = DiskQuota(profile_data, context)
    dq.handle_policy()

