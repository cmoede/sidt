import sidt
import os
import shutil

Version = '1.1.0b'

def makeCommonConfigureArgs(installDir):
    configure = []
    configure.append('--prefix=' + installDir)
    configure.append('no-shared')
    configure.append('no-asm')
    configure.append('no-async')
    configure.append('no-weak-ssl-ciphers')
    configure.append('no-ssl2')
    configure.append('no-ssl3')
    return configure

def start(builder):
    url = 'http://www.openssl.org/source/openssl-%s.tar.gz' % Version
    builder.setPackage(url)

def buildDroid(builder):
    buildDir = builder.getBuildDir()
    tmpDir = builder.getTmpDir()
    platform = builder.getCurPlatform()
    arch = builder.getCurArchitecture()
    installDir = '%s/%s_%s' % (tmpDir, platform, arch)

    dir = os.path.join(buildDir, 'openssl-%s' % Version)
    os.chdir(dir)

    configure = ['./Configure']
    if arch == 'x86':
        configure.append('android-' + arch)
    else:
        configure.append('android-armeabi')
    configure += makeCommonConfigureArgs(installDir)
    toolchainDir = builder.getDroidToolchainDir()
    cc = builder.getDroidToolchainTool('gcc')
    sysroot= builder.getDroidSysRoot()
    env = { 'CC': cc,
            'CROSS_SYSROOT':sysroot,
            #'LDFLAGS': sysroot,
            'AR': builder.getDroidToolchainTool('ar'),
            'RANLIB': builder.getDroidToolchainTool('ranlib'),
            'PATH':os.path.join(toolchainDir, 'bin') + ':' + os.environ['PATH']
            }

    # configure
    print('openssl: configure...')
    builder.execCmd(configure, shell=True, env=env)

    # make
    print('openssl: make...')
    builder.execCmd(['make'], env=env)

    # make install
    print('openssl: make install...')
    builder.execCmd(['make', 'install_sw'], env=env)

    libcrypto = os.path.join(installDir, 'lib/libcrypto.a')
    libopenssl = os.path.join(installDir, 'lib/libssl.a')
    return [libcrypto, libopenssl]


def buildDarwin(builder):

    buildDir = builder.getBuildDir()
    tmpDir = builder.getTmpDir()
    platform = builder.getCurPlatform()
    arch = builder.getCurArchitecture()

    dir = os.path.join(buildDir, 'openssl-%s' % Version)
    os.chdir(dir)

    configure = ['./Configure']
    if platform == 'iPhoneOS':
        configure.append('iphoneos-cross')
    elif platform == 'iPhoneSimulator':
        if arch == 'i386':
            configure.append('darwin-i386-cc')
        else:
            configure.append('darwin64-x86_64-cc')
    elif platform == 'osx':
        configure.append('darwin64-x86_64-cc')
    installDir = '%s/%s_%s' % (tmpDir, platform, arch)
    configure += makeCommonConfigureArgs(installDir)
    if platform != 'osx':
        cc = builder.getCompiler()
        cc += ' -arch %s ' % arch
        cc += ' -isysroot %s' % builder.getIosSysRoot()
        cc += ' -mios-simulator-version-min=8.0'
        if builder.Settings['ios']['bitcode']:
            cc += ' -fembed-bitcode'

        env = { 'PLATFORM':platform,
                'CROSS_TOP':builder.getIosCrossTop(),
                'CROSS_SDK':builder.getIosCrossSDK(),
                'BUILD_TOOLS':builder.getXcodeDeveloperPath(),
                'CC':cc }
    else:
        env = None


    # configure
    print('openssl: configure...')
    builder.execCmd(configure, shell=True, env=env)

    # make
    print('openssl: make...')
    builder.execCmd(['make', '-j', '4'], env=env)

    # make install
    print('openssl: make install...')
    builder.execCmd(['make', 'install_sw'], env=env)

    libcrypto = os.path.join(installDir, 'lib/libcrypto.a')
    libopenssl = os.path.join(installDir, 'lib/libssl.a')
    return [libcrypto, libopenssl]

def buildLinux(builder):
    buildDir = builder.getBuildDir()
    tmpDir = builder.getTmpDir()
    platform = builder.getCurPlatform()
    arch = builder.getCurArchitecture()
    installDir = '%s/%s_%s' % (tmpDir, platform, arch)

    dir = os.path.join(buildDir, 'openssl-%s' % Version)
    os.chdir(dir)

    configure = ['./Configure']
    configure += makeCommonConfigureArgs(installDir)
    if arch == 'amd64' or arch == 'x86_64':
        configure.append('linux-x86_64')
    else:
        configure.append('linux-elf')

    # configure
    print('openssl: configure...')
    builder.execCmd(configure, shell=True)

    # make
    print('openssl: make...')
    builder.execCmd(['make'])

    # make install
    print('openssl: make install...')
    builder.execCmd(['make', 'install_sw'])

    libcrypto = os.path.join(installDir, 'lib/libcrypto.a')
    libopenssl = os.path.join(installDir, 'lib/libssl.a')
    return [libcrypto, libopenssl]

def copyIncludeFiles(builder, dest):
    src = os.path.join(builder.getBuildDir(), 'openssl-%s' % Version, 'include')
    builder.copyTree(src, dest)


