# AuthPixel 🔒

AuthPixel is a local web application for invisible image watermarking using Streamlit. It allows you to embed invisible text watermarks into images and verify/decode them to prove ownership.

**Lightweight Version**: This version uses a custom DWT-based algorithm and does NOT require heavy deep learning libraries like PyTorch.

## Features
- **Protect**: Embed invisible text watermarks into images using a custom DWT algorithm.
- **Verify**: Decode and reveal hidden watermarks from images.
- **Privacy**: Runs entirely on your local machine. No data is uploaded to the cloud.
- **Cyberpunk UI**: A professional dark mode interface.

## Setup & Run

1.  **Create a Virtual Environment**:
    ```bash
    python -m venv venv
    ```

2.  **Activate the Virtual Environment**:
    - **Windows (PowerShell)**:
      ```powershell
      .\venv\Scripts\Activate.ps1
      ```
    - **Windows (Command Prompt)**:
      ```cmd
      .\venv\Scripts\activate.bat
      ```
    - **Mac/Linux**:
      ```bash
      source venv/bin/activate
      ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the App**:
    ```bash
    streamlit run app.py
    ```

## Technologies
- Streamlit
- OpenCV
- NumPy
- Pillow
- PyWavelets
