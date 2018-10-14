#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os


class ImageMagicConan(ConanFile):
    name = "imagemagick"
    version = "7.0.8-10"
    description = "ImageMagick is a free and open-source software suite for displaying, converting, and editing raster image and vector image files"
    url = "https://github.com/bincrafters/conan-imagemagic"
    homepage = "https://imagemagick.org"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "ImageMagick"
    exports = ["LICENSE.md"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "hdri": [True, False],
               "quantum_depth": [8, 16, 32]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "hdri": True,
                       "quantum_depth": 16}

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        source_url = "https://github.com/ImageMagick/ImageMagick"
        tools.get("{0}/archive/{1}.tar.gz".format(source_url, self.version))
        extracted_dir = "ImageMagick-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        with tools.chdir(self._source_subfolder):
            env_build = AutoToolsBuildEnvironment(self)
            args = ['--disable-openmp',
                    '--disable-docs',
                    '--with-utilities=no',
                    '--with-perl=no',
                    '--without-zlib'
                    ]
            if self.options.shared:
                args.extend(['--enable-shared=yes', '--enable-static=no'])
            else:
                args.extend(['--enable-shared=no', '--enable-static=yes'])
            args.append('--enable-hdri=yes' if self.options.hdri else '--enable-hdri=no')
            args.append('--with-quantum-depth=%s' % self.options.quantum_depth)
            env_build.configure(args=args)
            env_build.make()
            env_build.install()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)

    @property
    def _major(self):
        return self.version.split('.')[0]

    def _libname(self, library):
        suffix = 'HDRI' if self.options.hdri else ''
        return '%s-%s.Q%s%s' % (library, self._major, self.options.quantum_depth, suffix)

    def package_info(self):
        self.cpp_info.includedirs = [os.path.join('include', 'ImageMagick-%s' % self._major)]
        self.cpp_info.libs = [self._libname('MagickCore'),
                              self._libname('MagickWand'),
                              self._libname('Magick++')]
        if self.settings.os == 'Linux':
            self.cpp_info.libs.append('pthread')
        self.cpp_info.defines.append('MAGICKCORE_QUANTUM_DEPTH=%s' % self.options.quantum_depth)
        self.cpp_info.defines.append('MAGICKCORE_HDRI_ENABLE=%s' % int(bool(self.options.hdri)))
