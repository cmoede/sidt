#!/usr/bin/python

settings = {
    'ios': 
    {
        'bitcode':False,
        'architectures': ['iPhoneSimulator@i386', 'iPhoneSimulator@x86_64', 'iPhoneOS@armv7', 'iPhoneOS@armv7s', 'iPhoneOS@arm64']
    },
    'droid':
    {
        'ndk':'/opt/android-ndk-r12b',
        'platform':'android-17',
        'architectures' : ['armeabi', 'armeabi-v7a', 'armeabi-v7a-hard', 'arm64-v8a', 'x86', 'x86_64', 'mips', 'mips64' ]
    }
}
