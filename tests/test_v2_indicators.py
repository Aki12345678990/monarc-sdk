"""Hand-built cases ported from pipeline_v2/test_indicators_v2.py."""

from analyzer_core import v2_constants as cfg
from analyzer_core.attribution import classify_package
from analyzer_core.config import reference_dir
from analyzer_core.indicators.v2_rules import (
    READ_CELL_BROADCASTS,
    READ_MEDIA_VISUAL_USER_SELECTED,
    accept_host,
    compute_a,
    compute_f_backup,
    compute_f_cleartext,
    compute_f_debug,
    compute_n,
    compute_p,
    effective_exported,
    load_permission_lists,
    load_psl,
    m_exp_decision,
    psl_and_extension,
    registrable_domain,
)

PERM_LISTS = load_permission_lists(reference_dir() / "dangerous_permissions_v2.csv")
PSL = load_psl(reference_dir() / "public_suffix_list_9dfbe81.dat")
_PSL, EXT = psl_and_extension()
MINI_CATALOG = [
    {
        "prefix": "com.adsdk.",
        "sdk_name": "AdSDK",
        "category": "ads",
        "source": "test",
        "match_type": "prefix",
    }
]
APP_ID = "com.myapp"


def attr(pkg):
    return classify_package(pkg, APP_ID, MINI_CATALOG, cfg)[0]


def test_explicit_exported_and_defaults():
    assert effective_exported("true", False, "activity", 28) == "yes"
    assert effective_exported("false", True, "activity", 28) == "no"
    assert effective_exported("", True, "activity", 30) == "yes"
    assert effective_exported("", False, "activity", 30) == "no"
    assert effective_exported("", True, "activity", 31) == "anomaly"
    assert effective_exported("", False, "provider", 16) == "yes"
    assert effective_exported("", False, "provider", 17) == "no"


def test_launcher_excluded_and_provider_permission():
    assert m_exp_decision("true", True, "activity", 28, "", "", "", True) == "exclude_launcher"
    assert m_exp_decision("true", True, "activity", 28, "", "", "", False) == "count"
    assert (
        m_exp_decision("true", False, "provider", 28, "", "android.permission.READ", "", False)
        == "exclude_protected"
    )


def test_cleartext_and_flags():
    nsc = {
        "base_config_present": "True",
        "base_config_cleartext": "true",
        "n_domain_config_cleartext_true": "0",
    }
    assert compute_f_cleartext(nsc, "false", 33) == 1
    nsc_abs = {
        "base_config_present": "False",
        "base_config_cleartext": "absent",
        "n_domain_config_cleartext_true": "0",
    }
    assert compute_f_cleartext(nsc_abs, "false", 27) == 1
    assert compute_f_cleartext(nsc_abs, "false", 28) == 0
    domain = {
        "base_config_present": "True",
        "base_config_cleartext": "false",
        "n_domain_config_cleartext_true": "1",
    }
    assert compute_f_cleartext(domain, "false", 33) == 1
    base_false = {
        "base_config_present": "True",
        "base_config_cleartext": "false",
        "n_domain_config_cleartext_true": "0",
    }
    assert compute_f_cleartext(base_false, "true", 24) == 0
    assert compute_f_cleartext(None, "true", 33) == 1
    assert compute_f_cleartext(None, "false", 24) == 0
    assert compute_f_cleartext(None, "", 27) == 1
    assert compute_f_cleartext(None, "", 28) == 0
    assert compute_f_debug("true") == 1
    assert compute_f_debug("") == 0
    assert compute_f_debug("false") == 0
    assert compute_f_backup("") == 1
    assert compute_f_backup("true") == 1
    assert compute_f_backup("false") == 0
    assert compute_f_debug(None) is None
    assert compute_f_backup(None) is None
    assert compute_f_cleartext(None, None, 33) is None


