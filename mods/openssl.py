import sidt 
import os
import shutil

Version = '1.0.2h'

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
    configure.append('android-' + arch)   
    configure.append('--openssldir=' + installDir)
    
    toolchainDir = builder.getDroidToolchainDir()
    env = { 'CC': builder.getDroidToolchainTool('gcc'),  
            'AR': builder.getDroidToolchainTool('ar'), 
            'RANLIB': builder.getDroidToolchainTool('ranlib'), 
            'PATH':os.path.join(toolchainDir, 'bin') + ':' + os.environ['PATH']
            }
 
    # configure
    print('configure...') 
    builder.execCmd(configure, shell=True, env=env)

    # make
    print('make...')
    builder.execCmd(['make'], env=env)

    # make install
    print('make install...')
    builder.execCmd(['make', 'install'], env=env)

    libcrypto = os.path.join(installDir, 'lib/libcrypto.a') 
    libopenssl = os.path.join(installDir, 'lib/libssl.a') 
    return [libcrypto, libopenssl]


def buildIos(builder):

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
        configure.append('darwin64-x86_64-cc')
    installDir = '%s/%s_%s' % (tmpDir, platform, arch)
    configure.append('--openssldir=' + installDir)
 
    cc = builder.getCompiler()
    cc += ' -arch %s ' % arch
    cc += ' -isysroot %s' % builder.getIosSysRoot()
    cc += ' -mios-simulator-version-min=8.0'
   

    env = { 'PLATFORM':platform,
            'CROSS_TOP':builder.getIosCrossTop(),
            'CROSS_SDK':builder.getIosCrossSDK(),
            'BUILD_TOOLS':builder.getXcodeDeveloperPath(),
            'CC':cc }
   
    # configure
    print('configure...') 
    builder.execCmd(configure, shell=True, env=env)

    # make
    print('make...')
    builder.execCmd(['make', '-j', '4'], env=env)

    # make install
    print('make install...')
    builder.execCmd(['make', 'install'], env=env)

    libcrypto = os.path.join(installDir, 'lib/libcrypto.a') 
    libopenssl = os.path.join(installDir, 'lib/libssl.a') 
    return [libcrypto, libopenssl]

def copyIncludeFiles(builder, dest):
    src = os.path.join(builder.getBuildDir(), 'openssl-%s' % Version, 'include')
    builder.copyTree(src, dest)    


