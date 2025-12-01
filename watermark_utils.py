import numpy as np
import cv2

class WatermarkEmbedder:
    def __init__(self):
        self.block_size = 8
        self.Q = 35
        self.SYNC_CODE = "111000111000" # 12 bits

    def embed(self, image, watermark_text):
        """
        Embeds text into image using Redundant Block-based DCT with SYNC code.
        """
        img_yuv = cv2.cvtColor(image, cv2.COLOR_RGB2YCrCb)
        h, w, _ = img_yuv.shape
        y_channel = img_yuv[:, :, 0].astype(np.float32)

        # Prepare Packet: [SYNC][LEN][MSG]
        # LEN is 8 bits.
        binary_msg = ''.join(format(ord(char), '08b') for char in watermark_text)
        msg_len = len(binary_msg) // 8
        binary_len = format(msg_len, '08b')
        
        packet = self.SYNC_CODE + binary_len + binary_msg
        packet_len = len(packet)

        h_blocks = h // self.block_size
        w_blocks = w // self.block_size
        total_blocks = h_blocks * w_blocks
        
        if total_blocks < packet_len:
            return None, "Image too small to hold this watermark text."

        bit_idx = 0
        
        for r in range(h_blocks):
            for c in range(w_blocks):
                bit = int(packet[bit_idx % packet_len])
                
                r_start = r * self.block_size
                c_start = c * self.block_size
                block = y_channel[r_start:r_start+self.block_size, c_start:c_start+self.block_size]
                
                dct_block = cv2.dct(block)
                coeff = dct_block[3, 3]
                
                step = self.Q
                quantized = round(coeff / step)
                
                if bit == 0:
                    if quantized % 2 != 0:
                        quantized += 1 
                else: 
                    if quantized % 2 == 0:
                        quantized += 1
                
                new_coeff = quantized * step
                dct_block[3, 3] = new_coeff
                
                idct_block = cv2.idct(dct_block)
                y_channel[r_start:r_start+self.block_size, c_start:c_start+self.block_size] = idct_block
                
                bit_idx += 1

        img_yuv[:, :, 0] = np.clip(y_channel, 0, 255)
        img_rgb = cv2.cvtColor(img_yuv, cv2.COLOR_YCrCb2RGB)
        
        return img_rgb, None

class WatermarkDecoder:
    def __init__(self):
        self.block_size = 8
        self.Q = 35
        self.SYNC_CODE = "111000111000"

    def decode(self, image):
        img_yuv = cv2.cvtColor(image, cv2.COLOR_RGB2YCrCb)
        y_channel = img_yuv[:, :, 0].astype(np.float32)
        h, w = y_channel.shape
        
        # Group candidates by length
        candidates_by_len = {}
        
        # Grid Search
        for offset_y in range(self.block_size):
            for offset_x in range(self.block_size):
                
                extracted_bits = []
                h_blocks = (h - offset_y) // self.block_size
                w_blocks = (w - offset_x) // self.block_size
                
                if h_blocks == 0 or w_blocks == 0:
                    continue
                    
                for r in range(h_blocks):
                    for c in range(w_blocks):
                        r_start = offset_y + r * self.block_size
                        c_start = offset_x + c * self.block_size
                        
                        block = y_channel[r_start:r_start+self.block_size, c_start:c_start+self.block_size]
                        dct_block = cv2.dct(block)
                        coeff = dct_block[3, 3]
                        
                        step = self.Q
                        quantized = round(coeff / step)
                        
                        if quantized % 2 == 0:
                            extracted_bits.append('0')
                        else:
                            extracted_bits.append('1')
                
                if not extracted_bits:
                    continue
                    
                bit_stream = "".join(extracted_bits)
                
                # Find SYNC codes
                import re
                sync_indices = [m.start() for m in re.finditer(self.SYNC_CODE, bit_stream)]
                
                for idx in sync_indices:
                    # Read Length (next 8 bits)
                    len_start = idx + len(self.SYNC_CODE)
                    if len_start + 8 > len(bit_stream):
                        continue
                        
                    len_bits = bit_stream[len_start:len_start+8]
                    try:
                        msg_len = int(len_bits, 2)
                    except:
                        continue
                        
                    if msg_len <= 0 or msg_len > 50: # Sanity check
                        continue
                        
                    # Read Message Bits
                    msg_start = len_start + 8
                    msg_end = msg_start + (msg_len * 8)
                    
                    if msg_end > len(bit_stream):
                        continue
                        
                    msg_bits = bit_stream[msg_start:msg_end]
                    
                    if msg_len not in candidates_by_len:
                        candidates_by_len[msg_len] = []
                    candidates_by_len[msg_len].append(msg_bits)

        # Vote
        best_message = None
        max_votes = 0
        
        for length, bit_strings in candidates_by_len.items():
            # We need a reasonable number of votes to trust this length
            # But even 1 might be enough if it's the only one.
            
            # Bit-wise vote
            num_bits = length * 8
            consensus_bits = []
            
            for i in range(num_bits):
                ones = 0
                zeros = 0
                for s in bit_strings:
                    if i < len(s):
                        if s[i] == '1':
                            ones += 1
                        else:
                            zeros += 1
                
                if ones > zeros:
                    consensus_bits.append('1')
                else:
                    consensus_bits.append('0')
            
            consensus_str = "".join(consensus_bits)
            
            # Convert to text
            try:
                chars = []
                is_valid = True
                for k in range(0, len(consensus_str), 8):
                    byte = consensus_str[k:k+8]
                    char_code = int(byte, 2)
                    if 32 <= char_code <= 126:
                        chars.append(chr(char_code))
                    else:
                        is_valid = False
                        break
                
                if is_valid:
                    decoded_msg = "".join(chars)
                    # Heuristic: Prefer result supported by more packets
                    if len(bit_strings) > max_votes:
                        max_votes = len(bit_strings)
                        best_message = decoded_msg
            except:
                pass

        if best_message:
            return best_message, None
        else:
            return None, "No watermark detected."
