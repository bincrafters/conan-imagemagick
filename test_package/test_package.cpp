#include <cstdlib>
#include <iostream>
#include <MagickCore/MagickCore.h>

int main()
{
    size_t version, range, depth;
    std::cout << "ImageMagick version      : " << GetMagickVersion(&version) << std::endl;
    std::cout << "ImageMagick release data : " << GetMagickReleaseDate() << std::endl;
    std::cout << "ImageMagick quantum range: " << GetMagickQuantumRange(&range) << std::endl;
    std::cout << "ImageMagick quantum depth: " << GetMagickQuantumDepth(&depth) << std::endl;
    std::cout << "ImageMagick package name : " << GetMagickPackageName() << std::endl;
    std::cout << "ImageMagick license      : " << GetMagickLicense() << std::endl;
    std::cout << "ImageMagick home URL     : " << GetMagickHomeURL() << std::endl;
    std::cout << "ImageMagick features     : " << GetMagickFeatures() << std::endl;
    std::cout << "ImageMagick delegates    : " << GetMagickDelegates() << std::endl;
    std::cout << "ImageMagick copyright    : " << GetMagickCopyright() << std::endl;

    return EXIT_SUCCESS;
}
