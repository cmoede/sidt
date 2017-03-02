import sidt
import os

Version = '1.3.2'

def makeCommonConfigureArgs(installDir):
    configure = []
    configure.append('--enable-static=yes')
    configure.append('--enable-shared=no')
    configure.append('--disable-dependency-tracking')
    configure.append('--with-pic=yes')
    configure.append('--prefix')
    configure.append(installDir)
    return configure

def start(builder):
    url = 'http://downloads.xiph.org/releases/ogg/libogg-%s.tar.gz' % (Version,)
    builder.setPackage(url)

def buildDarwin(builder):
    buildDir = builder.getBuildDir()
    tmpDir = builder.getTmpDir()
    platform = builder.getCurPlatform()
    arch = builder.getCurArchitecture()
    installDir = os.path.join(tmpDir, '%s_%s' % (platform, arch))

    dir = os.path.join(buildDir, 'libogg-%s' % Version)
    os.chdir(dir)

    configure = ['./configure']
    configure += makeCommonConfigureArgs(installDir)
    if platform == 'iPhoneOS':
        configure.append('-host=arm-apple-darwin')
    cc = builder.getCompiler()
    cflags = ' -arch %s ' % arch
    if platform == 'iPhoneOS' or platform == 'iPhoneSimulator':
        cflags += ' -isysroot %s' % builder.getIosSysRoot()
        cflags += ' -mios-simulator-version-min=8.0'
    ldflags = ''
    cppflags = ''

    configure.append('CC=%s' % cc)
    configure.append('CFLAGS=%s' % cflags)
    configure.append('CPPFLAGS=%s' % cppflags)
    configure.append('LDFLAGS=%s' % ldflags)
    env = {}

    # configure
    print('libogg: configure...')
    builder.execCmd(configure, env=env)

    # make
    print('libogg: make...')
    builder.execCmd(['make'], env=env)

    # make install
    print('libogg: make install...')
    builder.execCmd(['make', 'install'], env=env)

    return [os.path.join(installDir, 'lib/libogg.a')]

def buildDroid(builder):
    buildDir = builder.getBuildDir()
    tmpDir = builder.getTmpDir()
    platform = builder.getCurPlatform()
    arch = builder.getCurArchitecture()
    installDir = os.path.join(tmpDir, '%s_%s' % (platform, arch))

    dir = os.path.join(buildDir, 'libogg-%s' % Version)
    os.chdir(dir)


    configure = ['./configure']
    configure.append('--host=arm-linux-androideabi')
    configure += makeCommonConfigureArgs(installDir)

    env = { 'PATH':os.path.join(builder.getDroidToolchainDir(), 'bin') + ':' + os.environ['PATH'] }


    # configure
    print('libogg: configure...')
    builder.execCmd(configure, env=env)

    # make
    print('libogg: make...')
    builder.execCmd(['make'], env=env)

    # make install
    print('libogg: make install...')
    builder.execCmd(['make', 'install'], env=env)

    return [os.path.join(installDir, 'lib/libogg.a')]

def buildLinux(builder):
    buildDir = builder.getBuildDir()
    tmpDir = builder.getTmpDir()
    platform = builder.getCurPlatform()
    arch = builder.getCurArchitecture()
    installDir = os.path.join(tmpDir, '%s_%s' % (platform, arch))

    dir = os.path.join(buildDir, 'libogg-%s' % Version)
    os.chdir(dir)


    configure = ['./configure']
    configure += makeCommonConfigureArgs(installDir)

    # configure
    print('libogg: configure...')
    builder.execCmd(configure)

    # make
    print('libogg: make...')
    builder.execCmd(['make'])

    # make install
    print('libogg: make install...')
    builder.execCmd(['make', 'install'])

    return [os.path.join(installDir, 'lib/libogg.a')]


def copyIncludeFiles(builder, dest):
    tmpDir = builder.getTmpDir()
    platform = builder.getCurPlatform()
    arch = builder.getCurArchitecture()
    installDir = os.path.join(tmpDir, '%s_%s' % (platform, arch))
    src = os.path.join(installDir, 'include')
    builder.copyTree(src, dest)