def test_permission_rules():
    dup = [
        {"tag": "uses-permission", "name": "android.permission.CAMERA", "max_sdk_version": ""},
        {"tag": "uses-permission", "name": "android.permission.CAMERA", "max_sdk_version": ""},
    ]
    assert compute_p(dup, 24, PERM_LISTS)[0]["P"] == 1
    sdk23 = [
        {"tag": "uses-permission-sdk-23", "name": "android.permission.CAMERA", "max_sdk_version": ""}
    ]
    assert compute_p(sdk23, 24, PERM_LISTS)[0]["P"] == 1
    below = [{"tag": "uses-permission", "name": "android.permission.CAMERA", "max_sdk_version": "23"}]
    equal = [{"tag": "uses-permission", "name": "android.permission.CAMERA", "max_sdk_version": "24"}]
    above = [{"tag": "uses-permission", "name": "android.permission.CAMERA", "max_sdk_version": "25"}]
    assert compute_p(below, 24, PERM_LISTS)[0]["P"] == 0
    assert compute_p(equal, 24, PERM_LISTS)[0]["P"] == 1
    assert compute_p(above, 24, PERM_LISTS)[0]["P"] == 1
    assert compute_p(below, 24, PERM_LISTS)[0]["P_declared"] == 1
    malformed = [
        {
            "tag": "uses-permission",
            "name": 'android.permission.WRITE_EXTERNAL_STORAGE" android:maxSdkVersion="29',
            "max_sdk_version": "",
        }
    ]
    assert compute_p(malformed, 24, PERM_LISTS)[0]["P"] == 0
    cell = [{"tag": "uses-permission", "name": READ_CELL_BROADCASTS, "max_sdk_version": ""}]
    vals = compute_p(cell, 24, PERM_LISTS)[0]
    assert vals["P"] == 0
    assert vals["P_all"] == 1
    assert vals["P_ext"] == 0
    media = [{"tag": "uses-permission", "name": READ_MEDIA_VISUAL_USER_SELECTED, "max_sdk_version": ""}]
    vals = compute_p(media, 24, PERM_LISTS)[0]
    assert vals["P"] == 0
    assert vals["P_ext"] == 1
    assert vals["P_all"] == 0


def _api(calls):
    primary = {("android.foo.Bar", "open"): {}, ("android.foo.Bar", "cond"): {}}
    axp = {("android.axp.X", "y"): {}}
    conditional = {("android.foo.Bar", "cond")}
    return compute_a(calls, APP_ID, MINI_CATALOG, {}, primary, axp, conditional)


def test_api_rules():
    both = [
        {"caller_package": "com.adsdk.a", "target_class": "android.foo.Bar", "target_method": "open", "n_callsites": 3},
        {"caller_package": "com.adsdk.b", "target_class": "android.foo.Bar", "target_method": "open", "n_callsites": 4},
    ]
    result = _api(both)
    assert attr("com.adsdk.a") == "sdk"
    assert result["A"] == 1
    assert result["A_calls"] == 7
    first = _api(
        [{"caller_package": "com.myapp.ui", "target_class": "android.foo.Bar", "target_method": "open", "n_callsites": 2}]
    )
    assert attr("com.myapp.ui") == "first_party"
    assert first["A"] == 0
    assert first["A_all"] == 1
    ax = _api(
        [{"caller_package": "com.adsdk.a", "target_class": "android.axp.X", "target_method": "y", "n_callsites": 1}]
    )
    assert ax["A"] == 0
    assert ax["A_all"] == 0
    assert ax["A_union"] == 1
    cond = _api(
        [{"caller_package": "com.adsdk.a", "target_class": "android.foo.Bar", "target_method": "cond", "n_callsites": 1}]
    )
    assert cond["A"] == 1
    assert cond["A_noncond"] == 0


def test_host_rules():
    assert accept_host("foo.example.com", False, PSL, EXT, True) is False
    denied = compute_n(
        [{"host": "foo.example.com", "caller_package": "com.adsdk.a", "ip_literal": False}],
        APP_ID,
        MINI_CATALOG,
        {},
        PSL,
        EXT,
    )
    assert denied["N"] == 0
    assert denied["N_all"] == 0
    assert accept_host("sub.w3.org", False, PSL, EXT, True) is False
    assert accept_host("sub.w3.org", False, PSL, EXT, False) is True
    assert accept_host("javax.xml.xmlconstants", False, PSL, EXT, True) is False
    assert accept_host("127.0.0.1", True, PSL, EXT, True) is False
    assert accept_host("10.0.0.1", True, PSL, EXT, True) is False
    assert accept_host("::1", True, PSL, EXT, True) is False
    assert accept_host("8.8.8.8", True, PSL, EXT, True) is True
    collapsed = compute_n(
        [
            {"host": "a.example-vendor.com", "caller_package": "com.adsdk.a", "ip_literal": False},
            {"host": "b.example-vendor.com", "caller_package": "com.adsdk.a", "ip_literal": False},
        ],
        APP_ID,
        MINI_CATALOG,
        {},
        PSL,
        EXT,
    )
    assert collapsed["N"] == 2
    assert registrable_domain("foo.bar.ck", PSL) == "foo.bar.ck"
    assert registrable_domain("www.ck", PSL) == "www.ck"
