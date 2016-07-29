import sidt 
import os

Version = '2.7.2'
AppMK = '''\
APP_OPTIM := release
APP_PLATFORM := android-17
APP_STL := gnustl_static
APP_CPPFLAGS += -frtti
APP_CPPFLAGS += -fexceptions
APP_CPPFLAGS += -DANDROID
APP_ABI := @ABI@
NDK_TOOLCHAIN_VERSION := clang'''

AndroidMK='''\
LOCAL_PATH := $(call my-dir)
include $(CLEAR_VARS)
LOCAL_MODULE    := libxml2
XML2_SOURCES := \
    SAX.c SAX2.c entities.c encoding.c error.c parserInternals.c \
    parser.c tree.c hash.c list.c dict.c xmlIO.c xmlmemory.c \
    uri.c globals.c xmlstring.c threads.c valid.c chvalid.c
XML2_LOCAL_SRC_FILES := $(addprefix ../,$(XML2_SOURCES))
LOCAL_SRC_FILES := $(XML2_LOCAL_SRC_FILES)
LOCAL_C_INCLUDES := $(LOCAL_PATH)/../include
include $(BUILD_STATIC_LIBRARY)'''

def start(builder):
    url = 'http://xmlsoft.org/sources/libxml2-%s.tar.gz' % Version
    builder.setPackage(url)

def buildDroid(builder):
    buildDir = builder.getBuildDir() 
    tmpDir = builder.getTmpDir()
    platform = builder.getCurPlatform()
    arch = builder.getCurArchitecture()
    installDir = os.path.join(tmpDir, '%s_%s' % (platform, arch))
    droidABI = builder.getDroidABI();
    
    buildDir = os.path.join(buildDir, 'libxml2-%s' % Version)
    os.chdir(buildDir)

    # create empty config file
    with open('config.h', 'w') as f:
        f.write('')

    # write jni files
    dir = os.path.join(buildDir, 'jni')
    os.mkdir(dir)
    with open("jni/Application.mk", "w") as f:
        f.write(AppMK.replace('@ABI@', droidABI))

    with open("jni/Android.mk", "w") as f:
        f.write(AndroidMK)    
    
    lines = []
    with open("include/libxml/xmlversion.h", "r") as f:
        lines = f.readlines()

    whitelist = ['LIBXML_TREE_ENABLED','LIBXML_OUTPUT_ENABLED','LIBXML_PUSH_ENABLED','LIBXML_READER_ENABLED','LIBXML_WRITER_ENABLED','LIBXML_SAX1_ENABLED']
    
    modifiedLines = []
    for i in range(0, len(lines)):
        if i + 1 < len(lines) and lines[i].find('#if 1') == 0: # #if 1
            if lines[i+1].find('#define ') != -1 and lines[i+1].find('_ENABLED') != -1:
                inWhiteList = False
                for w in whitelist:
                    if lines[i+1].find(w) != -1:
                        inWhiteList = True
                        break
                if not inWhiteList:
                    modifiedLines.append('#if 0\n')
                    continue
        modifiedLines.append(lines[i])

    with open('include/libxml/xmlversion.h', 'w') as f:
        f.writelines(modifiedLines)

    cmd = []
    cmd.append(os.path.join(builder.getDroidNdkDir(), 'ndk-build'))
    builder.execCmd(cmd)
   
    return [os.path.join(buildDir, 'obj/local/%s/libxml2.a' % droidABI)]
       
 
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
    src = os.path.join(builder.getBuildDir(), 'libxml2-%s' % Version, 'include')
    builder.copyTree(src, dest)    
