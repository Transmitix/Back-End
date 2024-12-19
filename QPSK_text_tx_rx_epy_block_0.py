import numpy as np
from gnuradio import gr

class preamble_detector(gr.basic_block):
    def __init__(self):
        gr.basic_block.__init__(self,
            name="Preamble Detector",
            in_sig=[np.uint8],
            out_sig=[np.uint8])
        
        self.state = 'SEARCH'
        self.preamble_pattern = np.array([49, 48] * 8, dtype=np.uint8)
        self.end_pattern = np.array([49] * 8, dtype=np.uint8)
        self.buffer = np.array([], dtype=np.uint8)
        
    def general_work(self, input_items, output_items):
        in_stream = input_items[0]
        out_stream = output_items[0]
        
        if self.state == 'SEARCH':
            # Append new data to the buffer
            self.buffer = np.concatenate((self.buffer, in_stream))
            
            # Look for the preamble pattern in the buffer
            preamble_start = np.where(np.convolve(self.buffer, self.preamble_pattern, mode='valid') == len(self.preamble_pattern) * 49)[0]
            
            if len(preamble_start) > 0:
                # Preamble found, switch to DETECT state
                self.state = 'DETECT'
                self.buffer = self.buffer[preamble_start[0] + len(self.preamble_pattern):]
        
        if self.state == 'DETECT':
            # Look for the end pattern in the buffer
            end_pattern_start = np.where(np.convolve(self.buffer, self.end_pattern, mode='valid') == len(self.end_pattern) * 49)[0]
            
            if len(end_pattern_start) > 0:
                # End pattern found, output the data after the end pattern
                out_data = self.buffer[end_pattern_start[0] + len(self.end_pattern):]
                out_stream[:len(out_data)] = out_data
                self.consume(0, len(in_stream))
                return len(out_data)
        
        self.consume(0, len(in_stream))
        return 0
