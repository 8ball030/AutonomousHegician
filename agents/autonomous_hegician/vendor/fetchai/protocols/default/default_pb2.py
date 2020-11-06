# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: default.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor.FileDescriptor(
    name="default.proto",
    package="aea.fetchai.default",
    syntax="proto3",
    serialized_options=None,
    serialized_pb=b'\n\rdefault.proto\x12\x13\x61\x65\x61.fetchai.default"\xb3\x05\n\x0e\x44\x65\x66\x61ultMessage\x12G\n\x05\x62ytes\x18\x05 \x01(\x0b\x32\x36.aea.fetchai.default.DefaultMessage.Bytes_PerformativeH\x00\x12G\n\x05\x65rror\x18\x06 \x01(\x0b\x32\x36.aea.fetchai.default.DefaultMessage.Error_PerformativeH\x00\x1a\xdd\x01\n\tErrorCode\x12O\n\nerror_code\x18\x01 \x01(\x0e\x32;.aea.fetchai.default.DefaultMessage.ErrorCode.ErrorCodeEnum"\x7f\n\rErrorCodeEnum\x12\x18\n\x14UNSUPPORTED_PROTOCOL\x10\x00\x12\x12\n\x0e\x44\x45\x43ODING_ERROR\x10\x01\x12\x13\n\x0fINVALID_MESSAGE\x10\x02\x12\x15\n\x11UNSUPPORTED_SKILL\x10\x03\x12\x14\n\x10INVALID_DIALOGUE\x10\x04\x1a%\n\x12\x42ytes_Performative\x12\x0f\n\x07\x63ontent\x18\x01 \x01(\x0c\x1a\xf7\x01\n\x12\x45rror_Performative\x12\x41\n\nerror_code\x18\x01 \x01(\x0b\x32-.aea.fetchai.default.DefaultMessage.ErrorCode\x12\x11\n\terror_msg\x18\x02 \x01(\t\x12Y\n\nerror_data\x18\x03 \x03(\x0b\x32\x45.aea.fetchai.default.DefaultMessage.Error_Performative.ErrorDataEntry\x1a\x30\n\x0e\x45rrorDataEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\x0c:\x02\x38\x01\x42\x0e\n\x0cperformativeb\x06proto3',
)


_DEFAULTMESSAGE_ERRORCODE_ERRORCODEENUM = _descriptor.EnumDescriptor(
    name="ErrorCodeEnum",
    full_name="aea.fetchai.default.DefaultMessage.ErrorCode.ErrorCodeEnum",
    filename=None,
    file=DESCRIPTOR,
    values=[
        _descriptor.EnumValueDescriptor(
            name="UNSUPPORTED_PROTOCOL",
            index=0,
            number=0,
            serialized_options=None,
            type=None,
        ),
        _descriptor.EnumValueDescriptor(
            name="DECODING_ERROR", index=1, number=1, serialized_options=None, type=None
        ),
        _descriptor.EnumValueDescriptor(
            name="INVALID_MESSAGE",
            index=2,
            number=2,
            serialized_options=None,
            type=None,
        ),
        _descriptor.EnumValueDescriptor(
            name="UNSUPPORTED_SKILL",
            index=3,
            number=3,
            serialized_options=None,
            type=None,
        ),
        _descriptor.EnumValueDescriptor(
            name="INVALID_DIALOGUE",
            index=4,
            number=4,
            serialized_options=None,
            type=None,
        ),
    ],
    containing_type=None,
    serialized_options=None,
    serialized_start=298,
    serialized_end=425,
)
_sym_db.RegisterEnumDescriptor(_DEFAULTMESSAGE_ERRORCODE_ERRORCODEENUM)


