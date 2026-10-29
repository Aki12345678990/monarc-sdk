import os

ROOT = os.environ.get("ANDROZOO_ROOT", r"E:\AndroZoo")
APK_DIR = os.path.join(ROOT, "apks")
METADATA_DIR = os.path.join(ROOT, "metadata")
SAMPLE_CSV = os.path.join(METADATA_DIR, "sample_v2.csv")
RESULTS_V2 = os.path.join(ROOT, "analyzer", "results_v2")
RAW_DIR = os.path.join(RESULTS_V2, "raw")
RAW_CALLS_DIR = os.path.join(RESULTS_V2, "raw_calls")
EXTRACT_LOG = os.path.join(RESULTS_V2, "extract_run_log.csv")

PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
SDK_CATALOG_CSV = os.path.join(PIPELINE_DIR, "sdk_catalog.csv")
SENSITIVE_API_MAP_CSV = os.path.join(PIPELINE_DIR, "sensitive_api_map_SEED_TEST.csv")

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
