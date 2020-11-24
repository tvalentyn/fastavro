from fastavro import json_writer, json_reader
from fastavro.schema import parse_schema

from io import StringIO
import json


def roundtrip(schema, records):
    new_file = StringIO()
    json_writer(new_file, schema, records)
    new_file.seek(0)

    new_records = list(json_reader(new_file, schema))
    return new_records


def test_json():
    schema = {
        "type": "record",
        "name": "Test",
        "namespace": "test",
        "fields": [
            {
                "name": "null",
                "type": "null",
            },
            {
                "name": "boolean",
                "type": "boolean",
            },
            {
                "name": "string",
                "type": "string",
            },
            {
                "name": "bytes",
                "type": "bytes",
            },
            {
                "name": "int",
                "type": "int",
            },
            {
                "name": "long",
                "type": "long",
            },
            {
                "name": "float",
                "type": "float",
            },
            {
                "name": "double",
                "type": "double",
            },
            {
                "name": "fixed",
                "type": {
                    "type": "fixed",
                    "name": "fixed_field",
                    "size": 5,
                },
            },
            {
                "name": "union",
                "type": [
                    "null",
                    "int",
                    {
                        "type": "record",
                        "name": "union_record",
                        "fields": [
                            {
                                "name": "union_record_field",
                                "type": "string",
                            }
                        ],
                    },
                ],
            },
            {
                "name": "enum",
                "type": {
                    "type": "enum",
                    "name": "enum_field",
                    "symbols": ["FOO", "BAR"],
                },
            },
            {
                "name": "array",
                "type": {
                    "type": "array",
                    "items": "string",
                },
            },
            {
                "name": "map",
                "type": {
                    "type": "map",
                    "values": "int",
                },
            },
            {
                "name": "record",
                "type": {
                    "type": "record",
                    "name": "subrecord",
                    "fields": [
                        {
                            "name": "sub_int",
                            "type": "int",
                        }
                    ],
                },
            },
        ],
    }

    records = [
        {
            "null": None,
            "boolean": True,
            "string": "foo",
            "bytes": b"\xe2\x99\xa5",
            "int": 1,
            "long": 1 << 33,
            "float": 2.2,
            "double": 3.3,
            "fixed": b"\x61\x61\x61\x61\x61",
            "union": None,
            "enum": "BAR",
            "array": ["a", "b"],
            "map": {"c": 1, "d": 2},
            "record": {
                "sub_int": 123,
            },
        },
        {
            "null": None,
            "boolean": True,
            "string": "foo",
            "bytes": b"\xe2\x99\xa5",
            "int": 1,
            "long": 1 << 33,
            "float": 2.2,
            "double": 3.3,
            "fixed": b"\x61\x61\x61\x61\x61",
            "union": 321,
            "enum": "BAR",
            "array": ["a", "b"],
            "map": {"c": 1, "d": 2},
            "record": {
                "sub_int": 123,
            },
        },
        {
            "null": None,
            "boolean": True,
            "string": "foo",
            "bytes": b"\xe2\x99\xa5",
            "int": 1,
            "long": 1 << 33,
            "float": 2.2,
            "double": 3.3,
            "fixed": b"\x61\x61\x61\x61\x61",
            "union": {
                "union_record_field": "union_field",
            },
            "enum": "BAR",
            "array": ["a", "b"],
            "map": {"c": 1, "d": 2},
            "record": {
                "sub_int": 123,
            },
        },
    ]

    new_records = roundtrip(schema, records)
    assert records == new_records


def test_more_than_one_record():
    schema = {
        "type": "record",
        "name": "test_more_than_one_record",
        "namespace": "test",
        "fields": [
            {
                "name": "string",
                "type": "string",
            },
            {
                "name": "int",
                "type": "int",
            },
        ],
    }

    records = [
        {
            "string": "foo",
            "int": 1,
        },
        {
            "string": "bar",
            "int": 2,
        },
    ]

    new_records = roundtrip(schema, records)
    assert records == new_records


