import numpy as np


class TFLitePilot:
    def __init__(self, model=None, *args, **kwargs):
        import tensorflow as tf

        if tf.__version__.startswith('1.12'):
            self.Interpreter = tf.lite.Interpreter
        elif tf.__version__.startswith('1.11'):
            self.Interpreter = tf.contrib.lite.Interpreter
        else: 
            raise ValueError('unsupported version of tensorflow lite {}, must be >= 1.1'.format(tf.__version__))

        self.tf = tf

        # Load TFLite model and allocate tensors.
        self.interpreter = None

        # Get input and output tensors.
        self.input_details = None
        self.output_details = None

    def load(self, model_path):
        # Load TFLite model and allocate tensors.
        print()
        self.interpreter = self.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()

        # Get input and output tensors.
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()


class TFLiteCategorical(TFLitePilot):
    def run(self, img_arr):
        image = np.array([img_arr], dtype=np.float32)
        self.interpreter.set_tensor(self.input_details[0]['index'], image)

        self.interpreter.invoke()
        angle_binned = self.interpreter.get_tensor(self.output_details[0]['index'])
        throttle = self.interpreter.get_tensor(self.output_details[1]['index'])
        #in order to support older models with linear throttle,
        #we will test for shape of throttle to see if it's the newer
        #binned version.
        N = len(throttle[0])
        throttle = dk.utils.linear_unbin(throttle, N=N, offset=0.0, R=0.5)
        angle_unbinned = dk.utils.linear_unbin(angle_binned)
        return angle_unbinned, throttle


class TFLiteLinear(TFLitePilot):
    def run(self, img_arr):
        image = np.array([img_arr], dtype=np.float32)
        self.interpreter.set_tensor(self.input_details[0]['index'], image)

        self.interpreter.invoke()
        angle = self.interpreter.get_tensor(self.output_details[0]['index'])
        throttle = self.interpreter.get_tensor(self.output_details[1]['index'])
        #in order to support older models with linear throttle,
        #we will test for shape of throttle to see if it's the newer
        #binned version.
        return angle[0][0], throttle[0][0]