import numpy as np

def isd(input_name, output_name, input_shape, output_shape, dtype):
    return {'input_name': input_name,
            'output_name': output_name,
            'input_shape': input_shape, 
            'output_shape': output_shape, 
            'dtype': dtype}

def models(batch):
    return {
        'small_lstm': isd('inputs', 'outputs', (batch, 8, 48), (batch, 2, 12), np.float32),
        'medium_cnn': isd('inputs', 'outputs', (batch, 101, 82, 9), (batch, 101, 82, 1), np.float32),
        'large_tcnn': isd('inputs', 'outputs', (batch, 3, 101, 82, 9), (batch, 3, 101, 82, 1), np.float32)
    }
