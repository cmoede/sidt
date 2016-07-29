#!/usr/bin/python

import sys
import os
import subprocess
import shutil
import importlib

class builder:
    PackageURL = 'narf'
    SavedCWD = os.getcwd()
    LogFile = ''
    PackageDir = ''
    BuildDir = ''
    TmpDir = ''
    InstallDir = ''
    DroidToolchainDir = ''
        
    Settings = None      

    LibsToBuild = []  

    KnownTargets = ['ios', 'droid']
    Targets = []
   
    # current build state 
    CurPlatform = ''
    CurArchitecture = ''
    CurDroidABI = ''
   
    # options
    OptForceDownload = False 
    OptDroidInstallDir = ''
    OptIOSInstallDir = ''
    OptNdkDir = ''

    def __init__(self):
        configMod = importlib.import_module('config')
        self.Settings = configMod.settings


    def setup(self):
        print('logging to build.log')
        self.LogFile = open('build.log', 'wb')
        if self.LogFile == None:
            self.printErrorAndExit(self, 'Failed to create logfile')        
        
        self.SavedCWD = os.getcwd()
        self.PackageDir = os.path.join(self.SavedCWD, 'packages') 
        if not os.path.exists(self.PackageDir):
            os.mkdir(self.PackageDir)
        
        self.BuildDir = os.path.join(self.SavedCWD, 'build') 
        self.rmDir(self.BuildDir)
        if not os.path.exists(self.BuildDir):
            os.mkdir(self.BuildDir)
    
        self.TmpDir = os.path.join(self.SavedCWD, 'tmp')
        self.rmDir(self.TmpDir)
        os.mkdir(self.TmpDir)    

        self.DroidToolchainDir = os.path.join(self.SavedCWD, 'toolchain')
        self.rmDir(self.DroidToolchainDir)

        self.InstallDir = os.path.join(self.SavedCWD, 'install')
        if not os.path.exists(self.InstallDir):
            os.mkdir(self.InstallDir)
    

    def printUsageAndExit():
        print('Usage:')
        print('build.py module')
        sys.exit(0) 

    def printErrorAndExit(self, err):
        os.chdir(self.SavedCWD)
        print('error: %s' % err)
        sys.exit(1)
    
    def printHelp():
        print('Simple Dependency Build Tool')
        sys.exit(0) 

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
        self.rmDir(self.DroidToolchainDir)
        self.mkDir(self.DroidToolchainDir)

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

    def getDroidPlatformDir(self):
        return os.path.join(self.Settings['droid']['ndk'], 'platforms', self.Settings['droid']['platform'], 'arch-arm')
    
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
        p = subprocess.Popen(args, stdout=self.LogFile, stderr=self.LogFile, shell = shell,  env=env)
        ret = p.wait()
        if ret != 0 and not ignoreError:
            print('subprocess.call failed with code %d' % ret)
            print('args: %s' % args)
            sys.exit(1)
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
            return
        
        print('downloading %s' % self.PackageURL)
        self.rmFile(self.getPackageFileName())
        self.execCmd(['curl', '-Lo', 'package.download', self.PackageURL])
        os.rename('package.download', self.getPackageFileName())  
        os.chdir(self.SavedCWD)

    def setPackage(self, url):
        print('setPackage %s' % url)
        self.PackageURL = url
    
    # returns the package filename
    def getPackageFileName(self):
        return self.PackageURL.rsplit('/', 1)[1] 

    def unpackPackage(self):
        print('extracting...')
        packageName = self.PackageURL.rsplit('/', 1)[1]
        os.chdir(self.BuildDir)
        path = os.path.join(self.PackageDir, packageName)
        ret = self.execCmd(['tar', 'zxf', path], ignoreError = True)
        if ret != 0:
            print('failed to unpack %s - removing tar file' % path)
            os.remove(path)
            sys.exit(1)
        os.chdir(self.SavedCWD)

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

    def buildIos(self, name, mod):

        # create output directory structure
        self.mkDir(os.path.join(self.InstallDir, 'ios'))
        self.mkDir(os.path.join(self.InstallDir, 'ios', 'include'))
        self.mkDir(os.path.join(self.InstallDir, 'ios', 'lib'))

        # build variants
        variants = [ ['iPhoneSimulator', 'x86_64'], ['iPhoneOS', 'armv7'], ['iPhoneOS', 'armv7s'], ['iPhoneOS', 'arm64']]
        variants = self.Settings['ios']['architectures']
        allLibs = []
        for i in range(0, len(variants)):
            v = variants[i]
            print('-----------------------------------------')
            print('building %s for %s' % (name, v))    
            self.unpackPackage()
            funcBuild = getattr(mod, 'buildIos')
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
        self.mkDir(os.path.join(self.InstallDir, 'droid', 'include'))
       
        # build variants
        variants = [ ['x86', 'x86'], ['armeabi-v7a', 'armv7'] ]
        
        for i in range(0, len(variants)):
            v = variants[i]
            print('-----------------------------------------')
            print('building %s for droid' % (name))    
            self.unpackPackage()
            self.CurDroidABI = v[0]
            self.CurPlatform = 'droid'
            self.CurArchitecture = v[1]
            self.droidMakeToolchain(self.CurDroidABI)
            funcBuild = getattr(mod, 'buildDroid')
            libs = funcBuild(self) 
        
            abidir = os.path.join(self.InstallDir, 'droid', self.CurDroidABI)
            self.mkDir(abidir)
            for l in libs:
                shutil.copy(l, abidir)       
 
            funcCopy = getattr(mod, 'copyIncludeFiles')
            funcCopy(self, os.path.join(self.InstallDir, 'droid', 'include'))
        
            os.chdir(self.SavedCWD)
            self.cleanupBuildDir()

        if self.OptDroidInstallDir != '':
            self.copyTree(os.path.join(self.InstallDir, 'droid'), self.OptDroidInstallDir) 

    def build(self, name):
        self.PackageURL = ''
        try:
            mod = importlib.import_module('mods.'+name)
        except ImportError as err:
            self.printErrorAndExit('failed to load module %s' % (name))
        except:
            self.printErrorAndExit('failed to load module %s (%s)' % (name, sys.exc_info()[0]))

        func = getattr(mod, 'start')
        func(self)
        if self.PackageURL == '':
            self.printErrorAndExit('setPackage not called')

        # download the package
        self.downloadPackage() 
       
        if 'ios' in self.Targets:
            self.buildIos(name, mod)
        if 'droid' in self.Targets:
            self.buildDroid(name, mod)
    
    def parseArgValue(self, args, i):
        arg = args[i]
        if arg.find('=') != -1:
            return [arg.split('=')[1], 0]
        if i + 1 >= len(args):
            self.printErrorAndExit('missing argument')
        return [args[i+1], 1]

    
    def parseOptions(self):
        i = 1 
        while i < len(sys.argv):
            arg = sys.argv[i]
            if arg == '--force-download' or arg == '-d':
                self.OptForceDownload = True
            elif arg == '-t' or arg.find('-t=') == 0 or arg == '--target' or arg.find('--target=') == 0:
                res = self.parseArgValue(sys.argv, i)
                self.Targets.append(res[0])
                i = i + res[1] 
            elif arg == '--ndk' or arg.find('--ndk') == 0:
                res = self.parseArgValue(sys.argv, i)
                self.OptNdkDir = res[0]
                i = i + res[1]
            elif arg == '--droidinstall' or arg.find('--droidinstall=') == 0:
                res = self.parseArgValue(sys.argv, i)  
                self.OptDroidInstallDir = res[0]
                if not os.path.isdir(self.OptDroidInstallDir):
                    self.printErrorAndExit('%s is not a directory' % self.OptDroidInstallDir)
                i = i + res[1]              
            elif arg == '--iosinstall' or arg.find('--iosinstall=') == 0:
                res = self.parseArgValue(sys.argv, i)  
                self.OptIOSInstallDir = res[0]
                if not os.path.isdir(self.OptIOSInstallDir):
                    self.printErrorAndExit('%s is not a directory' % self.OptIOSInstallDir)
                i = i + res[1]              
            else:
                if arg.find('-') == 0:
                    self.printErrorAndExit('error: unhandled option %s' % arg)
                else:
                    self.LibsToBuild.append(arg)       
            i = i + 1
        if not self.Targets:
            self.Targets = self.KnownTargets
        if len(self.LibsToBuild) == 0:
            self.printErrorAndExit('no libraries given')
      
    def run(self):
        for l in self.LibsToBuild:
            self.build(l)
def main():
    d = builder()
    d.parseOptions()
    d.setup()
    d.run()

if __name__ == "__main__":
    main()
