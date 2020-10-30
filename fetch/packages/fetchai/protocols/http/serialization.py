# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2020 fetchai
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------

"""Serialization module for http protocol."""

from typing import Any, Dict, cast

from aea.protocols.base import Message
from aea.protocols.base import Serializer

from packages.fetchai.protocols.http import http_pb2
from packages.fetchai.protocols.http.message import HttpMessage


class HttpSerializer(Serializer):
    """Serialization for the 'http' protocol."""

    @staticmethod
    def encode(msg: Message) -> bytes:
        """
        Encode a 'Http' message into bytes.

        :param msg: the message object.
        :return: the bytes.
        """
        msg = cast(HttpMessage, msg)
        http_msg = http_pb2.HttpMessage()
        http_msg.message_id = msg.message_id
        dialogue_reference = msg.dialogue_reference
        http_msg.dialogue_starter_reference = dialogue_reference[0]
        http_msg.dialogue_responder_reference = dialogue_reference[1]
        http_msg.target = msg.target

        performative_id = msg.performative
        if performative_id == HttpMessage.Performative.REQUEST:
            performative = http_pb2.HttpMessage.Request_Performative()  # type: ignore
            method = msg.method
            performative.method = method
            url = msg.url
            performative.url = url
            version = msg.version
            performative.version = version
            headers = msg.headers
            performative.headers = headers
            bodyy = msg.bodyy
            performative.bodyy = bodyy
            http_msg.request.CopyFrom(performative)
        elif performative_id == HttpMessage.Performative.RESPONSE:
            performative = http_pb2.HttpMessage.Response_Performative()  # type: ignore
            version = msg.version
            performative.version = version
            status_code = msg.status_code
            performative.status_code = status_code
            status_text = msg.status_text
            performative.status_text = status_text
            headers = msg.headers
            performative.headers = headers
            bodyy = msg.bodyy
            performative.bodyy = bodyy
            http_msg.response.CopyFrom(performative)
        else:
            raise ValueError("Performative not valid: {}".format(performative_id))

        http_bytes = http_msg.SerializeToString()
        return http_bytes

    @staticmethod
    def decode(obj: bytes) -> Message:
        """
        Decode bytes into a 'Http' message.

        :param obj: the bytes object.
        :return: the 'Http' message.
        """
        http_pb = http_pb2.HttpMessage()
        http_pb.ParseFromString(obj)
        message_id = http_pb.message_id
        dialogue_reference = (
            http_pb.dialogue_starter_reference,
            http_pb.dialogue_responder_reference,
        )
        target = http_pb.target

        performative = http_pb.WhichOneof("performative")
        performative_id = HttpMessage.Performative(str(performative))
        performative_content = dict()  # type: Dict[str, Any]
        if performative_id == HttpMessage.Performative.REQUEST:
            method = http_pb.request.method
            performative_content["method"] = method
            url = http_pb.request.url
            performative_content["url"] = url
            version = http_pb.request.version
            performative_content["version"] = version
            headers = http_pb.request.headers
            performative_content["headers"] = headers
            bodyy = http_pb.request.bodyy
            performative_content["bodyy"] = bodyy
        elif performative_id == HttpMessage.Performative.RESPONSE:
            version = http_pb.response.version
            performative_content["version"] = version
            status_code = http_pb.response.status_code
            performative_content["status_code"] = status_code
            status_text = http_pb.response.status_text
            performative_content["status_text"] = status_text
            headers = http_pb.response.headers
            performative_content["headers"] = headers
            bodyy = http_pb.response.bodyy
            performative_content["bodyy"] = bodyy
        else:
            raise ValueError("Performative not valid: {}.".format(performative_id))

        return HttpMessage(
            message_id=message_id,
            dialogue_reference=dialogue_reference,
            target=target,
            performative=performative,
            **performative_content
        )
