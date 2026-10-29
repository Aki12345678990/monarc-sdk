"""Port of pipeline_v2/test_classify.py asserts (meaning unchanged)."""

import pytest

from analyzer_core import v2_constants as cfg
from analyzer_core.attribution import (
    classify_package,
    host_denied,
    host_ok,
    load_catalog,
    validate_catalog,
)


@pytest.fixture(scope="module")
def catalog():
    loaded = load_catalog()
    return [
        {
            "prefix": "com.foo.",
            "sdk_name": "Foo",
            "category": "uncertain",
            "source": "test",
            "match_type": "prefix",
        }
    ] + loaded


def _cat(pkg, catalog, app=""):
    return classify_package(pkg, app, catalog, cfg)


def test_kotlin_is_toolchain(catalog):
    r = _cat("kotlin", catalog)
    assert r[0] == "toolchain", r


def test_kotlin_collections_is_toolchain(catalog):
    r = _cat("kotlin.collections", catalog)
    assert r[0] == "toolchain", r


def test_material_is_toolchain(catalog):
    r = _cat("com.google.android.material", catalog)
    assert r[0] == "toolchain", r


def test_com_foobar_is_not_foo_sdk(catalog):
    r = _cat("com.foobar", catalog)
    assert r[0] != "sdk" or r[1] != "Foo", r
    assert not ("com.foobar" + ".").startswith("com.foo.")


def test_react_bridge_is_framework(catalog):
    r = _cat("com.facebook.react.bridge", catalog)
    assert r[0] == "framework" and r[3] == "react_native", r


def test_unity_player_is_framework(catalog):
    r = _cat("com.unity3d.player", catalog)
    assert r[0] == "framework" and r[3] == "unity", r


def test_unity_ads_is_sdk_not_framework(catalog):
    r = _cat("com.unity3d.ads", catalog)
    assert r[0] == "sdk", r
    assert r[0] != "framework", r


def test_host_ok_www_dot():
    ok, ip = host_ok("www.")
    assert ok is False, (ok, ip)


def test_host_ok_example_com():
    ok, ip = host_ok("example.com")
    assert ok is False, (ok, ip)


def test_host_ok_foo_example_com():
    ok, ip = host_ok("foo.example.com")
    assert ok is False, (ok, ip)


def test_host_ok_schemas_microsoft():
    ok, ip = host_ok("schemas.microsoft.com")
    assert ok is False, (ok, ip)


def test_host_ok_github():
    ok, ip = host_ok("github.com")
    assert ok is True and ip is False, (ok, ip)


def test_host_ok_ip():
    ok, ip = host_ok("8.8.8.8")
    assert ok is True and ip is True, (ok, ip)


def test_host_denied_example_org():
    assert host_denied("page.example.org") is True


def test_com_facebook_is_facebook_sdk(catalog):
    r = _cat("com.facebook", catalog)
    assert r[0] == "sdk" and r[1] == "Facebook SDK", r


def test_facebook_login_widget_is_facebook_sdk(catalog):
    r = _cat("com.facebook.login.widget", catalog)
    assert r[0] == "sdk" and r[1] == "Facebook SDK", r


def test_facebook_soloader_is_meta_oss(catalog):
    r = _cat("com.facebook.soloader", catalog)
    assert r[0] == "sdk" and r[1] == "Meta OSS libraries", r


def test_fbreact_specs_is_react_native(catalog):
    r = _cat("com.facebook.fbreact.specs", catalog)
    assert r[0] == "framework" and r[3] == "react_native", r


def test_errorprone_is_toolchain(catalog):
    r = _cat("com.google.errorprone.annotations", catalog)
    assert r[0] == "toolchain", r


def test_bitter_jnibridge_is_unity(catalog):
    r = _cat("bitter.jnibridge", catalog)
    assert r[0] == "framework" and r[3] == "unity", r


def test_org_fmod_is_unity(catalog):
    r = _cat("org.fmod", catalog)
    assert r[0] == "framework" and r[3] == "unity", r


def test_facebook_katana_feed_is_first_party_exact(catalog):
    r = _cat("com.facebook.katana.feed", catalog, "com.facebook.katana")
    assert r[0] == "first_party" and r[4] == "exact", r


def test_facebook_login_under_katana_is_sdk(catalog):
    r = _cat("com.facebook.login", catalog, "com.facebook.katana")
    assert r[0] == "sdk" and r[1] == "Facebook SDK", r


