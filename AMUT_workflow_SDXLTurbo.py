import json
import sys
import random
from urllib import request
import datetime
from PIL import Image
import numpy as np

# This function sends a prompt workflow to the specified URL 
# (http://127.0.0.1:8188/prompt) and queues it on the ComfyUI server
# running at that address.
def queue_prompt(prompt_workflow):
    p = {"prompt": prompt_workflow}
    data = json.dumps(p).encode('utf-8')
    req = request.Request("http://127.0.0.1:8188/prompt", data=data)
    request.urlopen(req)

# Read workflow api data from file and convert it into a dictionary 
# Assign it to the variable prompt_workflow
prompt_workflow = json.load(open('workflow_AMUT.json'))

# Use sys.argv to get the prompt from the command line
prompt_text = sys.argv[1]

save_image_node = prompt_workflow["27"]

# Set the text prompt for positive CLIPTextEncode node
prompt_workflow["6"]["inputs"]["text"] = prompt_text


# Set a fixed filename prefix for all images (e.g., "amut")
fixed_filename_prefix = "amut"

# Update the filename prefix in the SaveImage node
prompt_workflow["27"]["inputs"]["filename_prefix"] = fixed_filename_prefix

# Everything set, add the entire workflow to the queue
queue_prompt(prompt_workflow)
