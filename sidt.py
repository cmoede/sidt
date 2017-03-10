#!/usr/bin/python

import sys
import os
import subprocess
import shutil
import importlib
import datetime
import platform
import argparse

class builder:
    PackageURL = ''
    SavedCWD = os.getcwd()
    LogFile = ''
    PackageDir = ''
    BuildDir = ''
    TmpDir = ''
    InstallDir = ''
    DroidToolchainDir = ''

    Settings = None

    LibsToBuild = []

    KnownTargets = ['ios', 'droid', 'linux', 'osx']
    Targets = []

    # current build state
    CurPlatform = ''
    CurArchitecture = ''
    CurDroidABI = ''

    # options
    OptForceDownload = False
    OptDroidInstallDir = ''
    OptLinuxInstallDir = ''
    OptIOSInstallDir = ''
    OptOSXInstallDir = ''
    OptNdkDir = ''

    def __init__(self):
        configMod = importlib.import_module('config')
        self.Settings = configMod.settings

    def writeLog(self, s):
        self.LogFile.write("sidt (%s): %s\n" % (str(datetime.datetime.now()), s))

    def setup(self):
        logFileName = 'sidt_build.log'
        print('logging to %s' % logFileName)
        self.LogFile = open(logFileName, 'wb')
        if self.LogFile == None:
            self.printErrorAndExit(self, 'Failed to create logfile')
        self.writeLog("Starting new build")

        self.SavedCWD = os.getcwd()
        self.PackageDir = os.path.join(self.SavedCWD, 'sidt_packages')
        if not os.path.exists(self.PackageDir):
            os.mkdir(self.PackageDir)
        self.writeLog("Setup: PackageDir=%s" % self.PackageDir)

        self.BuildDir = os.path.join(self.SavedCWD, 'sidt_build')
        self.rmDir(self.BuildDir)
        if not os.path.exists(self.BuildDir):
            os.mkdir(self.BuildDir)
        self.writeLog("Setup: BuildDir=%s" % self.BuildDir)

        self.TmpDir = os.path.join(self.SavedCWD, 'sidt_tmp')
        self.rmDir(self.TmpDir)
        os.mkdir(self.TmpDir)
        self.writeLog("Setup: TmpDir=%s" % self.TmpDir)

        self.DroidToolchainDir = os.path.join(self.SavedCWD, 'sidt_toolchain')
        self.rmDir(self.DroidToolchainDir)
        self.writeLog("Setup: DroidToolchainDir=%s" % self.DroidToolchainDir)

        self.InstallDir = os.path.join(self.SavedCWD, 'sidt_install')
        if not os.path.exists(self.InstallDir):
            os.mkdir(self.InstallDir)
        self.writeLog("Setup: InstallDir=%s" % self.InstallDir)


    def printErrorAndExit(self, err):
        os.chdir(self.SavedCWD)
        print('error: %s' % err)
        sys.exit(1)

    def mkDir(self, dir):
        if not os.path.isdir(dir):
            os.mkdir(dir)

    def copyTree(self, src, dst):
        names = os.listdir(src)

        self.mkDir(dst)
        errors = []
        for name in names:
            srcname = os.path.join(src, name)
            dstname = os.path.join(dst, name)
            if os.path.isdir(srcname):
                self.copyTree(srcname, dstname)
            else:
                self.rmFile(dstname)
                shutil.copy2(srcname, dstname)

    def droidMakeToolchain(self, abi):
        print('setting up toolchain for %s...' % abi)
        self.writeLog("Setting up toolchain for %s..." % abi)
        self.rmDir(self.DroidToolchainDir)

        cmd = []
        cmd.append(os.path.join(self.getDroidNdkDir(), 'build/tools/make-standalone-toolchain.sh'))
        cmd.append('--platform=%s' % self.Settings['droid']['platform'])
        cmd.append('--install-dir=%s' % self.DroidToolchainDir)

        arch = ''
        if abi.find('armeabi') == 0:
            arch = 'arm'
        elif abi == 'x86':
            arch = 'x86'
        elif abi == 'x86_64':
            arch = 'x86_64'
        elif abi == 'mips':
            arch = 'mips'
        elif abi == 'mips64':
            arch = 'mips64'
        else:
            print('unknown abi %s' % abi)
        cmd.append('--arch=%s' % arch)
        self.execCmd(cmd, shell=True)
        print("Finished setting up toolchain for %s." % abi)
        self.writeLog("Finished setting up toolchain for %s." % abi)

    def getXcodeDeveloperPath(self):
        path = subprocess.check_output('xcode-select -print-path', shell=True)
        path = path.strip()
        if not os.path.isdir(path):
            self.printErrorAndExit('xcode developer path not found: %s' % path)
        return path

    def getInstallDir(self):
        return self.InstallDir

    def isWindows(self):
        return os.name == 'nt'

    def getIosSDKVersion(self):
        version = subprocess.check_output('xcrun -sdk iphoneos --show-sdk-version', shell=True)
        version = version.strip()
        return version

    def getIosCrossTop(self):
        crossTop = '%s/Platforms/%s.platform/Developer' % (self.getXcodeDeveloperPath(), self.getCurPlatform())
        return crossTop

    def getIosCrossSDK(self):
        crossSDK = '%s%s.sdk' % (self.getCurPlatform(), self.getIosSDKVersion())
        return crossSDK

    def getIosSysRoot(self):
        return os.path.join(self.getIosCrossTop(), 'SDKs', self.getIosCrossSDK())

    def getDroidNdkDir(self):
        if self.OptNdkDir != '':
            return self.OptNdkDir
        return self.Settings['droid']['ndk']

    def getDroidSysRoot(self):
        return os.path.join(self.Settings['droid']['ndk'], 'platforms', self.Settings['droid']['platform'], 'arch-' + self.CurArchitecture)

    def getDroidToolchainDir(self):
        return self.DroidToolchainDir

    def getDroidToolchainTool(self, tool):
        if self.CurArchitecture == 'x86':
            return os.path.join(self.getDroidToolchainDir(), 'bin', 'i686-linux-android-%s' % tool)
        else:
            return os.path.join(self.getDroidToolchainDir(), 'bin', 'arm-linux-androideabi-%s' % tool)

    def getDroidSysRoot(self):
        return os.path.join(self.getDroidToolchainDir(), 'sysroot')

    def getDroidABI(self):
        return self.CurDroidABI

