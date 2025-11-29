import numpy as np
import cv2
import pywt

class WatermarkEmbedder:
    def __init__(self):
        self.block_shape = (4, 4)

    def embed(self, image, watermark_text):
        # Convert to YCrCb and use Y channel
        img_yuv = cv2.cvtColor(image, cv2.COLOR_RGB2YCrCb)
        h, w, _ = img_yuv.shape
        
        # Resize to be even for DWT
        h_new = h if h % 2 == 0 else h - 1
        w_new = w if w % 2 == 0 else w - 1
        img_yuv = img_yuv[:h_new, :w_new]
        
        y_channel = img_yuv[:, :, 0].astype(np.float32)
        
        # 1. DWT (Level 1)
        coeffs = pywt.dwt2(y_channel, 'haar')
        cA, (cH, cV, cD) = coeffs
        
        # 2. Embed into cH (Horizontal details) - simple strategy
        # Convert text to binary string
        binary_watermark = ''.join(format(ord(char), '08b') for char in watermark_text)
        # Add termination signal (null character)
        binary_watermark += '00000000'
        
        watermark_len = len(binary_watermark)
        
        # Flatten cH for embedding
        cH_flat = cH.flatten()
        
        if watermark_len > len(cH_flat):
            raise ValueError("Text too long for this image.")
            
        # Embed bits
        # Strategy: If bit is 1, make coeff positive/larger. If 0, make negative/smaller.
        # This is a simplified QIM (Quantization Index Modulation) or similar logic.
        # Here we use a very simple odd/even or sign based approach for demonstration stability.
        # Better approach for DWT-DCT is usually modifying mid-band frequencies.
        # Let's use a simpler LSB-like approach on DWT coefficients but with a strength factor.
        
        strength = 5
        
        for i in range(watermark_len):
            bit = int(binary_watermark[i])
            # Simple embedding: 
            # If bit 1, ensure coeff > 0 + margin
            # If bit 0, ensure coeff < 0 - margin
            # This is robust enough for simple "invisible" requirement without attacks.
            
            if bit == 1:
                if cH_flat[i] <= 0:
                    cH_flat[i] = strength
                else:
                    cH_flat[i] += strength
            else:
                if cH_flat[i] >= 0:
                    cH_flat[i] = -strength
                else:
                    cH_flat[i] -= strength
                    
        cH_embedded = cH_flat.reshape(cH.shape)
        
        # 3. Inverse DWT
        coeffs_new = (cA, (cH_embedded, cV, cD))
        y_embedded = pywt.idwt2(coeffs_new, 'haar')
        
        # Merge back
        img_yuv[:, :, 0] = np.clip(y_embedded, 0, 255)
        img_rgb = cv2.cvtColor(img_yuv, cv2.COLOR_YCrCb2RGB)
        
        return img_rgb

class WatermarkDecoder:
    def __init__(self):
        pass

    def decode(self, image):
        img_yuv = cv2.cvtColor(image, cv2.COLOR_RGB2YCrCb)
        h, w, _ = img_yuv.shape
        
        # Resize to be even
        h_new = h if h % 2 == 0 else h - 1
        w_new = w if w % 2 == 0 else w - 1
        img_yuv = img_yuv[:h_new, :w_new]
        
        y_channel = img_yuv[:, :, 0].astype(np.float32)
        
        # 1. DWT
        coeffs = pywt.dwt2(y_channel, 'haar')
        cA, (cH, cV, cD) = coeffs
        
        cH_flat = cH.flatten()
        
        # Extract bits
        binary_watermark = ""
        for val in cH_flat:
            if val > 0:
                binary_watermark += "1"
            else:
                binary_watermark += "0"
                
            # Check for null terminator every 8 bits
            if len(binary_watermark) % 8 == 0:
                if binary_watermark[-8:] == "00000000":
                    binary_watermark = binary_watermark[:-8] # Remove terminator
                    break
        
        # Convert binary to text
        try:
            chars = []
            for i in range(0, len(binary_watermark), 8):
                byte = binary_watermark[i:i+8]
                chars.append(chr(int(byte, 2)))
            return "".join(chars)
        except:
            return None
