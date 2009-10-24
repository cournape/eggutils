import zipfile
import re
import os
import sys

from distutils.util import rfc822_escape

# Copied from pkg_resources (setuptools 0.6.9c)
PY_MAJOR = sys.version[:3]

def get_build_platform():
    """Return this platform's string for platform-specific distributions

    XXX Currently this is the same as ``distutils.util.get_platform()``, but it
    needs some hacks for Linux and Mac OS X.
    """
    from distutils.util import get_platform
    plat = get_platform()
    if sys.platform == "darwin" and not plat.startswith('macosx-'):
        try:
            version = _macosx_vers()
            machine = os.uname()[4].replace(" ", "_")
            return "macosx-%d.%d-%s" % (int(version[0]), int(version[1]),
                _macosx_arch(machine))
        except ValueError:
            # if someone is running a non-Mac darwin system, this will fall
            # through to the default implementation
            pass
    return plat

def to_filename(name):
    """Convert a project or version name to its filename-escaped form

    Any '-' characters are currently replaced with '_'.
    """
    return name.replace('-','_')

def egg_name(project_name, version, py_version=None, platform=False):
    """Return what this distribution's standard .egg filename should be"""
    basename = "%s-%s-py%s" % (
        to_filename(project_name), to_filename(version),
        py_version or PY_MAJOR
        )

    if platform:
        basename += '-' + get_build_platform()

    return basename + ".egg"

# end of setuptools copy

# Metadata:
#  - Metadata-Version
#  - Name
#  - Version (should be parseable by LooseVersion or StrictVersion)
#  - Summary: one line summary
#  - Description: multi line description (optional)
#  - Keywords: comma separated list (optional)
#  - Home-Page: url (optional)
#  - Author (optional)
#  - Author-email (optional)
#  - License
#  - Download-Url (optional)
#  - Platform: comma separated list
#  - Classifier: trove
# 1.1 (PEP 314)
#  - Requires
#  - Provides
#  - Obsoletes
class MetaData(object):
    def __init__(self, name, version=None, summary=None, description=None,
                 url=None, author=None, author_email=None, license=None,
                 download_url=None, keywords=None, platforms=None):
        self.name = name
        self.version = version
        self.summary = summary
        self.description = description
        if not keywords:
            self.keywords = []
        else:
            self.keywords = keywords
        self.url = url
        self.author = author
        self.author_email = author_email
        self.license = license
        self.download_url = download_url
        if not platforms:
            self.platforms = []
        else:
            self.platforms = platforms

        self.requires = []
        self.provides = []
        self.obsoletes = []

def write_pkg_file (file, metadata):
    """Write the PKG-INFO format data to a file object.
    """
    version = '1.0'
    if metadata.provides or metadata.requires or metadata.obsoletes:
        version = '1.1'

    _write_field(file, 'Metadata-Version', version)
    _write_field(file, 'Name', metadata.name or "UNKNOWN")
    _write_field(file, 'Version', metadata.version or "UNKNOWN")
    _write_field(file, 'Summary', metadata.description or "UNKNOWN")
    _write_field(file, 'Home-page', metadata.url or "UNKNOWN")
    _write_field(file, 'Author', metadata.contact or "UNKNOWN")
    _write_field(file, 'Author-email', metadata.contact_email or "UNKNOWN")
    _write_field(file, 'License', metadata.license or "UNKNOWN")
    if metadata.download_url:
        _write_field(file, 'Download-URL', metadata.download_url or "UNKNOWN")

    # long_desc = rfc822_escape( self.get_long_description())
    # _write_field(file, 'Description', long_desc)

    # keywords = string.join( self.get_keywords(), ',')
    # if keywords:
    #     _write_field(file, 'Keywords', keywords)

    # _write_list(file, 'Platform', self.get_platforms())
    # _write_list(file, 'Classifier', self.get_classifiers())

    # # PEP 314
    # _write_list(file, 'Requires', self.get_requires())
    # _write_list(file, 'Provides', self.get_provides())
    # _write_list(file, 'Obsoletes', self.get_obsoletes())

def _write_field(file, name, value):

    if isinstance(value, unicode):
        value = value.encode(PKG_INFO_ENCODING)
    else:
        value = str(value)
    file.write('%s: %s\n' % (name, value))

def _write_list (file, name, values):

    for value in values:
        _write_field(file, name, value)

_RE_NAME = re.compile("Name\s*:\s*([a-zA-Z0-9_\-]+)")
_RE_VERSION = re.compile("Version\s*:\s*([a-zA-Z0-9_\-\.]+)")

def main(files, metadata, py_version=None):
    def read_meta():
        ret = {}
        f = open(metadata)
        try:
            cnt = f.readlines()
            for line in cnt:
                m = _RE_NAME.match(line)
                if m:
                    ret["name"] = m.group(1)
                    break

            for line in cnt:
                m = _RE_VERSION.match(line)
                if m:
                    ret["version"] = m.group(1)
                    break

        finally:
            f.close()

        return ret

    parsed = read_meta()
    filename = egg_name(parsed["name"], parsed["version"], py_version,
                        platform=True)
    egg = zipfile.ZipFile(filename, "w", zipfile.ZIP_DEFLATED)

    try:
        b = os.path.basename(metadata)
        egg.write(metadata, "EGG-INFO/PKG-INFO")

        for f in files:
            b = os.path.basename(f)
            egg.write(f, "EGG-INFO/scripts/" + b)
    finally:
        egg.close()

def wrap_main():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-m", "--meta-data", dest="metadata",
                      help="PKG-INFO file for metadata")
    parser.add_option("-p", "--python-version", dest="py_version",
                      help="Python version the egg should target (major.minor " \
                           "only)")

    (options, args) = parser.parse_args()

    if options.metadata:
        if options.py_version:
            py_version = options.py_version
        else:
            py_version = PY_MAJOR
        main(args, options.metadata, py_version)

if __name__ == "__main__":
    pass
    #dll_files = ["/usr/lib/libkrb5support.dylib"]
    #meta = {"name": "mkl-ia32-static", 
    #    "version": "11.1.048"}

    #egg = zipfile.ZipFile(meta["name"] + ".egg", "w", zipfile.ZIP_DEFLATED)

    #try:
    #    pkg = StringIO.StringIO()
    #    write_pkg_file(pkg, MetaData(**meta))
    #    egg.writestr("EGG-INFO/PKG-INFO", pkg.getvalue())

    #    for f in dll_files:
    #        b = os.path.basename(f)
    #        egg.write(f, "EGG-INFO/scripts/" + b)
    #finally:
    #    egg.close()
