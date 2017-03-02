import sidt
import os

Version = '1.3.5'

def makeCommonConfigureArgs(installDir):
    configure = []
    configure.append('--enable-static=yes')
    configure.append('--enable-shared=no')
    configure.append('--disable-dependency-tracking')
    configure.append('--prefix')
    configure.append(installDir)
    return configure

def start(builder):
    url = 'http://downloads.xiph.org/releases/vorbis/libvorbis-%s.tar.gz' % (Version,)
    builder.setPackage(url)

def buildDarwin(builder):
    buildDir = builder.getBuildDir()
    tmpDir = builder.getTmpDir()
    platform = builder.getCurPlatform()
    arch = builder.getCurArchitecture()
    installDir = os.path.join(tmpDir, '%s_%s' % (platform, arch))

    dir = os.path.join(buildDir, 'libvorbis-%s' % Version)
    os.chdir(dir)

    configure = ['./configure']
    configure += makeCommonConfigureArgs(installDir)
    configure.append('--with-ogg=%s' % (os.path.join(builder.getInstallDir(), 'osx')))
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
    print('libvorbis: configure...')
    builder.execCmd(configure, env=env)

    # make
    print('libvorbis: make...')
    builder.execCmd(['make'], env=env)

    # make install
    print('libvorbis: make install...')
    builder.execCmd(['make', 'install'], env=env)

    return [os.path.join(installDir, 'lib/libvorbis.a'), os.path.join(installDir, 'lib/libvorbisfile.a')]

def buildDroid(builder):
    buildDir = builder.getBuildDir()
    tmpDir = builder.getTmpDir()
    platform = builder.getCurPlatform()
    arch = builder.getCurArchitecture()
    installDir = os.path.join(tmpDir, '%s_%s' % (platform, arch))

    dir = os.path.join(buildDir, 'libvorbis-%s' % Version)
    os.chdir(dir)


    configure = ['./configure']
    configure.append('--host=arm-linux-androideabi')
    configure.append('--with-ogg=%s' % (os.path.join(builder.getInstallDir(), 'droid', builder.getDroidABI())))
    configure += makeCommonConfigureArgs(installDir)

    env = { 'PATH':os.path.join(builder.getDroidToolchainDir(), 'bin') + ':' + os.environ['PATH'] }


    # configure
    print('libvorbis: configure...')
    builder.execCmd(configure, env=env)

    # make
    print('libvorbis: make...')
    builder.execCmd(['make'], env=env)

    # make install
    print('libvorbis: make install...')
    builder.execCmd(['make', 'install'], env=env)

    return [os.path.join(installDir, 'lib/libvorbis.a'), os.path.join(installDir, 'lib/libvorbisfile.a')]


def buildLinux(builder):
    buildDir = builder.getBuildDir()
    tmpDir = builder.getTmpDir()
    platform = builder.getCurPlatform()
    arch = builder.getCurArchitecture()
    installDir = os.path.join(tmpDir, '%s_%s' % (platform, arch))

    dir = os.path.join(buildDir, 'libvorbis-%s' % Version)
    os.chdir(dir)


    configure = ['./configure']
    configure.append('--with-ogg=%s' % (os.path.join(builder.getInstallDir(), 'linux', builder.getCurArchitecture())))
    configure += makeCommonConfigureArgs(installDir)

    # configure
    print('libvorbis: configure...')
    builder.execCmd(configure)

    # make
    print('libvorbis: make...')
    builder.execCmd(['make'])

    # make install
    print('libvorbis: make install...')
    builder.execCmd(['make', 'install'])

    return [os.path.join(installDir, 'lib/libvorbis.a'), os.path.join(installDir, 'lib/libvorbisfile.a')]

def copyIncludeFiles(builder, dest):
    tmpDir = builder.getTmpDir()
    platform = builder.getCurPlatform()
    arch = builder.getCurArchitecture()
    installDir = os.path.join(tmpDir, '%s_%s' % (platform, arch))
    src = os.path.join(installDir, 'include')
    builder.copyTree(src, dest)
