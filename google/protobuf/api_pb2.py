# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: google/protobuf/api.proto
"""Generated protocol buffer code."""
from Codeium.google.protobuf import descriptor as _descriptor
from Codeium.google.protobuf import descriptor_pool as _descriptor_pool
from Codeium.google.protobuf import symbol_database as _symbol_database
from Codeium.google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from Codeium.google.protobuf import source_context_pb2 as google_dot_protobuf_dot_source__context__pb2
from Codeium.google.protobuf import type_pb2 as google_dot_protobuf_dot_type__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x19google/protobuf/api.proto\x12\x0fgoogle.protobuf\x1a$google/protobuf/source_context.proto\x1a\x1agoogle/protobuf/type.proto\"\x81\x02\n\x03\x41pi\x12\x0c\n\x04name\x18\x01 \x01(\t\x12(\n\x07methods\x18\x02 \x03(\x0b\x32\x17.google.protobuf.Method\x12(\n\x07options\x18\x03 \x03(\x0b\x32\x17.google.protobuf.Option\x12\x0f\n\x07version\x18\x04 \x01(\t\x12\x36\n\x0esource_context\x18\x05 \x01(\x0b\x32\x1e.google.protobuf.SourceContext\x12&\n\x06mixins\x18\x06 \x03(\x0b\x32\x16.google.protobuf.Mixin\x12\'\n\x06syntax\x18\x07 \x01(\x0e\x32\x17.google.protobuf.Syntax\"\xd5\x01\n\x06Method\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x18\n\x10request_type_url\x18\x02 \x01(\t\x12\x19\n\x11request_streaming\x18\x03 \x01(\x08\x12\x19\n\x11response_type_url\x18\x04 \x01(\t\x12\x1a\n\x12response_streaming\x18\x05 \x01(\x08\x12(\n\x07options\x18\x06 \x03(\x0b\x32\x17.google.protobuf.Option\x12\'\n\x06syntax\x18\x07 \x01(\x0e\x32\x17.google.protobuf.Syntax\"#\n\x05Mixin\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0c\n\x04root\x18\x02 \x01(\tBv\n\x13\x63om.google.protobufB\x08\x41piProtoP\x01Z,google.golang.org/protobuf/types/known/apipb\xa2\x02\x03GPB\xaa\x02\x1eGoogle.Protobuf.WellKnownTypesb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'google.protobuf.api_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\023com.google.protobufB\010ApiProtoP\001Z,google.golang.org/protobuf/types/known/apipb\242\002\003GPB\252\002\036Google.Protobuf.WellKnownTypes'
  _globals['_API']._serialized_start=113
  _globals['_API']._serialized_end=370
  _globals['_METHOD']._serialized_start=373
  _globals['_METHOD']._serialized_end=586
  _globals['_MIXIN']._serialized_start=588
  _globals['_MIXIN']._serialized_end=623
# @@protoc_insertion_point(module_scope)
