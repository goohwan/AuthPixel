import numpy as np
import cv2

class WatermarkEmbedder:
    def __init__(self):
        self.block_size = 8
        self.Q = 40  # Higher for stronger embedding
        self.SYNC_CODE = "10101010"  # 8 bits alternating pattern

    def embed(self, image, watermark_text):
        """
        Embeds text using Block DCT with simple repetition.
        """
        img_yuv = cv2.cvtColor(image, cv2.COLOR_RGB2YCrCb)
        h, w, _ = img_yuv.shape
        y_channel = img_yuv[:, :, 0].astype(np.float32)

        # Prepare Packet: [SYNC][MSG]
        binary_msg = ''.join(format(ord(char), '08b') for char in watermark_text)
        # Add terminator
        binary_msg += '00000000'
        
        packet = self.SYNC_CODE + binary_msg
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
        self.Q = 40
        self.SYNC_CODE = "10101010"

    def decode(self, image):
        img_yuv = cv2.cvtColor(image, cv2.COLOR_RGB2YCrCb)
        y_channel = img_yuv[:, :, 0].astype(np.float32)
        h, w = y_channel.shape
        
        # Grid Search
        all_extractions = []
        
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
                
                if len(extracted_bits) > 0:
                    all_extractions.append("".join(extracted_bits))
        
        # Try to decode from all extractions
        candidates = []
        
        for bit_stream in all_extractions:
            # Find SYNC
            import re
            sync_matches = [m.start() for m in re.finditer(self.SYNC_CODE, bit_stream)]
            
            for sync_pos in sync_matches:
                msg_start = sync_pos + len(self.SYNC_CODE)
                
                # Read until we hit terminator or run out
                for end in range(msg_start + 8, min(len(bit_stream), msg_start + 200), 8):
                    chunk = bit_stream[msg_start:end]
                    
                    # Check for terminator
                    if chunk.endswith('00000000'):
                        msg_bits = chunk[:-8]
                        
                        # Convert to text
                        try:
                            chars = []
                            for k in range(0, len(msg_bits), 8):
                                byte = msg_bits[k:k+8]
                                char_code = int(byte, 2)
                                if 32 <= char_code <= 126:
                                    chars.append(chr(char_code))
                                else:
                                    break
                            
                            if len(chars) > 0:
                                candidates.append("".join(chars))
                                break
                        except:
                            pass

        if candidates:
            # Return most common
            from collections import Counter
            most_common = Counter(candidates).most_common(1)
            return most_common[0][0], None
        else:
            return None, "No watermark detected."
