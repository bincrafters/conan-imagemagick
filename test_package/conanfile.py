from conans import ConanFile, CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        bin_path = os.path.join("bin", "test_package")
        self.run(bin_path, run_environment=True)

        with open('delegates.txt') as f:
            content = f.read()

            def check(option, token):
                self.output.info('checking feature %s...' % token)
                if option:
                    if token not in content.split():
                        raise Exception("feature %s wasn't enabled!" % token)
                self.output.info('checking feature %s... OK!' % token)

            check(self.options['imagemagick'].zlib, 'zlib')
            check(self.options['imagemagick'].bzlib, 'bzlib')
            check(self.options['imagemagick'].lzma, 'lzma')
            check(self.options['imagemagick'].lcms, 'lcms')
            check(self.options['imagemagick'].openexr, 'exr')
            check(self.options['imagemagick'].with_libjpeg, 'jpeg')
            check(self.options['imagemagick'].openjp2, 'jp2')
            check(self.options['imagemagick'].png, 'png')
            check(self.options['imagemagick'].tiff, 'tiff')
            check(self.options['imagemagick'].webp, 'webp')
            check(self.options['imagemagick'].freetype, 'freetype')
            check(self.options['imagemagick'].xml, 'xml')
