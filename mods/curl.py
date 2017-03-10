import sidt
import os

Version = '7.51.0'
WithSSL = True

def start(builder):
    url = 'http://curl.haxx.se/download/curl-%s.tar.gz' % Version
    builder.setPackage(url)

def makeCurlConfigureProtocols():
    configure = []
    configure.append('--disable-ftp')
    configure.append('--disable-file')
    configure.append('--disable-ldap')
    configure.append('--disable-ldaps')
    configure.append('--disable-rtsp')
    configure.append('--disable-proxy')
    configure.append('--disable-dict')
    configure.append('--disable-telnet')
    configure.append('--disable-tftp')
    configure.append('--disable-pop3')
    configure.append('--disable-imap')
    configure.append('--disable-smb')
    configure.append('--disable-smtp')
    configure.append('--disable-gopher')
    configure.append('--disable-manual')
    return configure

def buildDroid(builder):
    buildDir = builder.getBuildDir()
    tmpDir = builder.getTmpDir()
    platform = builder.getCurPlatform()
    arch = builder.getCurArchitecture()
    installDir = os.path.join(tmpDir, '%s_%s' % (platform, arch))

    dir = os.path.join(buildDir, 'curl-%s' % Version)
    os.chdir(dir)

    configure = ['./configure']
    if arch == 'x86':
        configure.append('--host=x86-linux-android')
    else:
        configure.append('--host=arm-linux-androideabi')
    configure += makeCurlConfigureProtocols()
    configure.append('--disable-shared')
    configure.append('--enable-static')
    if WithSSL:
        configure.append('--with-ssl')
    configure.append('--prefix')
    configure.append(installDir)
    configure.append('--enable-threaded-resolver') # NOTE: either use c-ares or threaded-resolver!  default (non-async) resolver is NOT thread-safe!


    #env = { 'PATH':os.path.join(builder.getDroidToolchainDir(), 'bin') + ':' + os.environ['PATH'] }

    toolchainDir = builder.getDroidToolchainDir()
    env = { 'CC': builder.getDroidToolchainTool('gcc'),
            'AR': builder.getDroidToolchainTool('ar'),
            'RANLIB': builder.getDroidToolchainTool('ranlib'),
            'PATH':os.path.join(toolchainDir, 'bin') + ':' + os.environ['PATH']
            }

    #env['NM'] = builder.getDroidToolchainTool('nm')
    if WithSSL:
        env['CFLAGS'] = '-I%s' % os.path.join(builder.getInstallDir(), 'droid', builder.getDroidABI(), 'include')
        env['CPPFLAGS'] = '-I%s' % os.path.join(builder.getInstallDir(), 'droid', builder.getDroidABI(), 'include')
        env['LDFLAGS'] = '-L%s' % os.path.join(builder.getInstallDir(), 'droid', builder.getDroidABI(), 'lib')

    # configure
    print('curl: configure...')
    builder.execCmd(configure, env=env)

    # make
    print('curl: make...')
    builder.execCmd(['make'], env=env)

    # make install
    print('curl: make install...')
    builder.execCmd(['make', 'install'], env=env)

    libcurl = os.path.join(installDir, 'lib/libcurl.a')
    return [libcurl]

