import numpy as np
from gnuradio import gr

class prepend_preamble(gr.sync_block):
    def __init__(self, preamble=[85, 85, 85, 85, 85, 127, 255]):
        gr.sync_block.__init__(self, name="prepend_preamble", in_sig=[np.uint8], out_sig=[np.uint8])
        self.preamble = np.array(preamble, dtype=np.uint8)  # Store the preamble
        self.preamble_sent = False  # Track if preamble has been fully sent
        self.preamble_index = 0  # Track progress in preamble

    def work(self, input_items, output_items):
        out = output_items[0]
        in0 = input_items[0]
        out_index = 0  # Track the current position in the output buffer

        # If preamble has not been fully sent, send the preamble
        if not self.preamble_sent:
            preamble_remaining = self.preamble[self.preamble_index:]  # Remaining preamble
            to_copy = min(len(preamble_remaining), len(out) - out_index)  # Fit as much as possible
            out[out_index:out_index + to_copy] = preamble_remaining[:to_copy]
            self.preamble_index += to_copy
            out_index += to_copy

            # Check if the preamble is fully sent
            if self.preamble_index >= len(self.preamble):
                self.preamble_sent = True

        # After preamble, forward the input data
        remaining_space = len(out) - out_index
        to_copy = min(len(in0), remaining_space)
        out[out_index:out_index + to_copy] = in0[:to_copy]
        return out_index + to_copy

            
        


