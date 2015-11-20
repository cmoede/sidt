import sidt 
import os

Version = '1.0.6'

def start(builder):
    url = 'https://download.libsodium.org/libsodium/releases/libsodium-%s.tar.gz' % Version
    builder.setPackage(url)

def buildDroid(builder):
    buildDir = builder.getBuildDir() 
    tmpDir = builder.getTmpDir()
    platform = builder.getCurPlatform()
    arch = builder.getCurArchitecture()
    installDir = os.path.join(tmpDir, '%s_%s' % (platform, arch))
    
    dir = os.path.join(buildDir, 'libsodium-%s' % Version)
    os.chdir(dir)

    configure = ['./configure']
    configure.append('--disable-shared')
    configure.append('--disable-soname-versions')
    configure.append('--enable-minimal')    
    configure.append('--prefix=%s' % installDir)
    configure.append('--with-sysroot=%s' % builder.getDroidSysRoot())
    configure.append('--host=%s' % 'arm-linux-androideabi')

    env = {
              'PATH':os.path.join(builder.getDroidToolchainDir(), 'bin') + ':' + os.environ['PATH']
            }

    # autogen   
    print('autogen...')
    builder.execCmd(['./autogen.sh'])
    
    # configure 
    print('configure...')
    builder.execCmd(configure, env=env)

    # make
    print('make...')
    builder.execCmd(['make'], env=env)

    # make install
    print('make install...')
    builder.execCmd(['make', 'install'], env=env)

    libsodium = os.path.join(installDir, 'lib/libsodium.a')  
    return [libsodium]
    

def buildIos(builder):
    buildDir = builder.getBuildDir() 
    tmpDir = builder.getTmpDir()
    platform = builder.getCurPlatform()
    arch = builder.getCurArchitecture()
    installDir = os.path.join(tmpDir, '%s_%s' % (platform, arch))
    
    dir = os.path.join(buildDir, 'libsodium-%s' % Version)
    os.chdir(dir)

    configure = ['./configure']
    configure.append('--disable-shared')
    configure.append('--enable-minimal')    
    configure.append('--prefix')
    configure.append(installDir) 
    if platform == 'iPhoneOS':
        configure.append('--host=arm-apple-darwin10')

    cc = builder.getCompiler()
    cflags = ' -arch %s ' % arch
    cflags += ' -isysroot %s' % builder.getIosSysRoot()
    cflags += ' -mios-simulator-version-min=8.0'
    
    configure.append('CC=%s' % cc)
    configure.append('CFLAGS=%s' % cflags)

    env = {
        'XCODEDIR':builder.getXcodeDeveloperPath(),
        'IOS_SIMULATOR_VERSION_MIN':'8.0',
        'BASEDIR':builder.getIosCrossTop(),
        'PATH':builder.getIosCrossTop() + '/usr/bin:' + builder.getIosCrossTop() + '/usr/sbin:' + os.environ['PATH'],
        'SDK':builder.getIosCrossSDK()
    }

    # autogen   
    print('autogen...')
    builder.execCmd(['./autogen.sh'])
    
    # configure 
    print('configure...')
    builder.execCmd(configure, env=env)

    # make
    print('make...')
    builder.execCmd(['make'], env=env)

    # make install
    print('make install...')
    builder.execCmd(['make', 'install'], env=env)

    libsodium = os.path.join(installDir, 'lib/libsodium.a')  
    return [libsodium]

def copyIncludeFiles(builder, dest):
    src = os.path.join(builder.getBuildDir(), 'libsodium-%s' % Version, 'src/libsodium/include')
    builder.copyTree(src, dest)    
