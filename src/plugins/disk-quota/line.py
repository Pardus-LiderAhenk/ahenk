import re


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