def test_encoded_union_output():
    schema = {
        "type": "record",
        "name": "Test",
        "namespace": "test",
        "fields": [
            {
                "name": "union",
                "type": [
                    "null",
                    "int",
                    {
                        "type": "record",
                        "name": "union_record",
                        "fields": [
                            {
                                "name": "union_record_field",
                                "type": "string",
                            }
                        ],
                    },
                ],
            }
        ],
    }

    # A null value is encoded as just null
    records = [{"union": None}]
    new_file = StringIO()
    json_writer(new_file, schema, records)
    assert new_file.getvalue().strip() == json.dumps({"union": None})

    # A non-null, non-named type is encoded as an object with a key for the
    # type
    records = [{"union": 321}]
    new_file = StringIO()
    json_writer(new_file, schema, records)
    assert new_file.getvalue().strip() == json.dumps({"union": {"int": 321}})

    # A non-null, named type is encoded as an object with a key for the name
    records = [{"union": {"union_record_field": "union_field"}}]
    new_file = StringIO()
    json_writer(new_file, schema, records)
    expected = json.dumps(
        {"union": {"test.union_record": {"union_record_field": "union_field"}}}
    )
    assert new_file.getvalue().strip() == expected


def test_union_string_and_bytes():
    schema = {
        "type": "record",
        "name": "Test",
        "namespace": "test",
        "fields": [
            {
                "name": "union",
                "type": [
                    "string",
                    "bytes",
                ],
            }
        ],
    }

    records = [
        {
            "union": "asdf",
        },
        {"union": b"asdf"},
    ]

    new_records = roundtrip(schema, records)
    assert records == new_records


def test_simple_type():
    schema = {"type": "string"}

    records = ["foo", "bar"]

    new_records = roundtrip(schema, records)
    assert records == new_records


def test_array_type_simple():
    schema = {"type": "array", "items": "string"}

    records = [
        ["foo", "bar"],
        ["a", "b"],
    ]

    new_records = roundtrip(schema, records)
    assert records == new_records


def test_array_type_records():
    schema = {
        "type": "array",
        "items": {
            "type": "record",
            "name": "test_array_type",
            "fields": [
                {
                    "name": "field1",
                    "type": "string",
                },
                {
                    "name": "field2",
                    "type": "int",
                },
            ],
        },
    }

    records = [
        [{"field1": "foo", "field2": 1}],
        [{"field1": "bar", "field2": 2}],
    ]

    new_records = roundtrip(schema, records)
    assert records == new_records


def test_empty_maps():
    """https://github.com/fastavro/fastavro/issues/380"""
    schema = {
        "type": "map",
        "values": "int",
    }

    records = [
        {"foo": 1},
        {},
    ]

    new_records = roundtrip(schema, records)
    assert records == new_records


def test_empty_arrays():
    """https://github.com/fastavro/fastavro/issues/380"""
    schema = {
        "type": "array",
        "items": "int",
    }

    records = [
        [1],
        [],
    ]

    new_records = roundtrip(schema, records)
    assert records == new_records


def test_union_in_array():
    """https://github.com/fastavro/fastavro/issues/399"""
    schema = {
        "type": "array",
        "items": [
            {
                "type": "record",
                "name": "rec1",
                "fields": [
                    {
                        "name": "field1",
                        "type": ["string", "null"],
                    }
                ],
            },
            {
                "type": "record",
                "name": "rec2",
                "fields": [
                    {
                        "name": "field2",
                        "type": ["string", "null"],
                    }
                ],
            },
            "null",
        ],
    }

    records = [
        [{"field1": "foo"}, {"field2": None}, None],
    ]

    new_records = roundtrip(schema, records)
    assert records == new_records


