import sidt
import os

Version = '7.45.0'
WithSSL = True 

def start(builder):
    url = 'http://curl.haxx.se/download/curl-%s.tar.gz' % Version
    builder.setPackage(url)

def buildDroid(builder):  
    buildDir = builder.getBuildDir() 
    tmpDir = builder.getTmpDir()
    platform = builder.getCurPlatform()
    arch = builder.getCurArchitecture()
    installDir = os.path.join(tmpDir, '%s_%s' % (platform, arch))
    
    dir = os.path.join(buildDir, 'curl-%s' % Version)
    os.chdir(dir)

    configure = ['./Configure']
    configure.append('--host=arm-linux-androideabi')
    configure.append('--disable-ldap')
    configure.append('--disable-ftp')
    configure.append('--disable-manual')
    configure.append('--disable-shared')
    configure.append('--enable-static')
    if WithSSL:
        configure.append('--with-ssl')
    configure.append('--prefix')
    configure.append(installDir) 

        

    env = { 'PATH':os.path.join(builder.getDroidToolchainDir(), 'bin') + ':' + os.environ['PATH'] }
    #env['NM'] = builder.getDroidToolchainTool('nm')
    if WithSSL:
        env['CFLAGS'] = '-I%s' % os.path.join(builder.getInstallDir(), 'droid', 'include')
        env['CPPFLAGS'] = '-I%s' % os.path.join(builder.getInstallDir(), 'droid', 'include')
        env['LDFLAGS'] = '-L%s' % os.path.join(builder.getInstallDir(), 'droid', builder.getDroidABI())

    # configure 
    print('configure...')
    builder.execCmd(configure, env=env)

    # make
    print('make...')
    builder.execCmd(['make'], env=env)

    # make install
    print('make install...')
    builder.execCmd(['make', 'install'], env=env)

    libcurl = os.path.join(installDir, 'lib/libcurl.a')  
    return [libcurl]

def buildIos(builder):
  
    buildDir = builder.getBuildDir() 
    tmpDir = builder.getTmpDir()
    platform = builder.getCurPlatform()
    arch = builder.getCurArchitecture()
    installDir = os.path.join(tmpDir, '%s_%s' % (platform, arch))
    
    dir = os.path.join(buildDir, 'curl-%s' % Version)
    os.chdir(dir)

    configure = ['./Configure']
    
    configure.append('--disable-ldap')
    configure.append('--disable-ftp')
    configure.append('--disable-manual')
    configure.append('--disable-shared')
    configure.append('--enable-static')
    if WithSSL:
        configure.append('--with-ssl')
    configure.append('--prefix')
    configure.append(installDir) 
    if platform == 'iPhoneOS':
        configure.append('-host=armv7')

    cc = builder.getCompiler()
    cc += ' -framework Security'
    cflags = ' -arch %s ' % arch
    cflags += ' -isysroot %s' % builder.getIosSysRoot()
    cflags += ' -mios-simulator-version-min=8.0'
    ldflags = '' 
    cppflags = ''
    if WithSSL:
        cflags += ' -I%s' % os.path.join(builder.getInstallDir(), 'ios', 'include')  
        cppflags += '-I%s' % os.path.join(builder.getInstallDir(), 'ios', 'include')  
        ldflags += '-L%s' % os.path.join(builder.getInstallDir(), 'ios', 'lib')

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

    libcurl = os.path.join(installDir, 'lib/libcurl.a')  
    return [libcurl]

def copyIncludeFiles(builder, dest):
    src = os.path.join(builder.getBuildDir(), 'curl-%s' % Version, 'include')

    # fix include files to work for 32 and 64 bit architectures
    path = os.path.join(src, 'curl', 'curlbuild.h') 
    with open(path, 'r') as forg:
        with open(path + '.new', 'w') as fout:
            for line in forg:
                if '#define CURL_SIZEOF_LONG' in line:
                    line = '#define CURL_SIZEOF_LONG sizeof(long)\n'
                if '#define CURL_SIZEOF_CURL_OFF_T' in line:
                    line = '#define CURL_SIZEOF_CURL_OFF_T sizeof(long)\n' 
                fout.write(line)
    os.remove(path)
    os.rename(path + '.new', path)

    builder.copyTree(src, dest)
