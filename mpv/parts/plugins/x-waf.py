
import os
import shutil

import snapcraft

class WafPlugin(snapcraft.BasePlugin):

    @classmethod
    def schema(cls):
        schema = super().schema()
        schema['properties']['configflags'] = {
            'type': 'array',
            'minitems': 1,
            'uniqueItems': True,
            'items': {
                'type': 'string',
            },
            'default': [],
        }

        # Inform Snapcraft of the properties associated with building. If these
        # change in the YAML Snapcraft will consider the build step dirty.
        schema['build-properties'].append('configflags')

        return schema

    def __init__(self, name, options, project):
        super().__init__(name, options, project)
        self.build_packages.extend(['make'])

    def build(self):
        super().build()
#        if os.path.exists(self.builddir):
#            shutil.rmtree(self.builddir)
#        os.mkdir(self.builddir)

#        source_subdir = getattr(self.options, 'source_subdir', None)
#        if source_subdir:
#            sourcedir = os.path.join(self.sourcedir, source_subdir)
#        else:
#            sourcedir = self.sourcedir

        env = self._build_environment()
        # Run bootstrap.py to download waf binary
        self.run(['./bootstrap.py'], env=env)

        # Run waf to configure
        print(env)
        self.run(['./waf', '-v', 'configure', '--prefix=/usr/local'], env=env)

        # Run waf to build the sources
        self.run(['./waf', '-v'], env=env)

        # Install
        self.run(['./waf', '-v', 'install', '--destdir=' + self.installdir], env=env)

    def _build_environment(self):
        env = os.environ.copy()
        env['QT_SELECT'] = '5'
        env['LFLAGS'] = '-L ' +  ' -L'.join(
            ['{0}/lib', '{0}/usr/lib', '{0}/lib/{1}',
             '{0}/usr/lib/{1}']).format(
                self.project.stage_dir, self.project.arch_triplet)
        env['INCDIRS'] =  ':'.join(
            ['{0}/include', '{0}/usr/include', '{0}/include/{1}',
             '{0}/usr/include/{1}']).format(
                self.project.stage_dir, self.project.arch_triplet)
        env['CPATH'] = ':'.join(
            ['{0}/include', '{0}/usr/include', '{0}/include/{1}',
             '{0}/usr/include/{1}']).format(
                self.project.stage_dir, self.project.arch_triplet)
        env['LIBRARY_PATH'] = '$LD_LIBRARY_PATH:' + ':'.join(
            ['{0}/lib', '{0}/usr/lib', '{0}/lib/{1}',
             '{0}/usr/lib/{1}']).format(
                self.project.stage_dir, self.project.arch_triplet)
        return env