def test_gms_internal_ads_is_google_mobile_ads(catalog):
    r = _cat("com.google.android.gms.internal.ads", catalog, "com.example.app")
    assert r[0] == "sdk" and r[1] == "Google Mobile Ads" and r[2] == "ads", r


def test_mlkit_vision_digital_ink(catalog):
    r = _cat("com.google.android.gms.internal.mlkit_vision_digital_ink", catalog)
    assert r[0] == "sdk" and r[1] == "ML Kit", r


def test_gms_foo_is_play_services_other(catalog):
    r = _cat("com.google.android.gms.foo", catalog)
    assert r[0] == "sdk" and r[1] == "Google Play Services (other)", r


def test_google_android_a_unresolved(catalog):
    r = _cat("com.google.android.a", catalog)
    assert r[0] == "sdk" and r[1] == "Google (unresolved)", r


def test_facebook_k_n_is_meta_unresolved(catalog):
    r = _cat("com.facebook.k.n", catalog)
    assert r[0] == "sdk" and r[1] == "Meta (unresolved)", r


def test_fresco(catalog):
    r = _cat("com.facebook.imagepipeline.core", catalog)
    assert r[0] == "sdk" and r[1] == "Fresco", r


def test_facebook_debug_holder_is_react_native(catalog):
    r = _cat("com.facebook.debug.holder", catalog)
    assert r[0] == "framework" and r[3] == "react_native", r


def test_coroutine_is_toolchain(catalog):
    r = _cat("_COROUTINE", catalog)
    assert r[0] == "toolchain", r


def test_picasso(catalog):
    r = _cat("com.squareup.picasso", catalog)
    assert r[0] == "sdk" and r[1] == "Picasso", r


def test_junit_is_toolchain(catalog):
    r = _cat("org.junit.runner", catalog)
    assert r[0] == "toolchain", r


def test_desugar_jdollar_is_toolchain(catalog):
    r = _cat("j$.time", catalog)
    assert r[0] == "toolchain", r


def test_xamarin_forms_is_framework(catalog):
    r = _cat("com.xamarin.forms.platform.android", catalog)
    assert r[0] == "framework" and r[3] == "xamarin_maui", r


def test_cocos2dx_is_framework(catalog):
    r = _cat("org.cocos2dx.lib", catalog)
    assert r[0] == "framework" and r[3] == "cocos2dx", r


def test_gms_identity_intents_is_google_pay(catalog):
    r = _cat("com.google.android.gms.identity.intents.model", catalog)
    assert r[0] == "sdk" and r[1] == "Google Pay", r


def test_gms_identity_is_play_services_auth(catalog):
    r = _cat("com.google.android.gms.identity", catalog)
    assert r[0] == "sdk" and r[1] == "Google Play Services Auth", r


def test_tagmanager_legacy(catalog):
    r = _cat("com.google.android.gms.tagmanager_legacy", catalog)
    assert r[0] == "sdk" and r[1] == "Google Tag Manager", r


def test_pangle(catalog):
    r = _cat("com.bytedance.sdk.component.g", catalog)
    assert r[0] == "sdk" and r[1] == "Pangle", r


def test_bytedance_unresolved(catalog):
    r = _cat("com.bytedance", catalog)
    assert r[0] == "sdk" and r[1] == "ByteDance (unresolved)", r


def test_amazon_publisher_services(catalog):
    r = _cat("com.amazon.device.ads", catalog)
    assert r[0] == "sdk" and r[1] == "Amazon Publisher Services", r


def test_expo_modules(catalog):
    r = _cat("expo.modules.core", catalog)
    assert r[0] == "sdk" and r[1] == "Expo modules", r


def test_app_center_crashes(catalog):
    r = _cat("com.microsoft.appcenter.crashes", catalog)
    assert r[0] == "sdk" and r[1] == "App Center Crashes" and r[2] == "crash_reporting", r


def test_google_android_a_unresolved_again(catalog):
    r = _cat("com.google.android.a", catalog)
    assert r[0] == "sdk" and r[1] == "Google (unresolved)", r


def test_sqlcipher(catalog):
    r = _cat("net.sqlcipher.database", catalog)
    assert r[0] == "sdk" and r[1] == "SQLCipher", r


def test_unity_levelplay(catalog):
    r = _cat("com.unity3d.mediation.banner", catalog)
    assert r[0] == "sdk" and r[1] == "Unity LevelPlay Mediation", r


def test_amazon_unresolved(catalog):
    r = _cat("com.amazon.a.a.b", catalog)
    assert r[0] == "sdk" and r[1] == "Amazon (unresolved)", r


def test_validate_catalog():
    validate_catalog()
