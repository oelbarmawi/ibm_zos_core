# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest
from pprint import pprint

EXISTING_DATA_SET = "user.private.proclib"
DEFAULT_DATA_SET = "user.private.rawds"
DEFAULT_DATA_SET_WITH_MEMBER = "{0}(mem1)".format(DEFAULT_DATA_SET)
DEFAULT_DD = "MYDD"
SYSIN_DD = "SYSIN"
SYSPRINT_DD = "SYSPRINT"
IDCAMS_STDIN = " LISTCAT ENTRIES('{0}')".format(EXISTING_DATA_SET.upper())
IDCAMS_INVALID_STDIN = " hello world #$!@%!#$!@``~~^$*%"
DEFAULT_VOLUME = "000000"


# ---------------------------------------------------------------------------- #
#                               Data set DD tests                              #
# ---------------------------------------------------------------------------- #


def test_failing_name_format(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_raw(
        program_name="idcams",
        dds=[dict(dd_data_set=dict(dd_name=DEFAULT_DD, data_set_name="!!^&.BAD.NAME"))],
    )
    for result in results.contacted.values():
        pprint(result)
        assert "ValueError" in result.get("msg")


def test_disposition_new(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(name=DEFAULT_DATA_SET, state="absent")
    results = hosts.all.zos_raw(
        program_name="idcams",
        auth=True,
        dds=[
            dict(
                dd_data_set=dict(
                    dd_name=SYSPRINT_DD,
                    data_set_name=DEFAULT_DATA_SET,
                    disposition="new",
                    type="seq",
                    return_content=dict(type="text"),
                ),
            ),
            dict(dd_input=dict(dd_name=SYSIN_DD, content=IDCAMS_STDIN)),
        ],
    )
    for result in results.contacted.values():
        pprint(result)
        assert result.get("ret_code", {}).get("code", -1) == 0
        assert len(result.get("dd_names", [])) > 0
    results = hosts.all.zos_data_set(name=DEFAULT_DATA_SET, state="absent")
    for result in results.contacted.values():
        pprint(result)
        assert result.get("changed", False) is True


@pytest.mark.parametrize(
    "disposition", ["shr", "mod", "old"],
)
def test_dispositions_for_existing_data_set(ansible_zos_module, disposition):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(
        name=DEFAULT_DATA_SET, type="seq", state="present", replace=True
    )
    results = hosts.all.zos_raw(
        program_name="idcams",
        auth=True,
        dds=[
            dict(
                dd_data_set=dict(
                    dd_name=SYSPRINT_DD,
                    data_set_name=DEFAULT_DATA_SET,
                    disposition=disposition,
                    return_content=dict(type="text"),
                ),
            ),
            dict(dd_input=dict(dd_name=SYSIN_DD, content=IDCAMS_STDIN)),
        ],
    )
    for result in results.contacted.values():
        pprint(result)
        assert result.get("ret_code", {}).get("code", -1) == 0
        assert len(result.get("dd_names", [])) > 0
    results = hosts.all.zos_data_set(name=DEFAULT_DATA_SET, state="absent")
    for result in results.contacted.values():
        pprint(result)
        assert result.get("changed", False) is True


# * new data set and append to member in one step not currently supported
def test_new_disposition_for_data_set_members(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(name=DEFAULT_DATA_SET, state="absent")
    results = hosts.all.zos_raw(
        program_name="idcams",
        auth=True,
        dds=[
            dict(
                dd_data_set=dict(
                    dd_name=SYSPRINT_DD,
                    data_set_name=DEFAULT_DATA_SET_WITH_MEMBER,
                    disposition="new",
                    type="pds",
                    return_content=dict(type="text"),
                ),
            ),
            dict(dd_input=dict(dd_name=SYSIN_DD, content=IDCAMS_STDIN)),
        ],
    )
    for result in results.contacted.values():
        pprint(result)
        assert result.get("ret_code", {}).get("code", -1) == 8
    results = hosts.all.zos_data_set(name=DEFAULT_DATA_SET, state="absent")
    for result in results.contacted.values():
        pprint(result)
        assert result.get("changed", True) is False


@pytest.mark.parametrize(
    "disposition", ["shr", "mod", "old"],
)
def test_dispositions_for_existing_data_set_members(ansible_zos_module, disposition):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(
        name=DEFAULT_DATA_SET, type="pds", state="present", replace=True
    )
    results = hosts.all.zos_raw(
        program_name="idcams",
        auth=True,
        dds=[
            dict(
                dd_data_set=dict(
                    dd_name=SYSPRINT_DD,
                    data_set_name=DEFAULT_DATA_SET_WITH_MEMBER,
                    disposition=disposition,
                    return_content=dict(type="text"),
                ),
            ),
            dict(dd_input=dict(dd_name=SYSIN_DD, content=IDCAMS_STDIN)),
        ],
    )
    for result in results.contacted.values():
        pprint(result)
        assert result.get("ret_code", {}).get("code", -1) == 0
        assert len(result.get("dd_names", [])) > 0
    results = hosts.all.zos_data_set(name=DEFAULT_DATA_SET, state="absent")
    for result in results.contacted.values():
        pprint(result)
        assert result.get("changed", False) is True


@pytest.mark.parametrize(
    "normal_disposition,changed",
    [("keep", True), ("delete", True), ("catalog", True), ("uncatalog", True)],
)
def test_normal_dispositions_data_set(ansible_zos_module, normal_disposition, changed):
    hosts = ansible_zos_module
    results = hosts.all.zos_data_set(
        name=DEFAULT_DATA_SET,
        type="seq",
        state="present",
        replace=True,
        volumes=[DEFAULT_VOLUME],
    )
    results = hosts.all.zos_raw(
        program_name="idcams",
        auth=True,
        dds=[
            dict(
                dd_data_set=dict(
                    dd_name=SYSPRINT_DD,
                    data_set_name=DEFAULT_DATA_SET,
                    disposition="shr",
                    disposition_normal=normal_disposition,
                    volumes=[DEFAULT_VOLUME],
                    return_content=dict(type="text"),
                ),
            ),
            dict(dd_input=dict(dd_name=SYSIN_DD, content=IDCAMS_STDIN)),
        ],
    )
    for result in results.contacted.values():
        pprint(result)
        assert result.get("ret_code", {}).get("code", -1) == 0
        assert len(result.get("dd_names", [])) > 0
    results = hosts.all.zos_data_set(
        name=DEFAULT_DATA_SET, state="absent", volumes=[DEFAULT_VOLUME]
    )
    for result in results.contacted.values():
        pprint(result)
        assert result.get("changed", not changed) is changed


@pytest.mark.parametrize(
    "abnormal_disposition,changed",
    [("keep", True), ("delete", False), ("catalog", True)],
)
def test_abnormal_dispositions_data_set(
    ansible_zos_module, abnormal_disposition, changed
):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(
        name=DEFAULT_DATA_SET, type="seq", state="present", replace=True
    )
    results = hosts.all.zos_raw(
        program_name="IGYCRCTL",
        auth=True,
        dds=[
            dict(
                dd_data_set=dict(
                    dd_name=SYSPRINT_DD,
                    data_set_name=DEFAULT_DATA_SET,
                    disposition="shr",
                    disposition_abnormal=abnormal_disposition,
                    return_content=dict(type="text"),
                ),
            ),
            dict(dd_input=dict(dd_name=SYSIN_DD, content=IDCAMS_INVALID_STDIN)),
        ],
    )
    # for result in results.contacted.values():
    #     pprint(result)
    #     assert result.get("ret_code", {}).get("code", 0) != 0
    #     assert len(result.get("dd_names", [])) > 0
    results = hosts.all.zos_data_set(name=DEFAULT_DATA_SET, state="absent")
    for result in results.contacted.values():
        pprint(result)
        assert result.get("changed", not changed) is changed


@pytest.mark.parametrize(
    "space_type,primary,secondary,expected",
    [
        ("trk", 3, 1, 169992),
        ("cyl", 3, 1, 2549880),
        ("b", 3, 1, 56664),
        ("k", 3, 1, 56664),
        ("m", 3, 1, 2889864),
    ],
)
def test_space_types(ansible_zos_module, space_type, primary, secondary, expected):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(name=DEFAULT_DATA_SET, state="absent")
    results = hosts.all.zos_raw(
        program_name="idcams",
        auth=True,
        dds=[
            dict(
                dd_data_set=dict(
                    dd_name=SYSPRINT_DD,
                    data_set_name=DEFAULT_DATA_SET,
                    disposition="new",
                    type="seq",
                    space_primary=primary,
                    space_secondary=secondary,
                    space_type=space_type,
                    volumes=[DEFAULT_VOLUME],
                    return_content=dict(type="text"),
                ),
            ),
            dict(dd_input=dict(dd_name=SYSIN_DD, content=IDCAMS_STDIN)),
        ],
    )
    for result in results.contacted.values():
        pprint(result)
        assert result.get("ret_code", {}).get("code", -1) == 0
        assert len(result.get("dd_names", [])) > 0
    results = hosts.all.command(cmd="dls -l -s {0}".format(DEFAULT_DATA_SET))
    for result in results.contacted.values():
        pprint(result)
        assert str(expected) in result.get("stdout", "")

    results = hosts.all.zos_data_set(name=DEFAULT_DATA_SET, state="absent")
    for result in results.contacted.values():
        pprint(result)
        assert result.get("changed", False) is True


@pytest.mark.parametrize(
    "data_set_type", ["pds", "pdse", "large", "basic", "seq"],
)
def test_data_set_types_non_vsam(ansible_zos_module, data_set_type):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(name=DEFAULT_DATA_SET, state="absent")
    results = hosts.all.zos_raw(
        program_name="idcams",
        auth=True,
        dds=[
            dict(
                dd_data_set=dict(
                    dd_name=SYSPRINT_DD,
                    data_set_name=DEFAULT_DATA_SET,
                    disposition="new",
                    type=data_set_type,
                    volumes=[DEFAULT_VOLUME],
                ),
            ),
            dict(dd_input=dict(dd_name=SYSIN_DD, content=IDCAMS_STDIN)),
        ],
    )
    for result in results.contacted.values():
        pprint(result)
        assert (
            result.get("ret_code", {}).get("code", -1) != 8
            and result.get("ret_code", {}).get("code", -1) != -1
        )
    results = hosts.all.command(cmd="dls {0}".format(DEFAULT_DATA_SET))
    for result in results.contacted.values():
        pprint(result)
        assert "BGYSC1103E" not in result.get("stderr", "")

    results = hosts.all.zos_data_set(name=DEFAULT_DATA_SET, state="absent")
    for result in results.contacted.values():
        pprint(result)
        assert result.get("changed", False) is True


@pytest.mark.parametrize(
    "data_set_type", ["ksds", "rrds", "lds", "esds"],
)
def test_data_set_types_vsam(ansible_zos_module, data_set_type):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(name=DEFAULT_DATA_SET, state="absent")
    results = hosts.all.zos_raw(
        program_name="idcams",
        auth=True,
        dds=[
            # * ksds requires additional parameters
            dict(
                dd_data_set=dict(
                    dd_name=SYSPRINT_DD,
                    data_set_name=DEFAULT_DATA_SET,
                    disposition="new",
                    type=data_set_type,
                    volumes=["000000"],
                ),
            )
            if data_set_type != "ksds"
            else dict(
                dd_data_set=dict(
                    dd_name=SYSPRINT_DD,
                    data_set_name=DEFAULT_DATA_SET,
                    disposition="new",
                    type=data_set_type,
                    key_length=5,
                    key_offset=0,
                    volumes=["000000"],
                ),
            ),
            dict(dd_input=dict(dd_name=SYSIN_DD, content=IDCAMS_STDIN)),
        ],
    )
    for result in results.contacted.values():
        pprint(result)
        assert (
            result.get("ret_code", {}).get("code", -1) != 8
            and result.get("ret_code", {}).get("code", -1) != -1
        )
    # * we hope to see EDC5041I An error was detected at the system level when opening a file.
    # * because that means data set exists and is VSAM so we can't read it
    results = hosts.all.command(cmd="head \"//'{0}'\"".format(DEFAULT_DATA_SET))
    for result in results.contacted.values():
        pprint(result)
        assert "EDC5041I" in result.get("stderr", "")

    results = hosts.all.zos_data_set(name=DEFAULT_DATA_SET, state="absent")
    for result in results.contacted.values():
        pprint(result)
        assert result.get("changed", False) is True


@pytest.mark.parametrize(
    "record_format", ["u", "vb", "vba", "fb", "fba"],
)
def test_record_formats(ansible_zos_module, record_format):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(name=DEFAULT_DATA_SET, state="absent")
    results = hosts.all.zos_raw(
        program_name="idcams",
        auth=True,
        dds=[
            dict(
                dd_data_set=dict(
                    dd_name=SYSPRINT_DD,
                    data_set_name=DEFAULT_DATA_SET,
                    disposition="new",
                    record_format=record_format,
                    volumes=[DEFAULT_VOLUME],
                ),
            ),
            dict(dd_input=dict(dd_name=SYSIN_DD, content=IDCAMS_STDIN)),
        ],
    )
    for result in results.contacted.values():
        pprint(result)
        assert result.get("ret_code", {}).get("code", -1) != 8
        assert result.get("ret_code", {}).get("code", -1) != -1

    results = hosts.all.command(cmd="dls -l {0}".format(DEFAULT_DATA_SET))
    for result in results.contacted.values():
        pprint(result)
        assert str(" {0} ".format(record_format.upper())) in result.get("stdout", "")

    results = hosts.all.zos_data_set(name=DEFAULT_DATA_SET, state="absent")
    for result in results.contacted.values():
        pprint(result)
        assert result.get("changed", False) is True


@pytest.mark.parametrize(
    "return_content_type,expected",
    [
        ("text", "IDCAMS  SYSTEM"),
        (
            "base64",
            "\udcc9\udcc4\udcc3\udcc1\udcd4\udce2@@\udce2\udce8\udce2\udce3\udcc5",
        ),
    ],
)
def test_return_content_type(ansible_zos_module, return_content_type, expected):
    hosts = ansible_zos_module
    results = hosts.all.zos_data_set(
        name=DEFAULT_DATA_SET,
        type="seq",
        state="present",
        replace=True,
        volumes=[DEFAULT_VOLUME],
    )
    results = hosts.all.zos_raw(
        program_name="idcams",
        auth=True,
        dds=[
            dict(
                dd_data_set=dict(
                    dd_name=SYSPRINT_DD,
                    data_set_name=DEFAULT_DATA_SET,
                    disposition="shr",
                    volumes=[DEFAULT_VOLUME],
                    return_content=dict(type=return_content_type),
                ),
            ),
            dict(dd_input=dict(dd_name=SYSIN_DD, content=IDCAMS_STDIN)),
        ],
    )
    hosts.all.zos_data_set(
        name=DEFAULT_DATA_SET, state="absent", volumes=[DEFAULT_VOLUME]
    )
    for result in results.contacted.values():
        pprint(result)
        assert result.get("ret_code", {}).get("code", -1) == 0
        assert len(result.get("dd_names", [])) > 0
        assert expected in "\n".join(result.get("dd_names")[0].get("content", []))


@pytest.mark.parametrize(
    "src_encoding,response_encoding,expected",
    [
        ("iso8859-1", "ibm-1047", "qcfe\udcebB||BTBFg\udceb|Bg\udcfdGqfgB"),
        ("ibm-1047", "iso8859-1", "IDCAMS  SYSTEM",),
    ],
)
def test_return_text_content_encodings(
    ansible_zos_module, src_encoding, response_encoding, expected
):
    hosts = ansible_zos_module
    results = hosts.all.zos_data_set(
        name=DEFAULT_DATA_SET,
        type="seq",
        state="present",
        replace=True,
        volumes=[DEFAULT_VOLUME],
    )
    results = hosts.all.zos_raw(
        program_name="idcams",
        auth=True,
        dds=[
            dict(
                dd_data_set=dict(
                    dd_name=SYSPRINT_DD,
                    data_set_name=DEFAULT_DATA_SET,
                    disposition="shr",
                    volumes=[DEFAULT_VOLUME],
                    return_content=dict(
                        type="text",
                        src_encoding=src_encoding,
                        response_encoding=response_encoding,
                    ),
                ),
            ),
            dict(dd_input=dict(dd_name=SYSIN_DD, content=IDCAMS_STDIN)),
        ],
    )
    hosts.all.zos_data_set(
        name=DEFAULT_DATA_SET, state="absent", volumes=[DEFAULT_VOLUME]
    )
    for result in results.contacted.values():
        pprint(result)
        assert result.get("ret_code", {}).get("code", -1) == 0
        assert len(result.get("dd_names", [])) > 0
        assert expected in "\n".join(result.get("dd_names")[0].get("content", []))


def test_reuse_existing_data_set(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(
        name=DEFAULT_DATA_SET, type="seq", state="present", replace=True
    )
    results = hosts.all.zos_raw(
        program_name="IDCAMS",
        auth=True,
        dds=[
            dict(
                dd_data_set=dict(
                    dd_name=SYSPRINT_DD,
                    data_set_name=DEFAULT_DATA_SET,
                    disposition="new",
                    type="seq",
                    reuse=True,
                    return_content=dict(type="text"),
                ),
            ),
            dict(dd_input=dict(dd_name=SYSIN_DD, content=IDCAMS_STDIN)),
        ],
    )
    for result in results.contacted.values():
        pprint(result)
        assert result.get("ret_code", {}).get("code", 0) == 0
        assert len(result.get("dd_names", [])) > 0
    results = hosts.all.zos_data_set(name=DEFAULT_DATA_SET, state="absent")
    for result in results.contacted.values():
        pprint(result)
        assert result.get("changed", False) is True


def test_replace_existing_data_set(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(
        name=DEFAULT_DATA_SET, type="seq", state="present", replace=True
    )
    results = hosts.all.zos_raw(
        program_name="IDCAMS",
        auth=True,
        dds=[
            dict(
                dd_data_set=dict(
                    dd_name=SYSPRINT_DD,
                    data_set_name=DEFAULT_DATA_SET,
                    disposition="new",
                    type="seq",
                    replace=True,
                    return_content=dict(type="text"),
                ),
            ),
            dict(dd_input=dict(dd_name=SYSIN_DD, content=IDCAMS_STDIN)),
        ],
    )
    for result in results.contacted.values():
        pprint(result)
        assert result.get("ret_code", {}).get("code", 0) == 0
        assert len(result.get("dd_names", [])) > 0
    results = hosts.all.zos_data_set(name=DEFAULT_DATA_SET, state="absent")
    for result in results.contacted.values():
        pprint(result)
        assert result.get("changed", False) is True


def test_replace_existing_data_set_make_backup(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(name=DEFAULT_DATA_SET, state="absent")
    hosts.all.zos_raw(
        program_name="IDCAMS",
        auth=True,
        dds=[
            dict(
                dd_data_set=dict(
                    dd_name=SYSPRINT_DD,
                    data_set_name=DEFAULT_DATA_SET,
                    disposition="new",
                    type="seq",
                    replace=True,
                    return_content=dict(type="text"),
                ),
            ),
            dict(dd_input=dict(dd_name=SYSIN_DD, content=IDCAMS_STDIN)),
        ],
    )
    results = hosts.all.zos_raw(
        program_name="IDCAMS",
        auth=True,
        dds=[
            dict(
                dd_data_set=dict(
                    dd_name=SYSPRINT_DD,
                    data_set_name=DEFAULT_DATA_SET,
                    disposition="new",
                    type="seq",
                    replace=True,
                    backup=True,
                    return_content=dict(type="text"),
                ),
            ),
            dict(dd_input=dict(dd_name=SYSIN_DD, content=IDCAMS_STDIN)),
        ],
    )
    for result in results.contacted.values():
        pprint(result)
        assert result.get("ret_code", {}).get("code", 0) == 0
        assert len(result.get("dd_names", [])) > 0
        assert len(result.get("backups", [])) > 0
        assert result.get("backups")[0].get("backup_name") is not None
        results2 = hosts.all.command(
            cmd="head \"//'{0}'\"".format(result.get("backups")[0].get("backup_name"))
        )
        hosts.all.zos_data_set(
            name=result.get("backups")[0].get("backup_name"), state="absent"
        )
        assert (
            result.get("backups")[0].get("original_name").lower()
            == DEFAULT_DATA_SET.lower()
        )
    for result in results2.contacted.values():
        pprint(result)
        assert "IDCAMS" in result.get("stdout", "")
    results = hosts.all.zos_data_set(name=DEFAULT_DATA_SET, state="absent")
    for result in results.contacted.values():
        pprint(result)
        assert result.get("changed", False) is True


# ---------------------------------------------------------------------------- #
#                                 Input DD Tests                                #
# ---------------------------------------------------------------------------- #


def test_input_empty(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(name=DEFAULT_DATA_SET, state="absent")
    results = hosts.all.zos_raw(
        program_name="idcams",
        auth=True,
        dds=[
            dict(
                dd_data_set=dict(
                    dd_name=SYSPRINT_DD,
                    data_set_name=DEFAULT_DATA_SET,
                    disposition="new",
                    type="seq",
                    return_content=dict(type="text"),
                ),
            ),
            dict(dd_input=dict(dd_name=SYSIN_DD, content="")),
        ],
    )
    for result in results.contacted.values():
        pprint(result)
        assert result.get("ret_code", {}).get("code", -1) == 0
        assert len(result.get("dd_names", [])) > 0
    results = hosts.all.zos_data_set(name=DEFAULT_DATA_SET, state="absent")
    for result in results.contacted.values():
        pprint(result)
        assert result.get("changed", False) is True


def test_input_large(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(name=DEFAULT_DATA_SET, state="absent")
    contents = ""
    for i in range(50000):
        contents += "this is line {0}\n".format(i)
    results = hosts.all.zos_raw(
        program_name="idcams",
        auth=True,
        dds=[
            dict(
                dd_data_set=dict(
                    dd_name=SYSPRINT_DD,
                    data_set_name=DEFAULT_DATA_SET,
                    disposition="new",
                    type="seq",
                    return_content=dict(type="text"),
                ),
            ),
            dict(dd_input=dict(dd_name=SYSIN_DD, content=contents)),
        ],
    )
    for result in results.contacted.values():
        # pprint(result)
        assert result.get("ret_code", {}).get("code", -1) == 12
        assert len(result.get("dd_names", [])) > 0
        assert len(result.get("dd_names", [{}])[0].get("content")) > 100000
    results = hosts.all.zos_data_set(name=DEFAULT_DATA_SET, state="absent")
    for result in results.contacted.values():
        pprint(result)
        assert result.get("changed", False) is True


def test_input_provided_as_list(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(name=DEFAULT_DATA_SET, state="absent")
    contents = []
    for i in range(10):
        contents.append(IDCAMS_STDIN)
    results = hosts.all.zos_raw(
        program_name="idcams",
        auth=True,
        dds=[
            dict(
                dd_data_set=dict(
                    dd_name=SYSPRINT_DD,
                    data_set_name=DEFAULT_DATA_SET,
                    disposition="new",
                    type="seq",
                    return_content=dict(type="text"),
                ),
            ),
            dict(dd_input=dict(dd_name=SYSIN_DD, content=contents)),
        ],
    )
    for result in results.contacted.values():
        # pprint(result)
        assert result.get("ret_code", {}).get("code", -1) == 0
        assert len(result.get("dd_names", [])) > 0
        assert len(result.get("dd_names", [{}])[0].get("content")) > 100
    results = hosts.all.zos_data_set(name=DEFAULT_DATA_SET, state="absent")
    for result in results.contacted.values():
        pprint(result)
        assert result.get("changed", False) is True


@pytest.mark.parametrize(
    "return_content_type,expected",
    [
        ("text", "LISTCAT ENTRIES"),
        (
            "base64",
            "@\udcd3\udcc9\udce2\udce3\udcc3\udcc1\udce3@\udcc5\udcd5\udce3\udcd9\udcc9\udcc5",
        ),
    ],
)
def test_input_return_content_types(ansible_zos_module, return_content_type, expected):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(name=DEFAULT_DATA_SET, state="absent")
    results = hosts.all.zos_raw(
        program_name="idcams",
        auth=True,
        dds=[
            dict(
                dd_data_set=dict(
                    dd_name=SYSPRINT_DD,
                    data_set_name=DEFAULT_DATA_SET,
                    disposition="new",
                    type="seq",
                ),
            ),
            dict(
                dd_input=dict(
                    dd_name=SYSIN_DD,
                    content=IDCAMS_STDIN,
                    return_content=dict(type=return_content_type),
                )
            ),
        ],
    )
    for result in results.contacted.values():
        pprint(result)
        assert result.get("ret_code", {}).get("code", -1) == 0
        assert len(result.get("dd_names", [])) > 0
        assert expected in "\n".join(result.get("dd_names", [{}])[0].get("content"))
    results = hosts.all.zos_data_set(name=DEFAULT_DATA_SET, state="absent")
    for result in results.contacted.values():
        pprint(result)
        assert result.get("changed", False) is True


@pytest.mark.parametrize(
    "src_encoding,response_encoding,expected",
    [
        (
            "iso8859-1",
            "ibm-1047",
            "|\udceeqBFfeF|g\udcefF\udcfdqgB\udcd4\udcd0CBg\udcfdҿ\udcfdqGeFgҿ\udcfd",
        ),
        ("ibm-1047", "iso8859-1", "LISTCAT ENTRIES",),
    ],
)
def test_input_return_text_content_encodings(
    ansible_zos_module, src_encoding, response_encoding, expected
):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(name=DEFAULT_DATA_SET, state="absent")
    results = hosts.all.zos_raw(
        program_name="idcams",
        auth=True,
        dds=[
            dict(
                dd_data_set=dict(
                    dd_name=SYSPRINT_DD,
                    data_set_name=DEFAULT_DATA_SET,
                    disposition="new",
                    type="seq",
                ),
            ),
            dict(
                dd_input=dict(
                    dd_name=SYSIN_DD,
                    content=IDCAMS_STDIN,
                    return_content=dict(
                        type="text",
                        src_encoding=src_encoding,
                        response_encoding=response_encoding,
                    ),
                )
            ),
        ],
    )
    for result in results.contacted.values():
        pprint(result)
        assert result.get("ret_code", {}).get("code", -1) == 0
        assert len(result.get("dd_names", [])) > 0
        assert expected in "\n".join(result.get("dd_names", [{}])[0].get("content"))
    results = hosts.all.zos_data_set(name=DEFAULT_DATA_SET, state="absent")
    for result in results.contacted.values():
        pprint(result)
        assert result.get("changed", False) is True