_DEFAULTMESSAGE_ERRORCODE = _descriptor.Descriptor(
    name="ErrorCode",
    full_name="aea.fetchai.default.DefaultMessage.ErrorCode",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(
            name="error_code",
            full_name="aea.fetchai.default.DefaultMessage.ErrorCode.error_code",
            index=0,
            number=1,
            type=14,
            cpp_type=8,
            label=1,
            has_default_value=False,
            default_value=0,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[_DEFAULTMESSAGE_ERRORCODE_ERRORCODEENUM,],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=204,
    serialized_end=425,
)

_DEFAULTMESSAGE_BYTES_PERFORMATIVE = _descriptor.Descriptor(
    name="Bytes_Performative",
    full_name="aea.fetchai.default.DefaultMessage.Bytes_Performative",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(
            name="content",
            full_name="aea.fetchai.default.DefaultMessage.Bytes_Performative.content",
            index=0,
            number=1,
            type=12,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=b"",
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=427,
    serialized_end=464,
)

_DEFAULTMESSAGE_ERROR_PERFORMATIVE_ERRORDATAENTRY = _descriptor.Descriptor(
    name="ErrorDataEntry",
    full_name="aea.fetchai.default.DefaultMessage.Error_Performative.ErrorDataEntry",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(
            name="key",
            full_name="aea.fetchai.default.DefaultMessage.Error_Performative.ErrorDataEntry.key",
            index=0,
            number=1,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=b"".decode("utf-8"),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
        _descriptor.FieldDescriptor(
            name="value",
            full_name="aea.fetchai.default.DefaultMessage.Error_Performative.ErrorDataEntry.value",
            index=1,
            number=2,
            type=12,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=b"",
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=b"8\001",
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=666,
    serialized_end=714,
)

_DEFAULTMESSAGE_ERROR_PERFORMATIVE = _descriptor.Descriptor(
    name="Error_Performative",
    full_name="aea.fetchai.default.DefaultMessage.Error_Performative",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(
            name="error_code",
            full_name="aea.fetchai.default.DefaultMessage.Error_Performative.error_code",
            index=0,
            number=1,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
        _descriptor.FieldDescriptor(
            name="error_msg",
            full_name="aea.fetchai.default.DefaultMessage.Error_Performative.error_msg",
            index=1,
            number=2,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=b"".decode("utf-8"),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
        _descriptor.FieldDescriptor(
            name="error_data",
            full_name="aea.fetchai.default.DefaultMessage.Error_Performative.error_data",
            index=2,
            number=3,
            type=11,
            cpp_type=10,
            label=3,
            has_default_value=False,
            default_value=[],
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
    ],
    extensions=[],
    nested_types=[_DEFAULTMESSAGE_ERROR_PERFORMATIVE_ERRORDATAENTRY,],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=467,
    serialized_end=714,
)

_DEFAULTMESSAGE = _descriptor.Descriptor(
    name="DefaultMessage",
    full_name="aea.fetchai.default.DefaultMessage",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(
            name="bytes",
            full_name="aea.fetchai.default.DefaultMessage.bytes",
            index=0,
            number=5,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
        _descriptor.FieldDescriptor(
            name="error",
            full_name="aea.fetchai.default.DefaultMessage.error",
            index=1,
            number=6,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
    ],
    extensions=[],
    nested_types=[
        _DEFAULTMESSAGE_ERRORCODE,
        _DEFAULTMESSAGE_BYTES_PERFORMATIVE,
        _DEFAULTMESSAGE_ERROR_PERFORMATIVE,
    ],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[
        _descriptor.OneofDescriptor(
            name="performative",
            full_name="aea.fetchai.default.DefaultMessage.performative",
            index=0,
            containing_type=None,
            fields=[],
        ),
    ],
    serialized_start=39,
    serialized_end=730,
)

_DEFAULTMESSAGE_ERRORCODE.fields_by_name[
    "error_code"
].enum_type = _DEFAULTMESSAGE_ERRORCODE_ERRORCODEENUM
_DEFAULTMESSAGE_ERRORCODE.containing_type = _DEFAULTMESSAGE
_DEFAULTMESSAGE_ERRORCODE_ERRORCODEENUM.containing_type = _DEFAULTMESSAGE_ERRORCODE
_DEFAULTMESSAGE_BYTES_PERFORMATIVE.containing_type = _DEFAULTMESSAGE
_DEFAULTMESSAGE_ERROR_PERFORMATIVE_ERRORDATAENTRY.containing_type = (
    _DEFAULTMESSAGE_ERROR_PERFORMATIVE
)
_DEFAULTMESSAGE_ERROR_PERFORMATIVE.fields_by_name[
    "error_code"
].message_type = _DEFAULTMESSAGE_ERRORCODE
_DEFAULTMESSAGE_ERROR_PERFORMATIVE.fields_by_name[
    "error_data"
].message_type = _DEFAULTMESSAGE_ERROR_PERFORMATIVE_ERRORDATAENTRY
_DEFAULTMESSAGE_ERROR_PERFORMATIVE.containing_type = _DEFAULTMESSAGE
_DEFAULTMESSAGE.fields_by_name[
    "bytes"
].message_type = _DEFAULTMESSAGE_BYTES_PERFORMATIVE
_DEFAULTMESSAGE.fields_by_name[
    "error"
].message_type = _DEFAULTMESSAGE_ERROR_PERFORMATIVE
_DEFAULTMESSAGE.oneofs_by_name["performative"].fields.append(
    _DEFAULTMESSAGE.fields_by_name["bytes"]
)
_DEFAULTMESSAGE.fields_by_name[
    "bytes"
].containing_oneof = _DEFAULTMESSAGE.oneofs_by_name["performative"]
_DEFAULTMESSAGE.oneofs_by_name["performative"].fields.append(
    _DEFAULTMESSAGE.fields_by_name["error"]
)
_DEFAULTMESSAGE.fields_by_name[
    "error"
].containing_oneof = _DEFAULTMESSAGE.oneofs_by_name["performative"]
DESCRIPTOR.message_types_by_name["DefaultMessage"] = _DEFAULTMESSAGE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

DefaultMessage = _reflection.GeneratedProtocolMessageType(
    "DefaultMessage",
    (_message.Message,),
    {
        "ErrorCode": _reflection.GeneratedProtocolMessageType(
            "ErrorCode",
            (_message.Message,),
            {
                "DESCRIPTOR": _DEFAULTMESSAGE_ERRORCODE,
                "__module__": "default_pb2"
                # @@protoc_insertion_point(class_scope:aea.fetchai.default.DefaultMessage.ErrorCode)
            },
        ),
        "Bytes_Performative": _reflection.GeneratedProtocolMessageType(
            "Bytes_Performative",
            (_message.Message,),
            {
                "DESCRIPTOR": _DEFAULTMESSAGE_BYTES_PERFORMATIVE,
                "__module__": "default_pb2"
                # @@protoc_insertion_point(class_scope:aea.fetchai.default.DefaultMessage.Bytes_Performative)
            },
        ),
        "Error_Performative": _reflection.GeneratedProtocolMessageType(
            "Error_Performative",
            (_message.Message,),
            {
                "ErrorDataEntry": _reflection.GeneratedProtocolMessageType(
                    "ErrorDataEntry",
                    (_message.Message,),
                    {
                        "DESCRIPTOR": _DEFAULTMESSAGE_ERROR_PERFORMATIVE_ERRORDATAENTRY,
                        "__module__": "default_pb2"
                        # @@protoc_insertion_point(class_scope:aea.fetchai.default.DefaultMessage.Error_Performative.ErrorDataEntry)
                    },
                ),
                "DESCRIPTOR": _DEFAULTMESSAGE_ERROR_PERFORMATIVE,
                "__module__": "default_pb2"
                # @@protoc_insertion_point(class_scope:aea.fetchai.default.DefaultMessage.Error_Performative)
            },
        ),
        "DESCRIPTOR": _DEFAULTMESSAGE,
        "__module__": "default_pb2"
        # @@protoc_insertion_point(class_scope:aea.fetchai.default.DefaultMessage)
    },
)
_sym_db.RegisterMessage(DefaultMessage)
_sym_db.RegisterMessage(DefaultMessage.ErrorCode)
_sym_db.RegisterMessage(DefaultMessage.Bytes_Performative)
_sym_db.RegisterMessage(DefaultMessage.Error_Performative)
_sym_db.RegisterMessage(DefaultMessage.Error_Performative.ErrorDataEntry)


_DEFAULTMESSAGE_ERROR_PERFORMATIVE_ERRORDATAENTRY._options = None
# @@protoc_insertion_point(module_scope)