#cc = '/opt/android-ndk-r10e/toolchains/arm-linux-androideabi-4.9/prebuilt/darwin-x86_64/bin/

    def getCurPlatform(self):
        return self.CurPlatform

    def getCurArchitecture(self):
        return self.CurArchitecture

    def getCompiler(self):
        return os.path.join(self.getXcodeDeveloperPath(), 'usr/bin/gcc')

    def getBuildDir(self):
        return self.BuildDir

    def getTmpDir(self):
        return self.TmpDir

    def rmFile(self, file):
        if os.path.isfile(file):
            os.remove(file)

    def rmDir(self, dir):
        if dir.find(self.SavedCWD) != 0:
            self.printErrorAndExit('will not delete dir')
        if not self.isWindows():
            os.system('rm -rf %s' % dir)
        else:
            os.system('rmdir "%s" /s /q' % dir)

    def execCmd(self, args, shell = False, env = None, ignoreError = False):
        if shell:
            args = ' '.join(args)
        self.writeLog("Executing command: %s" % args)
        self.LogFile.flush()
        p = subprocess.Popen(args, stdout=self.LogFile, stderr=self.LogFile, shell = shell,  env=env)
        ret = p.wait()
        if ret != 0 and not ignoreError:
            self.writeLog("Subprocess failed with code %d" % ret)
            print('subprocess.call failed with code %d' % ret)
            print('args: %s' % args)
            sys.exit(1)
        self.writeLog("Command (%s) finished with exitcode 0" % args)
        return ret

    def mergeLibs(self, libs, out):
        args = ['lipo', '-create']
        for l in libs:
            args.append(l)
        args.append('-output')
        args.append(out)
        self.execCmd(args)

    def downloadPackage(self):
        os.chdir(self.PackageDir)
        if os.path.isfile(self.getPackageFileName()) and not self.OptForceDownload:
            print('using downloaded package')
            self.writeLog("Using downloaded package")
            return

        print('downloading %s' % self.PackageURL)
        self.writeLog("Downloading %s" % self.PackageURL)
        self.rmFile(self.getPackageFileName())
        self.execCmd(['curl', '-Lo', 'package.download', self.PackageURL])
        os.rename('package.download', self.getPackageFileName())
        os.chdir(self.SavedCWD)
        self.writeLog("Package download finished")
        print("Package download finished")

    def setPackage(self, url):
        print('setPackage %s' % url)
        self.PackageURL = url

    # returns the package filename
    def getPackageFileName(self):
        return self.PackageURL.rsplit('/', 1)[1]

    def unpackPackage(self):
        print('extracting...')
        self.writeLog("Extracting...")
        packageName = self.PackageURL.rsplit('/', 1)[1]
        os.chdir(self.BuildDir)
        path = os.path.join(self.PackageDir, packageName)
        ret = self.execCmd(['tar', 'zxf', path], ignoreError = True)
        if ret != 0:
            print('failed to unpack %s - removing tar file' % path)
            self.writeLog("Extracting to %s FAILED, removing tar file" % path)
            os.remove(path)
            sys.exit(1)
        os.chdir(self.SavedCWD)
        self.writeLog("Extracting finished.")

    def cleanupBuildDir(self):
        self.rmDir(self.BuildDir)
        os.mkdir(self.BuildDir)

    def checkNdkDir(self):
        ndkDir = self.getDroidNdkDir()
        if not os.path.isdir(ndkDir):
            return False
        if not os.path.isfile(os.path.join(ndkDir, 'ndk-build')):
            return False
        return True

    def checkDroidSetup(self):
        if not self.checkNdkDir():
            self.printErrorAndExit('nkd dir not found')

    def buildOsx(self, name, mod):

        # create output directory structure
        self.mkDir(os.path.join(self.InstallDir, 'osx'))
        self.mkDir(os.path.join(self.InstallDir, 'osx', 'include'))
        self.mkDir(os.path.join(self.InstallDir, 'osx', 'lib'))

        # build variants
        print('-----------------------------------------')
        print('building %s for osx/x86_64' % name)
        self.unpackPackage()
        funcBuild = getattr(mod, 'buildDarwin')
        self.CurPlatform = 'osx'
        self.CurArchitecture = 'x86_64'
        libs = funcBuild(self)
        for l in libs:
            shutil.copy(l, os.path.join(self.InstallDir, 'osx', 'lib'))

        # copy include files
        funcCopy = getattr(mod, 'copyIncludeFiles')
        funcCopy(self, os.path.join(self.InstallDir, 'osx', 'include'))

        os.chdir(self.SavedCWD)
        self.cleanupBuildDir()

        if self.OptOSXInstallDir != '':
            self.copyTree(os.path.join(self.InstallDir, 'osx'), self.OptOSXInstallDir)


    def buildIos(self, name, mod):

        # create output directory structure
        self.mkDir(os.path.join(self.InstallDir, 'ios'))
        self.mkDir(os.path.join(self.InstallDir, 'ios', 'include'))
        self.mkDir(os.path.join(self.InstallDir, 'ios', 'lib'))

        # build variants
        variants = self.Settings['ios']['architectures']
        allLibs = []
        for i in range(0, len(variants)):
            v = variants[i]
            print('-----------------------------------------')
            print('building %s for %s' % (name, v))
            self.unpackPackage()
            funcBuild = getattr(mod, 'buildDarwin')
            self.CurPlatform = v.split('@')[0]
            self.CurArchitecture = v.split('@')[1]
            libs = funcBuild(self)
            allLibs.append(libs)
            if i == 0: # copy include files
                funcCopy = getattr(mod, 'copyIncludeFiles')
                funcCopy(self, os.path.join(self.InstallDir, 'ios', 'include'))
            os.chdir(self.SavedCWD)
            self.cleanupBuildDir()

        # merge libraries to fat lib
        count = len(allLibs[0])
        for i in range(1, len(allLibs)):
            c = len(allLibs[i])
            if c != count:
                self.printErrorAndExit('all variants must return the same number of libs')

        for i in range(0, count):
            merge = []
            for libs in allLibs:
                merge.append(libs[i])
            self.mergeLibs(merge, os.path.join(self.InstallDir, 'ios', 'lib', os.path.basename(merge[0])))

        if self.OptIOSInstallDir != '':
            self.copyTree(os.path.join(self.InstallDir, 'ios'), self.OptIOSInstallDir)

    def buildDroid(self, name, mod):

        self.checkDroidSetup()

        # create output directory structure
        self.mkDir(os.path.join(self.InstallDir, 'droid'))

        # build variants
        variants = [ ['x86', 'x86'], ['armeabi-v7a', 'armv7'] ]

        for i in range(0, len(variants)):
            v = variants[i]
            print('-----------------------------------------')
            print('building %s for droid' % (name))
            self.writeLog('-----------------------------------------')
            self.writeLog('Building %s for droid' % (name))
            self.unpackPackage()
            self.CurDroidABI = v[0]
            self.CurPlatform = 'droid'
            self.CurArchitecture = v[1]
            self.droidMakeToolchain(self.CurDroidABI)
            self.writeLog('BuildDir: %s' % self.getBuildDir())
            self.writeLog('Platform: %s' % self.getCurPlatform())
            self.writeLog('Architecture: %s' % self.getCurArchitecture())
            funcBuild = getattr(mod, 'buildDroid')
            libs = funcBuild(self)

            abidir = os.path.join(self.InstallDir, 'droid', self.CurDroidABI)
            self.mkDir(abidir)
            self.mkDir(os.path.join(abidir, 'lib'))
            for l in libs:
                shutil.copy(l, os.path.join(abidir, 'lib'))

            funcCopy = getattr(mod, 'copyIncludeFiles')
            funcCopy(self, os.path.join(abidir, 'include'))

            os.chdir(self.SavedCWD)
            self.cleanupBuildDir()

        if self.OptDroidInstallDir != '':
            self.copyTree(os.path.join(self.InstallDir, 'droid'), self.OptDroidInstallDir)

    def buildLinux(self, name, mod):

        # create output directory structure
        self.mkDir(os.path.join(self.InstallDir, 'linux'))

        if self.CurArchitecture == '':
            self.CurArchitecture = platform.machine()

        self.writeLog('Build for architecture: %s' % self.CurArchitecture);

        print('-----------------------------------------')
        print('building %s for linux' % (name))
        self.unpackPackage()
        self.CurPlatform = 'linux'
        # self.linuxMakeToolchain(self.CurDroidABI)
        funcBuild = getattr(mod, 'buildLinux')
        libs = funcBuild(self)

        abidir = os.path.join(self.InstallDir, 'linux', self.CurArchitecture)
        self.mkDir(abidir)
        self.mkDir(os.path.join(abidir, 'lib'))
        for l in libs:
            shutil.copy(l, os.path.join(abidir, 'lib'))

        funcCopy = getattr(mod, 'copyIncludeFiles')
        funcCopy(self, os.path.join(abidir, 'include'))

        # copy pkgconfig files, if any
        try:
            funcCopy = getattr(mod, 'copyPkgConfigFiles')
        except AttributeError:
            funcCopy = None
        if funcCopy:
            funcCopy(self, os.path.join(abidir, 'lib', 'pkgconfig'))

        os.chdir(self.SavedCWD)
        self.cleanupBuildDir()

        if self.OptLinuxInstallDir != '':
            self.copyTree(os.path.join(self.InstallDir, 'linux', self.CurArchitecture), self.OptLinuxInstallDir)

    def build(self, name):
        self.writeLog("Starting to build lib " + name)
        self.PackageURL = ''
        try:
            mod = importlib.import_module('mods.'+name)
        except ImportError as err:
            self.printErrorAndExit('failed to load module %s (%s)' % (name, err))
        except Exception as err:
            self.printErrorAndExit('failed to load module %s (%s: %s)' % (name, sys.exc_info()[0], err))

        func = getattr(mod, 'start')
        func(self)
        if self.PackageURL != '':
            # download the package
            self.downloadPackage()

        if 'ios' in self.Targets:
            self.buildIos(name, mod)
        if 'osx' in self.Targets:
            self.buildOsx(name, mod)
        if 'droid' in self.Targets:
            self.buildDroid(name, mod)
        if 'linux' in self.Targets:
            self.buildLinux(name, mod)

        self.writeLog("Finished to build lib " + name)

    def parseOptions(self):
        cmdLineParser = argparse.ArgumentParser('Simple Dependency Build Tool')
        cmdLineParser.add_argument('--force-download', '-d', action='store_true', help='don\'t use already downloaded packages')
        cmdLineParser.add_argument('--target', '-t', metavar='TARGET', action='append', help='add build target (ios, droid, liux)')
        cmdLineParser.add_argument('--ndk', metavar='DIR', help='android NDK directory')
        cmdLineParser.add_argument('--droidinstall', metavar='DIR', help='install directory for android libs/include files')
        cmdLineParser.add_argument('--iosinstall', metavar='DIR', help='install directory for ios libs/include files')
        cmdLineParser.add_argument('--osxinstall', metavar='DIR', help='install directory for osx libs/include files')
        cmdLineParser.add_argument('--linuxinstall', metavar='DIR', help='install directory for linux libs/include files')
        cmdLineParser.add_argument('libstobuild', nargs='+', metavar='LIB', help='libraries to build (space separated)')
        cmdLineArgs = cmdLineParser.parse_args()

        if cmdLineArgs.force_download:
            self.OptForceDownload = True
        if cmdLineArgs.target:
            self.Targets += cmdLineArgs.target
            for t in self.Targets:
                if not t in self.KnownTargets:
                    self.printErrorAndExit("ERROR: Unknown target %s" % t)
        if cmdLineArgs.ndk:
            self.OptNdkDir = cmdLineArgs.ndk
        if cmdLineArgs.droidinstall:
            self.OptDroidInstallDir = cmdLineArgs.droidinstall
            if not os.path.isdir(self.OptDroidInstallDir):
                self.printErrorAndExit('%s is not a directory' % self.OptDroidInstallDir)
        if cmdLineArgs.iosinstall:
            self.OptIOSInstallDir = cmdLineArgs.iosinstall
            if not os.path.isdir(self.OptIOSInstallDir):
                self.printErrorAndExit('%s is not a directory' % self.OptIOSInstallDir)
        if cmdLineArgs.osxinstall:
            self.OptOSXInstallDir = cmdLineArgs.osxinstall
            if not os.path.isdir(self.OptOSXInstallDir):
                self.printErrorAndExit('%s is not a directory' % self.OptOSXInstallDir)
        if cmdLineArgs.linuxinstall:
            self.OptLinuxInstallDir = cmdLineArgs.linuxinstall
            if not os.path.isdir(self.OptLinuxInstallDir):
                self.printErrorAndExit('%s is not a directory' % self.OptLinuxInstallDir)
        if not self.Targets:
            self.Targets = self.KnownTargets
        self.LibsToBuild = cmdLineArgs.libstobuild

    def run(self):
        self.writeLog("Starting build for libs: " + ','.join(self.LibsToBuild) + " targets: " + ','.join(self.Targets))
        for l in self.LibsToBuild:
            self.build(l)
def main():
    d = builder()
    d.parseOptions()
    d.setup()
    d.run()

if __name__ == "__main__":
    main()
