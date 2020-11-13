from conans import ConanFile, tools, AutoToolsBuildEnvironment, MSBuild
import os
import glob


class ImageMagicConan(ConanFile):
    name = "imagemagick"
    version = "7.0.8-44"
    description = ("ImageMagick is a free and open-source software suite for displaying, converting, and editing "
                  "raster image and vector image files")
    topics = ("conan", "imagemagick", "images", "manipulating")
    url = "https://github.com/bincrafters/conan-imagemagic"
    homepage = "https://github.com/ImageMagick/ImageMagick"
    license = "ImageMagick"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "hdri": [True, False],
               "quantum_depth": [8, 16, 32],
               "zlib": [True, False],
               "bzlib": [True, False],
               "lzma": [True, False],
               "lcms": [True, False],
               "openexr": [True, False],
               "jpeg": [True, False],
               "openjp2": [True, False],
               "png": [True, False],
               "tiff": [True, False],
               "webp": [True, False],
               "xml": [True, False],
               "freetype": [True, False],
               "utilities": [True, False],
               "with_libjpeg": [False, "libjpeg", "libjpeg-turbo"]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "hdri": True,
                       "quantum_depth": 16,
                       "zlib": True,
                       "bzlib": True,
                       "lzma": True,
                       "lcms": True,
                       "openexr": True,
                       "jpeg": False,
                       "openjp2": True,
                       "png": True,
                       "tiff": True,
                       "webp": True,
                       "with_libjpeg": "libjpeg",
                       "xml": True,
                       "freetype": True,
                       "utilities": True}

    generators = "pkg_config"

    _source_subfolder = "ImageMagick"  # name is important, VisualMagick uses relative paths to it
    _build_subfolder = "build_subfolder"

    @property
    def _is_mingw_windows(self):
        return self.settings.os == 'Windows' and self.settings.compiler == 'gcc' and os.name == 'nt'

    @property
    def _is_msvc(self):
        return self.settings.compiler == 'Visual Studio'

    @property
    def _modules(self):
        return ['Magick++', 'MagickWand', 'MagickCore']

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC
    
    def configure(self):
        # Handle deprecated jpeg option
        if self.options.jpeg:
            self.output.warn("jpeg option is deprecated, use with_libjpeg option instead.")
        del self.options.jpeg

    def requirements(self):
        if self.options.zlib:
            self.requires('zlib/1.2.11')
        if self.options.bzlib:
            self.requires('bzip2/1.0.8')
        if self.options.lzma:
            self.requires('xz_utils/5.2.4')
        if self.options.lcms:
            self.requires('lcms/2.9')
        if self.options.openexr:
            self.requires('openexr/2.3.0')
        if self.options.with_libjpeg:
            if self.options.with_libjpeg == "libjpeg-turbo":
                self.requires('libjpeg-turbo/2.0.5')
            else:
                self.requires('libjpeg/9d')
        if self.options.openjp2:
            self.requires('openjpeg/2.3.1')
        if self.options.png:
            self.requires('libpng/1.6.37')
        if self.options.tiff:
            self.requires('libtiff/4.0.9')
        if self.options.webp:
            self.requires('libwebp/1.0.3')
        if self.options.xml:
            self.requires('libxml2/2.9.10')
        if self.options.freetype:
            self.requires('freetype/2.10.2')

    def source(self):
        tools.get("{0}/archive/{1}.tar.gz".format(self.homepage, self.version))
        extracted_dir = "ImageMagick-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

        tools.get('https://github.com/ImageMagick/VisualMagick/archive/master.zip')
        os.rename('VisualMagick-master', 'VisualMagick')

    def build(self):
        if self._is_msvc:
            self._build_msvc()
        else:
            self._build_configure()

    def _build_msvc(self):
        # remove unnecessary dependencies from config
        for lib in ['bzlib', 'lcms', 'libxml', 'lqr', 'zlib']:
            tools.replace_in_file(os.path.join('VisualMagick', 'MagickCore', 'Config.txt'),
                                  '\n%s' % lib, '', strict=False)
        tools.replace_in_file(os.path.join('VisualMagick', 'coders', 'Config.dng.txt'), '\nlibraw', '')
        tools.replace_in_file(os.path.join('VisualMagick', 'coders', 'Config.exr.txt'), '\nexr', '')
        tools.replace_in_file(os.path.join('VisualMagick', 'coders', 'Config.flif.txt'), '\nflif', '')
        tools.replace_in_file(os.path.join('VisualMagick', 'coders', 'Config.heic.txt'), '\nlibheif', '')
        tools.replace_in_file(os.path.join('VisualMagick', 'coders', 'Config.jbig.txt'), '\njbig', '')
        tools.replace_in_file(os.path.join('VisualMagick', 'coders', 'Config.jp2.txt'), '\nopenjpeg', '')
        tools.replace_in_file(os.path.join('VisualMagick', 'coders', 'Config.jpeg.txt'), '\njpeg', '')
        tools.replace_in_file(os.path.join('VisualMagick', 'coders', 'Config.mat.txt'), '\nzlib', '')
        tools.replace_in_file(os.path.join('VisualMagick', 'coders', 'Config.miff.txt'), '\nbzlib', '')
        tools.replace_in_file(os.path.join('VisualMagick', 'coders', 'Config.miff.txt'), '\nliblzma', '')
        tools.replace_in_file(os.path.join('VisualMagick', 'coders', 'Config.miff.txt'), '\nzlib', '')
        tools.replace_in_file(os.path.join('VisualMagick', 'coders', 'Config.msl.txt'), '\nlibxml', '')
        tools.replace_in_file(os.path.join('VisualMagick', 'coders', 'Config.pango.txt'), '\ncairo', '')
        tools.replace_in_file(os.path.join('VisualMagick', 'coders', 'Config.pango.txt'), '\nglib', '')
        tools.replace_in_file(os.path.join('VisualMagick', 'coders', 'Config.pango.txt'), '\npango', '')
        tools.replace_in_file(os.path.join('VisualMagick', 'coders', 'Config.png.txt'), '\npng', '')
        tools.replace_in_file(os.path.join('VisualMagick', 'coders', 'Config.png.txt'), '\nzlib', '')
        tools.replace_in_file(os.path.join('VisualMagick', 'coders', 'Config.psd.txt'), '\nzlib', '')
        tools.replace_in_file(os.path.join('VisualMagick', 'coders', 'Config.svg.txt'), '\ncairo', '')
        tools.replace_in_file(os.path.join('VisualMagick', 'coders', 'Config.svg.txt'), '\nglib', '')
        tools.replace_in_file(os.path.join('VisualMagick', 'coders', 'Config.svg.txt'), '\nlibxml', '')
        tools.replace_in_file(os.path.join('VisualMagick', 'coders', 'Config.svg.txt'), '\nlibrsvg', '')
        tools.replace_in_file(os.path.join('VisualMagick', 'coders', 'Config.tiff.txt'), '\ntiff', '')
        tools.replace_in_file(os.path.join('VisualMagick', 'coders', 'Config.url.txt'), '\nlibxml', '')
        tools.replace_in_file(os.path.join('VisualMagick', 'coders', 'Config.webp.txt'), '\nwebp', '')

        # FIXME: package LiquidRescale  aka liblqr
        tools.replace_in_file(os.path.join('VisualMagick', 'lqr', 'Config.txt'),
                              '#define MAGICKCORE_LQR_DELEGATE', '')
        # FIXME: package LibRaw
        tools.replace_in_file(os.path.join('VisualMagick', 'libraw', 'Config.txt'),
                              '#define MAGICKCORE_RAW_R_DELEGATE', '')

        # FIXME: package FLIF (FLIF: Free Lossless Image Format)
        tools.replace_in_file(os.path.join('VisualMagick', 'flif', 'Config.txt'),
                              '#define MAGICKCORE_FLIF_DELEGATE', '')

        # FIXME: package libheif (High Efficiency Image File Format)
        tools.replace_in_file(os.path.join('VisualMagick', 'libheif', 'Config.txt'),
                              '#define MAGICKCORE_HEIC_DELEGATE', '')

        # FIXME: package pango
        tools.replace_in_file(os.path.join('VisualMagick', 'pango', 'Config.txt'),
                              '#define MAGICKCORE_PANGOCAIRO_DELEGATE', '')

        # FIXME: package librsvg
        tools.replace_in_file(os.path.join('VisualMagick', 'librsvg', 'Config.txt'),
                              '#define MAGICKCORE_RSVG_DELEGATE', '')

        if not self.options.shared:
            for module in self._modules:
                tools.replace_in_file(os.path.join('VisualMagick', module, 'Config.txt'), '[DLL]', '[STATIC]')
            tools.replace_in_file(os.path.join('VisualMagick', 'coders', 'Config.txt'), '[DLLMODULE]',
                                  '[STATIC]\n[DEFINES]\n_MAGICKLIB_')

        if self.settings.arch == 'x86_64':
            project = os.path.join('VisualMagick', 'configure', 'configure.vcxproj')
            tools.replace_in_file(project, 'Win32', 'x64')
            tools.replace_in_file(project, '/MACHINE:I386', '/MACHINE:x64')

        with tools.chdir(os.path.join('VisualMagick', 'configure')):

            toolset = self.settings.get_safe("compiler.toolset")
            if not toolset:
                toolset = {'12': 'v120',
                           '14': 'v140',
                           '15': 'v141'}.get(str(self.settings.compiler.version))
            tools.replace_in_file('configure.vcxproj',
                                  '<PlatformToolset>v120</PlatformToolset>',
                                  '<PlatformToolset>%s</PlatformToolset>' % toolset)

            msbuild = MSBuild(self)
            # fatal error C1189: #error:  Please use the /MD switch for _AFXDLL builds
            msbuild.build_env.flags = ["/MD"]
            msbuild.build(project_file='configure.vcxproj',
                          platforms={'x86': 'Win32'}, force_vcvars=True)

            # https://github.com/ImageMagick/ImageMagick-Windows/blob/master/AppVeyor/Build.ps1
            command = ['configure.exe', '/noWizard']
            msvc_version = {9: '/VS2002',
                            10: '/VS2010',
                            11: '/VS2012',
                            12: '/VS2013',
                            14: '/VS2015',
                            15: '/VS2017',
                            16: '/VS2019'}.get(int(str(self.settings.compiler.version)))
            runtime = {'MT': '/smt',
                       'MTd': '/smtd',
                       'MD': '/dmt',
                       'MDd': '/mdt'}.get(str(self.settings.compiler.runtime))
            command.append(runtime)
            command.append(msvc_version)
            command.append('/hdri' if self.options.hdri else '/noHdri')
            command.append('/Q%s' % self.options.quantum_depth)
            if self.settings.arch == 'x86_64':
                command.append('/x64')
            command = ' '.join(command)

            self.output.info(command)
            self.run(command)

        # disable incorrectly detected OpenCL
        baseconfig = os.path.join(self._source_subfolder, 'MagickCore', 'magick-baseconfig.h')
        tools.replace_in_file(baseconfig,
                              '#define MAGICKCORE__OPENCL', '#undef MAGICKCORE__OPENCL', strict=False)
        tools.replace_in_file(baseconfig,
                              '#define MAGICKCORE_HAVE_CL_CL_H', '#undef MAGICKCORE_HAVE_CL_CL_H', strict=False)

        suffix = {'MT': 'StaticMT',
                  'MTd': 'StaticMTD',
                  'MD': 'DynamicMT',
                  'MDd': 'DynamicMT'}.get(str(self.settings.compiler.runtime))

        # GdiPlus requires C++, but ImageMagick has *.c files
        project = 'IM_MOD_emf_%s.vcxproj' % suffix if self.options.shared else 'CORE_coders_%s.vcxproj' % suffix
        tools.replace_in_file(os.path.join('VisualMagick', 'coders', project),
                              '<ClCompile Include="..\\..\\ImageMagick\\coders\\emf.c">',
                              '<ClCompile Include="..\\..\\ImageMagick\\coders\\emf.c">\n'
                              '<CompileAs>CompileAsCpp</CompileAs>')

        for module in self._modules:
            with tools.chdir(os.path.join('VisualMagick', module)):
                msbuild = MSBuild(self)
                msbuild.build(project_file='CORE_%s_%s.vcxproj' % (module, suffix),
                              upgrade_project=False,
                              platforms={'x86': 'Win32', 'x86_64': 'x64'})

        with tools.chdir(os.path.join('VisualMagick', 'coders')):
            pattern = 'IM_MOD_*_%s.vcxproj' % suffix if self.options.shared else 'CORE_coders_%s.vcxproj' % suffix
            projects = glob.glob(pattern)
            for project in projects:
                msbuild = MSBuild(self)
                msbuild.build(project_file=project,
                              upgrade_project=False,
                              platforms={'x86': 'Win32', 'x86_64': 'x64'})

    def _build_configure(self):
        with tools.chdir(self._source_subfolder):
            env_build = AutoToolsBuildEnvironment(self, win_bash=self._is_mingw_windows)
            args = ['--disable-openmp',
                    '--disable-docs',
                    '--with-perl=no',
                    '--with-x=no'
                    ]

            if self.options.shared:
                args.extend(['--enable-shared=yes', '--enable-static=no'])
            else:
                args.extend(['--enable-shared=no', '--enable-static=yes'])
            args.append('--enable-hdri=yes' if self.options.hdri else '--enable-hdri=no')
            args.append('--with-quantum-depth=%s' % self.options.quantum_depth)
            args.append('--with-zlib=yes' if self.options.zlib else '--with-zlib=no')
            args.append('--with-bzlib=yes' if self.options.bzlib else '--with-bzlib=no')
            args.append('--with-lzma=yes' if self.options.lzma else '--with-lzma=no')

            args.append('--with-lcms=yes' if self.options.lcms else '--with-lcms=no')
            args.append('--with-openexr=yes' if self.options.openexr else '--with-openexr=no')
            args.append('--with-jpeg=yes' if self.options.with_libjpeg else '--with-jpeg=no')
            args.append('--with-openjp2=yes' if self.options.openjp2 else '--with-openjp2=no')
            args.append('--with-png=yes' if self.options.png else '--with-png=no')
            args.append('--with-tiff=yes' if self.options.tiff else '--with-tiff=no')
            args.append('--with-webp=yes' if self.options.webp else '--with-webp=no')
            args.append('--with-xml=yes' if self.options.xml else '--with-xml=no')
            args.append('--with-freetype=yes' if self.options.freetype else '--with-freetype=no')
            args.append('--with-utilities=yes' if self.options.utilities else '--with-utilities=no')
            env_build.configure(args=args)
            env_build.make()
            env_build.install()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        if self._is_msvc:
            self.copy(pattern="*CORE_*.lib", dst="lib", src=os.path.join('VisualMagick', 'lib'), keep_path=False)
            self.copy(pattern="*CORE_*.pdb", dst="lib", src=os.path.join('VisualMagick', 'lib'), keep_path=False)

            self.copy(pattern="*CORE_*.dll", dst="bin", src=os.path.join('VisualMagick', 'bin'), keep_path=False)
            self.copy(pattern="*IM_MOD_*.dll", dst="bin", src=os.path.join('VisualMagick', 'bin'), keep_path=False)
            self.copy(pattern="*CORE_*.pdb", dst="bin", src=os.path.join('VisualMagick', 'bin'), keep_path=False)
            self.copy(pattern="*IM_MOD_*.pdb", dst="bin", src=os.path.join('VisualMagick', 'bin'), keep_path=False)
            for module in self._modules:
                self.copy(pattern="*.h", dst=os.path.join("include", "ImageMagick-%s" % self._major, module),
                          src=os.path.join(self._source_subfolder, module))

    @property
    def _major(self):
        return self.version.split('.')[0]

    def _libname(self, library):
        if self._is_msvc:
            infix = 'DB' if self.settings.build_type == 'Debug' else 'RL'
            return 'CORE_%s_%s_' % (infix, library)
        else:
            suffix = 'HDRI' if self.options.hdri else ''
            return '%s-%s.Q%s%s' % (library, self._major, self.options.quantum_depth, suffix)

    def package_info(self):
        self.env_info.path.append(os.path.join(self.package_folder, "bin"))
        self.cpp_info.includedirs = [os.path.join('include', 'ImageMagick-%s' % self._major)]
        self.cpp_info.libs = [self._libname(m) for m in self._modules]
        if self._is_msvc:
            if not self.options.shared:
                self.cpp_info.libs.append(self._libname('coders'))
        if self.settings.os == 'Linux':
            self.cpp_info.libs.append('pthread')
        self.cpp_info.defines.append('MAGICKCORE_QUANTUM_DEPTH=%s' % self.options.quantum_depth)
        self.cpp_info.defines.append('MAGICKCORE_HDRI_ENABLE=%s' % int(bool(self.options.hdri)))
        self.cpp_info.defines.append('_MAGICKDLL_=1' if self.options.shared else '_MAGICKLIB_=1')
