"""Frozen v2 constants copied verbatim from config_v2.py.

Ported from config_v2.py:16-125 (v2). Values are asserted against the
vendored file by tests/test_v2_constants.py via ast.literal_eval (no import,
no exec).
"""

TOOLCHAIN_PREFIXES = [
    "android.",
    "androidx.",
    "android.support.",
    "java.",
    "javax.",
    "kotlin.",
    "kotlinx.",
    "dalvik.",
    "org.jetbrains.",
    "org.intellij.",
    "com.google.android.material.",
    "com.google.errorprone.",
    "com.google.j2objc.",
    "org.checkerframework.",
    "org.codehaus.mojo.",
    "com.google.auto.",
    "org.chromium.support_lib_boundary.",
    "_COROUTINE.",
    "org.junit.",
    "junit.",
    "org.hamcrest.",
    "net.jcip.annotations.",
    "j$.",
]

FRAMEWORK_PREFIXES = {
    "flutter": ["io.flutter."],
    "react_native": [
        "com.facebook.react.",
        "com.facebook.hermes.",
        "com.swmansion.",
        "com.facebook.fbreact.",
        "com.facebook.debug.",
        "com.facebook.perftest.",
        "com.facebook.v8.",
        "org.webkit.androidjsc.",
    ],
    "unity": [
        "com.unity3d.player.",
        "bitter.jnibridge.",
        "org.fmod.",
        "com.unity3d.EditorPlugin.",
    ],
    "xamarin_maui": ["mono.android.", "mono.", "crc64", "com.xamarin.", "xamarin."],
    "cordova_capacitor": [
        "org.apache.cordova.",
        "com.getcapacitor.",
        "com.ionicframework.cordova.",
    ],
    "cocos2dx": ["org.cocos2dx."],
}

FRAMEWORK_NATIVE_LIBS = {
    "flutter": ["libflutter.so", "libapp.so"],
    "react_native": ["libreactnativejni.so", "libhermes.so", "libjsc.so"],
    "unity": ["libunity.so", "libil2cpp.so"],
    "xamarin_maui": ["libmonodroid.so", "libmonosgen-2.0.so"],
    "cocos2dx": ["libcocos2dcpp.so", "libcocos2djs.so"],
}

SDK_CATEGORY_VOCABULARY = [
    "ads",
    "analytics",
    "attribution",
    "crash_reporting",
    "social",
    "networking",
    "payments",
    "maps_location",
    "push_messaging",
    "ui",
    "game_engine",
    "cloud_backend",
    "utility",
    "uncertain",
    "media",
    "framework_plugin",
]

SERVICE_SDK_CATEGORIES = {
    "ads",
    "analytics",
    "attribution",
    "crash_reporting",
    "social",
    "payments",
    "maps_location",
    "push_messaging",
    "cloud_backend",
}

HOST_DENYLIST = [
    "schemas.android.com",
    "www.w3.org",
    "ns.adobe.com",
    "xmlpull.org",
    "www.xmlpull.org",
    "xml.apache.org",
    "schemas.xmlsoap.org",
    "purl.org",
    "json-schema.org",
    "example.com",
    "example.org",
    "example.net",
    "schemas.microsoft.com",
    "schemas.openxmlformats.org",
]

ANDROID_NS = "http://schemas.android.com/apk/res/android"
