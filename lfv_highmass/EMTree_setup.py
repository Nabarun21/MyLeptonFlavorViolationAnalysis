
# Tools to compile cython proxy class
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

setup(ext_modules=[Extension(
    "EMTree",                 # name of extension
    ["EMTree.pyx"], #  our Cython source
    include_dirs=['/cvmfs/cms.cern.ch/slc6_amd64_gcc530/cms/cmssw-patch/CMSSW_8_0_26_patch1/external/slc6_amd64_gcc530/bin/../../../../../../../slc6_amd64_gcc530/lcg/root/6.06.00-ikhhed6/include'],
    library_dirs=['/cvmfs/cms.cern.ch/slc6_amd64_gcc530/cms/cmssw-patch/CMSSW_8_0_26_patch1/external/slc6_amd64_gcc530/bin/../../../../../../../slc6_amd64_gcc530/lcg/root/6.06.00-ikhhed6/lib'],
    libraries=['Tree', 'Core', 'TreePlayer'],
    language="c++", 
    extra_compile_args=['-std=c++11', '-fno-var-tracking-assignments'])],  # causes Cython to create C++ source
    cmdclass={'build_ext': build_ext})
