#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os
import shutil
import glob


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
               "quantum_depth": [8, 16, 32],
               "zlib": [True, False],
               "bzlib": [True, False],
               "lzma": [True, False],
               "lcms": [True, False],
               "exr": [True, False],
               "jpeg": [True, False],
               "openjp2": [True, False],
               "png": [True, False],
               "tiff": [True, False],
               "webp": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "hdri": True,
                       "quantum_depth": 16,
                       "zlib": True,
                       "bzlib": True,
                       "lzma": True,
                       "lcms": True,
                       "exr": True,
                       "jpeg": True,
                       "openjp2": True,
                       "png": True,
                       "tiff": True,
                       "webp": True}

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def requirements(self):
        if self.options.zlib:
            self.requires('zlib/1.2.11@conan/stable')
        if self.options.bzlib:
            self.requires('bzip2/1.0.6@conan/stable')
        if self.options.lzma:
            self.requires('lzma/5.2.4@bincrafters/stable')
        if self.options.lcms:
            self.requires('lcms/2.9@bincrafters/stable')
        if self.options.exr:
            self.requires('openexr/2.3.0@conan/stable')
        if self.options.jpeg:
            self.requires('libjpeg/9c@bincrafters/stable')
        if self.options.openjp2:
            self.requires('openjpeg/2.3.0@bincrafters/stable')
        if self.options.png:
            self.requires('libpng/1.6.34@bincrafters/stable')
        if self.options.tiff:
            self.requires('libtiff/4.0.9@bincrafters/stable')
        if self.options.webp:
            self.requires('libwebp/1.0.0@bincrafters/stable')

    def source(self):
        source_url = "https://github.com/ImageMagick/ImageMagick"
        tools.get("{0}/archive/{1}.tar.gz".format(source_url, self.version))
        extracted_dir = "ImageMagick-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _copy_pkg_config(self, name):
        if name not in self.deps_cpp_info.deps:
            return
        root = self.deps_cpp_info[name].rootpath
        pc_dir = os.path.join(root, 'lib', 'pkgconfig')
        pc_files = glob.glob('%s/*.pc' % pc_dir)
        if not pc_files:
            pc_files = glob.glob('%s/.pc' % root)
        for pc_name in pc_files:
            new_pc = os.path.join('pkgconfig', os.path.basename(pc_name))
            self.output.info('copying .pc file %s' % os.path.basename(pc_name))
            shutil.copy(pc_name, new_pc)
            prefix = tools.unix_path(root) if os.name == 'nt' else root
            tools.replace_prefix_in_pc_file(new_pc, prefix)

    def build(self):
        with tools.chdir(self._source_subfolder):
            env_build = AutoToolsBuildEnvironment(self)
            args = ['--disable-openmp',
                    '--disable-docs',
                    '--with-utilities=no',
                    '--with-perl=no'
                    ]

            os.makedirs('pkgconfig')
            pkg_config_path = os.path.abspath('pkgconfig')
            pkg_config_path = tools.unix_path(pkg_config_path) if os.name == 'nt' else pkg_config_path

            for dep in self.deps_cpp_info.deps:
                self._copy_pkg_config(dep)

            if self.options.shared:
                args.extend(['--enable-shared=yes', '--enable-static=no'])
            else:
                args.extend(['--enable-shared=no', '--enable-static=yes'])
            args.append('--enable-hdri=yes' if self.options.hdri else '--enable-hdri=no')
            args.append('--with-quantum-depth=%s' % self.options.quantum_depth)
            args.append('--with-zlib=yes' if self.options.zlib else '--with-zlib=no')
            args.append('--with-bzlib=yes' if self.options.bzlib else '--with-bzlib=no')
            args.append('--with-lzma=yes' if self.options.lzma else '--with-lzma=no')

            args.append('--with-lsmc=yes' if self.options.lcms else '--with-lcms=no')
            args.append('--with-exr=yes' if self.options.exr else '--with-exr=no')
            args.append('--with-jpeg=yes' if self.options.exr else '--with-exr=jpeg')
            args.append('--with-openjp2=yes' if self.options.openjp2 else '--with-openjp2=no')
            args.append('--with-png=yes' if self.options.png else '--with-png=no')
            args.append('--with-tiff=yes' if self.options.png else '--with-tiff=no')
            args.append('--with-webp=yes' if self.options.webp else '--with-webp=no')
            env_build.configure(args=args, pkg_config_paths=[pkg_config_path])
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