def test_union_in_array2():
    """https://github.com/fastavro/fastavro/issues/399"""
    schema = {
        "type": "record",
        "name": "Inbox",
        "fields": [
            {"type": "string", "name": "id"},
            {"type": "string", "name": "msg_title"},
            {
                "name": "msg_content",
                "type": {
                    "type": "array",
                    "items": [
                        {
                            "type": "record",
                            "name": "LimitedTime",
                            "fields": [
                                {
                                    "type": ["string", "null"],
                                    "name": "type",
                                    "default": "now",
                                }
                            ],
                        },
                        {
                            "type": "record",
                            "name": "Text",
                            "fields": [{"type": ["string", "null"], "name": "text"}],
                        },
                    ],
                },
            },
        ],
    }

    records = [
        {
            "id": 1234,
            "msg_title": "Hi",
            "msg_content": [{"type": "now"}, {"text": "hi from here!"}],
        },
    ]

    new_records = roundtrip(schema, records)
    assert records == new_records


def test_union_in_map():
    """https://github.com/fastavro/fastavro/issues/399"""
    schema = {
        "type": "record",
        "name": "Test",
        "namespace": "test",
        "fields": [
            {
                "name": "map",
                "type": {
                    "type": "map",
                    "values": ["string", "null"],
                },
            }
        ],
    }

    records = [{"map": {"c": "1", "d": None}}]

    new_records = roundtrip(schema, records)
    assert records == new_records


def test_with_dependent_schema():
    """Tests a schema with dependent schema
    https://github.com/fastavro/fastavro/issues/418"""
    dependency = {
        "type": "record",
        "name": "Dependency",
        "namespace": "test",
        "fields": [{"name": "_name", "type": "string"}],
    }

    schema = {
        "type": "record",
        "name": "Test",
        "namespace": "test",
        "fields": [
            {"name": "_name", "type": "string"},
            {"name": "_dependency", "type": "Dependency"},
        ],
    }

    records = [{"_name": "parent", "_dependency": {"_name": "child"}}]

    parsed_schema = parse_schema([dependency, schema])

    new_records = roundtrip(parsed_schema, records)
    assert records == new_records


def test_enum_named_type():
    """https://github.com/fastavro/fastavro/issues/450"""
    schema = {
        "type": "record",
        "name": "test_enum_named_type",
        "fields": [
            {
                "name": "test1",
                "type": {
                    "type": "enum",
                    "name": "my_enum",
                    "symbols": ["FOO", "BAR"],
                },
            },
            {
                "name": "test2",
                "type": "my_enum",
            },
        ],
    }

    records = [{"test1": "FOO", "test2": "BAR"}]
    parsed_schema = parse_schema(schema)
    assert records == roundtrip(parsed_schema, records)


def test_fixed_named_type():
    """https://github.com/fastavro/fastavro/issues/450"""
    schema = {
        "type": "record",
        "name": "test_fixed_named_type",
        "fields": [
            {
                "name": "test1",
                "type": {
                    "type": "fixed",
                    "name": "my_fixed",
                    "size": 4,
                },
            },
            {
                "name": "test2",
                "type": "my_fixed",
            },
        ],
    }

    records = [{"test1": b"1234", "test2": b"4321"}]
    parsed_schema = parse_schema(schema)
    assert records == roundtrip(parsed_schema, records)


def test_record_named_type():
    """https://github.com/fastavro/fastavro/issues/450"""
    schema = {
        "type": "record",
        "name": "test_record_named_type",
        "fields": [
            {
                "name": "test1",
                "type": {
                    "type": "record",
                    "name": "my_record",
                    "fields": [
                        {
                            "name": "field1",
                            "type": "string",
                        }
                    ],
                },
            },
            {
                "name": "test2",
                "type": "my_record",
            },
        ],
    }

    records = [{"test1": {"field1": "foo"}, "test2": {"field1": "bar"}}]
    parsed_schema = parse_schema(schema)
    assert records == roundtrip(parsed_schema, records)