def buildDarwin(builder):

    buildDir = builder.getBuildDir()
    tmpDir = builder.getTmpDir()
    platform = builder.getCurPlatform()
    arch = builder.getCurArchitecture()
    installDir = os.path.join(tmpDir, '%s_%s' % (platform, arch))

    dir = os.path.join(buildDir, 'curl-%s' % Version)
    os.chdir(dir)

    configure = ['./Configure']

    configure += makeCurlConfigureProtocols()
    configure.append('--disable-shared')
    configure.append('--enable-static')
    configure.append('--with-ssl')
    configure.append('--prefix')
    configure.append(installDir)
    configure.append('--enable-threaded-resolver') # NOTE: either use c-ares or threaded-resolver!  default (non-async) resolver is NOT thread-safe!
    if platform != 'osx':
        if arch == 'i386':
            configure.append('--host=i386-apple-darwin')
        elif arch == 'x86_64':
            configure.append('--host=x86_64-apple-darwin')
        elif arch == 'arm64':
            configure.append('--host=arm-apple-darwin')
        elif arch == 'armv7':
            configure.append('--host=armv7-apple-darwin')
        elif arch == 'armv7s':
            configure.append('--host=armv7s-apple-darwin')
        cc = builder.getCompiler()
        cc += ' -framework Security'
        if builder.Settings['ios']['bitcode']:
            cc += ' -fembed-bitcode'

        cflags = ' -arch %s ' % arch
        cflags += ' -isysroot %s' % builder.getIosSysRoot()
        cflags += ' -mios-simulator-version-min=8.0'
        ldflags = ''
        cppflags = ''
    else:
        cflags = ''
        ldflags = ''
        cppflags = ''
        cc = None
    if WithSSL:
        if platform != 'osx':
            cflags += ' -I%s' % os.path.join(builder.getInstallDir(), 'ios', 'include')
            cppflags += '-I%s' % os.path.join(builder.getInstallDir(), 'ios', 'include')
            ldflags += '-L%s' % os.path.join(builder.getInstallDir(), 'ios', 'lib')
        else:
            cflags += ' -I%s' % os.path.join(builder.getInstallDir(), 'osx', 'include')
            cppflags += '-I%s' % os.path.join(builder.getInstallDir(), 'osx', 'include')
            ldflags += '-L%s' % os.path.join(builder.getInstallDir(), 'osx', 'lib')

    cflags = cflags + '-Werror=partial-availability'

    if cc:
        configure.append('CC=%s' % cc)
    configure.append('CFLAGS=%s' % cflags)
    configure.append('CPPFLAGS=%s' % cppflags)
    configure.append('LDFLAGS=%s' % ldflags)
    env = {}

    # configure
    print('curl: configure...')
    builder.execCmd(configure, env=env)

    # make
    print('curl: make...')
    builder.execCmd(['make'], env=env)

    # make install
    print('curl: make install...')
    builder.execCmd(['make', 'install'], env=env)

    libcurl = os.path.join(installDir, 'lib/libcurl.a')
    return [libcurl]

def buildLinux(builder):
    buildDir = builder.getBuildDir()
    tmpDir = builder.getTmpDir()
    platform = builder.getCurPlatform()
    arch = builder.getCurArchitecture()
    installDir = os.path.join(tmpDir, '%s_%s' % (platform, arch))

    dir = os.path.join(buildDir, 'curl-%s' % Version)
    os.chdir(dir)

    configure = ['./configure']
    if arch == 'amd64' or arch == 'x86_64':
        configure.append('--host=amd64-linux')
    else:
        configure.append('--host=x86-linux')
    configure += makeCurlConfigureProtocols()
    configure.append('--disable-shared')
    configure.append('--enable-static')
    if WithSSL:
        configure.append('--with-ssl')
        configure.append('--with-ssl=' + os.path.join(builder.getInstallDir(), 'linux', builder.getCurArchitecture()))
    configure.append('--prefix')
    configure.append(installDir)
    configure.append('--enable-threaded-resolver') # NOTE: either use c-ares or threaded-resolver!  default (non-async) resolver is NOT thread-safe!
    configure.append('--without-librtmp')

    env = { 'CC': 'gcc',
            'PATH': os.environ['PATH'],
            # on linux the curl configure script may pkg-config to find its dependencies (most notably
            # openssl), so we must set the pkg-config path accordingly.
            # UPDATE: currently disabled, because our openssl installs cript does create the
            #         required pkgconfig files. --with-ssl=... *should* be sufficient.
            'PKG_CONFIG_PATH=$FH_DEPENDENCIES_PREFIX/lib/pkgconfig': os.path.join(builder.getInstallDir(), 'linux', builder.getCurArchitecture(), 'lib/pkgconfig')
    }

    if WithSSL:
        env['CFLAGS'] = '-I%s' % os.path.join(builder.getInstallDir(), platform, arch, 'include')
        env['CPPFLAGS'] = '-I%s' % os.path.join(builder.getInstallDir(), platform, arch, 'include')
        env['LDFLAGS'] = '-L%s' % os.path.join(builder.getInstallDir(), platform, arch, 'lib')
        # curl configure and/or openssl pkgconfig files do not like static openssl libraries,
        # they omit required libraries. add them.
        env['LIBS'] = ' -lpthread -ldl'


    # configure
    print('curl: configure...')
    builder.execCmd(configure, env=env)

    # make
    print('curl: make...')
    builder.execCmd(['make'], env=env)

    # make install
    print('curl: make install...')
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
                    line = '#define CURL_SIZEOF_CURL_OFF_T sizeof(curl_off_t)\n'
                fout.write(line)
    os.remove(path)
    os.rename(path + '.new', path)

    builder.copyTree(src, dest)
