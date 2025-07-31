# from fastapi import FastAPI, UploadFile, File
# from fastapi.responses import StreamingResponse
# from backgroundremover import remove_background
# from PIL import Image
# import io
# import os
# import uuid

# app = FastAPI()

# @app.post("/remove-background")
# async def remove_background_api(file: UploadFile = File(...)):
#     # Save uploaded image temporarily
#     temp_input_path = f"temp_input_{uuid.uuid4().hex}.png"
#     temp_output_path = f"temp_output_{uuid.uuid4().hex}.png"

#     with open(temp_input_path, "wb") as f:
#         content = await file.read()
#         f.write(content)

#     # Remove background using backgroundremover
#     remove_background(
#         input_path=temp_input_path,
#         output_path=temp_output_path,
#         model_name="u2net"  # or 'isnet-general-use'
#     )

#     # Load the result and prepare streaming response
#     with open(temp_output_path, "rb") as output_file:
#         image_bytes = output_file.read()
#         buffer = io.BytesIO(image_bytes)
#         buffer.seek(0)

#     # Cleanup temp files
#     os.remove(temp_input_path)
#     os.remove(temp_output_path)

#     return StreamingResponse(buffer, media_type="image/png")



from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
import io
import os
import uuid
import subprocess

app = FastAPI()

@app.post("/remove-background")
async def remove_background_api(file: UploadFile = File(...)):
    # Step 1: Save uploaded image temporarily
    temp_input = f"input_{uuid.uuid4().hex}.png"
    temp_output = f"output_{uuid.uuid4().hex}.png"

    with open(temp_input, "wb") as f:
        f.write(await file.read())

    # Step 2: Run the CLI backgroundremover tool via subprocess
    try:
        subprocess.run([
            "backgroundremover",
            "-i", temp_input,
            "-o", temp_output,
            "-m", "u2net"  # or isnet-general-use
        ], check=True)
    except subprocess.CalledProcessError as e:
        os.remove(temp_input)
        return {"error": f"Background removal failed: {str(e)}"}

    # Step 3: Load the processed image
    with open(temp_output, "rb") as out_img:
        buffer = io.BytesIO(out_img.read())
        buffer.seek(0)

    # Step 4: Cleanup
    os.remove(temp_input)
    os.remove(temp_output)

    return StreamingResponse(buffer, media_type="image/png")
