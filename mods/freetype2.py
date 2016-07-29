import sidt
import os

Version = '2.6.2'

def start(builder):
    url = 'http://download.savannah.gnu.org/releases/freetype/freetype-%s.tar.gz' % Version
    builder.setPackage(url)

def buildDarwin(builder):
    buildDir = builder.getBuildDir() 
    tmpDir = builder.getTmpDir()
    platform = builder.getCurPlatform()
    arch = builder.getCurArchitecture()
    installDir = os.path.join(tmpDir, '%s_%s' % (platform, arch))
    
    dir = os.path.join(buildDir, 'freetype-%s' % Version)
    os.chdir(dir)

    configure = ['./configure']
    
    configure.append('--enable-static=yes')
    configure.append('--enable-shared=no')
    configure.append('--disable-dependency-trackin')
    configure.append('--without-harfbuzz')
    configure.append('--prefix')
    configure.append(installDir) 
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
    print('configure...') 
    builder.execCmd(configure, env=env)

    # make
    print('make...')
    builder.execCmd(['make'], env=env)

    # make install
    print('make install...')
    builder.execCmd(['make', 'install'], env=env)

    libft2 = os.path.join(installDir, 'lib/libfreetype.a')  
    return [libft2]

def buildDroid(builder):
    buildDir = builder.getBuildDir()
    tmpDir = builder.getTmpDir()
    platform = builder.getCurPlatform()
    arch = builder.getCurArchitecture()
    installDir = os.path.join(tmpDir, '%s_%s' % (platform, arch))

    dir = os.path.join(buildDir, 'freetype-%s' % Version)
    os.chdir(dir)

    configure = ['./Configure']
    configure.append('--host=arm-linux-androideabi')
    configure.append('--disable-shared')
    configure.append('--enable-static')
    configure.append('--without-harfbuzz')
    configure.append('--prefix')
    configure.append(installDir)

    env = { 'PATH':os.path.join(builder.getDroidToolchainDir(), 'bin') + ':' + os.environ['PATH'] }


    # configure
    print('configure...')
    builder.execCmd(configure, env=env)

    # make
    print('make...')
    builder.execCmd(['make'], env=env)

    # make install
    print('make install...')
    builder.execCmd(['make', 'install'], env=env)

    libft2 = os.path.join(installDir, 'lib/libfreetype.a')
    return [libft2]

def copyIncludeFiles(builder, dest):
    tmpDir = builder.getTmpDir()
    platform = builder.getCurPlatform()
    arch = builder.getCurArchitecture()
    installDir = os.path.join(tmpDir, '%s_%s' % (platform, arch))
    src = os.path.join(installDir, 'include')
    builder.copyTree(src, dest)
