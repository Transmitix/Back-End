from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import shutil
import os
import subprocess

app = FastAPI()

# Enable CORS to allow requests from the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React development server URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory to save uploaded files
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    fileType: str = Form(...),
    sendMethod: str = Form(...),
):
    try:
        # Save the uploaded file to the server
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Log the received details
        print(f"Received file: {file.filename}")
        print(f"File Type: {fileType}")
        print(f"Send Method: {sendMethod}")

        # Process the file by adding preamble and end delimiter
        processed_file_path = os.path.join(UPLOAD_DIR, f"processed_{file.filename}")
        add_preamble_and_end_delimiter(file_path, processed_file_path)

        # Feed the processed file into QPSK_text_tx_rx.py using the system's default Python interpreter
        qpsk_output_path = os.path.join(UPLOAD_DIR, f"qpsk_{file.filename}")
        subprocess.run(["python3", "QPSK_text_tx_rx.py", processed_file_path, qpsk_output_path], check=True)

        # Feed the output of QPSK_text_tx_rx.py into remove_preamble_and_end_delimiter
        final_output_path = os.path.join(UPLOAD_DIR, f"final_{file.filename}")
        remove_preamble_and_end_delimiter(qpsk_output_path, final_output_path)

        # Simulate file processing (e.g., conversion or sending logic)
        processed_message = (
            f"File '{file.filename}' received and processed. "
            f"File type: {fileType}, Method: {sendMethod}."
        )

        # Return success response
        return JSONResponse(content={"message": processed_message, "final_output_path": final_output_path}, status_code=200)

    except subprocess.CalledProcessError as e:
        print(f"Subprocess error: {e}")
        return JSONResponse(content={"message": "An error occurred during QPSK processing."}, status_code=500)
    except Exception as e:
        # Handle other errors and return appropriate response
        print(f"Error: {e}")
        return JSONResponse(content={"message": "An error occurred during processing."}, status_code=500)
def add_preamble_and_end_delimiter(file_path, output_path):
    with open('preamble.txt', 'rb') as f1:
        preamble = f1.read()
    
    with open('tail.txt', 'rb') as f2:
        tail = f2.read()

    with open(file_path, 'rb') as input_file:
        file_data = input_file.read()

    # Create the output file with preamble and end delimiter
    with open(output_path, 'wb') as output_file:
        output_file.write(preamble)        # Add preamble
        output_file.write(file_data)      # Add file content
        output_file.write(tail)  # Add end delimiter

    print(f"Preamble and end delimiter added. Output saved to {output_path}")

#add_preamble_and_end_delimiter('flower.jpg', 'input_with_preamble.jpg') # images- give input to flower.jpg
# add_preamble_and_end_delimiter('sample_vid.mp4', 'input_with_preamble.mp4') # mp4- give input to sample_vid.mp4

def remove_preamble_and_end_delimiter(input_path, output_path):
    # Define preamble and end delimiter
    preamble = b'11111111'
    end_delimiter = b'11111111'

    with open(input_path, 'rb') as input_file:
        file_data = input_file.read()

    # Locate preamble and end delimiter
    preamble_index = file_data.find(preamble)

    payload = file_data[preamble_index + len(preamble):]
    file_data = payload

    end_delimiter_index = file_data.find(end_delimiter)

    if preamble_index == -1 or end_delimiter_index == -1:
        raise ValueError("Preamble or end delimiter not found in the file!")

    # Extract the payload between preamble and end delimiter
    payload = file_data[:end_delimiter_index]

    # Save the payload to the output file
    with open(output_path, 'wb') as output_file:
        output_file.write(payload)

    print(f"Preamble and end delimiter removed. Output saved to {output_path}")

#remove_preamble_and_end_delimiter('output_img.jpg', 'output_no_pre_no_del.jpg')
# remove_preamble_and_end_delimiter('output.mp4', 'output_no_pre_no_del.mp4')


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8800)
