import grpc
import json
import numpy as np
import os
import requests
import tensorflow as tf

from smartredis import Client

from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc
from tensorflow.keras.models import load_model

from models import models


class SMI:

    def __init__(self, model, hostport=None):
        self.hostport = hostport
        self.model = model

    def grpc(self, batch):
        channel = grpc.insecure_channel(self.hostport,
                  options=[('grpc.max_receive_message_length', 2147483647)])
        stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)
        def inference(data):
            request = predict_pb2.PredictRequest()
            request.model_spec.name = self.model
            request.model_spec.signature_name = 'serving_default'
            mods = models(batch)
            data = np.array(data, dtype=mods[self.model]['dtype'])
            request.inputs[mods[self.model]['input_name']].\
                CopyFrom(tf.make_tensor_proto(data, shape=mods[self.model]['input_shape']))
            response = stub.Predict(request)
            return response
        return inference

    def resp_inference(self):
        client = Client(address=self.hostport)
        def inference(data):
            client.put_tensor("input", data)
            client.run_model("model", "input", "output")
            return client.get_tensor("output")
        return inference

    def http(self):
        method_name = ":predict"
        headers = {"content-type": "application/json"}
        url = "http://" + self.hostport + "/v1/models/" + self.model
        def inference(data):
            payload = json.dumps({"instances": data.tolist()})
            response = requests.post(url + method_name, data=payload, headers=headers)
            return response
        return inference

    def embedded(self, model_base_path):
        model = load_model(os.path.join(model_base_path, self.model, "1"), compile=False)
        return lambda data : model(data)
