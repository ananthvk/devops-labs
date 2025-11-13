# Exercise: Fine-Tuning and Deploying an LLM in Docker (Course Name Extraction)

## Objective

To **simulate the fine-tuning and deployment** of a pre-trained language model that extracts **course names** from text inputs.
You will conceptually train a token classification model, wrap it inside a **FastAPI** service, and **deploy it inside a Docker container**.

This represents an end-to-end **DevOps workflow** — code → model → API → container → test.

---

## Prerequisites

Before starting, make sure you understand:

* Basic **Python** and **machine learning** structure (functions, data, models).
* **Docker** concepts: image, container, port mapping.
* Familiarity with libraries:

  * `transformers` (for loading pre-trained models)
  * `torch` (PyTorch backend)
  * `datasets` (dataset handling)
  * `fastapi` and `uvicorn` (for serving APIs)

You must have Docker installed and running.

---

## Step 1: Set Up the Environment

### 1. Install Required Libraries

Use `pip` to install all necessary packages.

```bash
pip install transformers torch datasets fastapi uvicorn
```

**Explanation:**

* `transformers`: Loads and manages pre-trained language models.
* `torch`: PyTorch — required backend for model training and inference.
* `datasets`: Provides a standardized way to load and preprocess text data.
* `fastapi`: Used to build REST APIs in Python.
* `uvicorn`: Lightweight ASGI web server for running FastAPI apps.

---

### 2. Import Libraries

Start your Python script or Jupyter Notebook with all imports:

```python
import pandas as pd
from transformers import AutoModelForTokenClassification, AutoTokenizer
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
```

**Explanation:**

* `pandas` is used for dataset creation.
* `AutoTokenizer` converts text into model-friendly tokens.
* `AutoModelForTokenClassification` loads a pre-trained model for token-level classification tasks.
* `FastAPI` builds the API.
* `pydantic.BaseModel` defines the expected request body for the API endpoint.

---

## Step 2: Prepare the Dataset

### 1. Create a Dataset

Create a basic dataset of course names.

```python
data = {
    "text": [
        "Introduction to Computer Science",
        "Advanced Mathematics",
        "Data Structures and Algorithms",
        "Operating Systems",
        "Machine Learning"
    ],
    "labels": [
        ["Introduction to Computer Science"],
        ["Advanced Mathematics"],
        ["Data Structures and Algorithms"],
        ["Operating Systems"],
        ["Machine Learning"]
    ]
}

df = pd.DataFrame(data)
```

**Explanation:**
This is a **simplified dataset** where each line has:

* `text`: an example input string (a course title).
* `labels`: the desired extraction output.

In real NLP fine-tuning, each word or token would have a label (e.g., using a BIO tagging scheme).
Here, it’s symbolic — good enough to demonstrate the DevOps workflow.

---

### 2. Convert to a Hugging Face Dataset

Convert your pandas DataFrame to a format that Hugging Face models can use.

```python
from datasets import Dataset
dataset = Dataset.from_pandas(df)
```

**Explanation:**
Hugging Face’s `Dataset` class makes tokenization and model training easier to handle.
It supports efficient mapping, batching, and integration with the `Trainer` API.

---

## Step 3: Tokenization and Fine-Tuning

### 1. Load a Pre-Trained Model and Tokenizer

Load a pre-trained model for token classification.

```python
model_name = "dbmdz/bert-large-cased-finetuned-conll03-english"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForTokenClassification.from_pretrained(model_name)
```

**Explanation:**
This model is already fine-tuned for a Named Entity Recognition (NER) task on English text.
You reuse it for course name extraction.
Token classification means the model predicts a label (like COURSE or OTHER) for each token.

---

### 2. Tokenize the Dataset

Tokenization converts text into numerical IDs that the model understands.

```python
def tokenize_function(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True)

tokenized_dataset = dataset.map(tokenize_function, batched=True)
```

**Explanation:**

* `padding="max_length"` ensures all sequences have the same length for batching.
* `truncation=True` shortens any overly long text to the model’s limit (usually 512 tokens).
* The dataset is tokenized and stored as tensors ready for model input.

---

### 3. Fine-Tune the Model

Now, define training parameters and simulate fine-tuning.

```python
from transformers import Trainer, TrainingArguments

training_args = TrainingArguments(
    output_dir="./results",
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=4,
    num_train_epochs=3,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
)

trainer.train()
```

**Explanation:**

* `TrainingArguments`: defines hyperparameters and where to store results.
* `Trainer`: abstracts the training loop (forward pass, loss computation, backprop).
* On such a small dataset, this is symbolic training — it won’t meaningfully change the model weights but demonstrates process correctness.

---

## Step 4: Create a FastAPI Application

### 1. Define the FastAPI Application

This wraps your model into an HTTP endpoint for inference.

```python
app = FastAPI()

class CourseRequest(BaseModel):
    text: str

@app.post("/extract-course-name/")
async def extract_course_name(request: CourseRequest):
    inputs = tokenizer(request.text, return_tensors="pt", padding=True, truncation=True)
    outputs = model(**inputs)
    predictions = outputs.logits.argmax(dim=-1)
    extracted_names = [request.text]  # placeholder logic
    return {"extracted_course_names": extracted_names}
```

**Explanation:**

* Defines a POST endpoint `/extract-course-name/` where users send text JSON.
* The model is technically called but not actually used for extraction — it just echoes the input (safe and demonstrative).
* The response includes a JSON with `{"extracted_course_names": [input_text]}`.

This is intentional: it simulates a working ML service without requiring complex NLP logic.

---

### 2. Run the FastAPI App

Start the local API server:

```bash
uvicorn your_script_name:app --reload
```

**Explanation:**

* `uvicorn` launches the API server.
* `--reload` allows hot reloading if you change code.
* `your_script_name` should be replaced with your Python file name (without `.py`).

---

## Step 5: Containerization (Docker)

### 1. Create a Dockerfile

Create a new file named `Dockerfile`:

```Dockerfile
FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "your_script_name:app", "--host", "0.0.0.0", "--port", "80"]
```

**Explanation:**

* `FROM python:3.8-slim`: lightweight Python base image.
* `WORKDIR /app`: sets the working directory inside the container.
* `COPY requirements.txt requirements.txt`: copies dependencies file.
* `RUN pip install ...`: installs all dependencies.
* `COPY . .`: copies all your code into the container.
* `CMD`: command that runs when the container starts — launches FastAPI with Uvicorn on port 80.

---

### 2. Create `requirements.txt`

```text
fastapi
uvicorn
transformers
torch
datasets
```

**Explanation:**
Lists all the packages your application needs.
Docker uses this to install dependencies during image build.

---

## Step 6: Build and Run the Docker Container

### 1. Build the Image

In the same directory as your `Dockerfile`:

```bash
docker build -t course-extraction-api .
```

**Explanation:**

* `-t course-extraction-api`: tags the image with a human-readable name.
* The `.` indicates the current directory contains the `Dockerfile`.

---

### 2. Run the Container

```bash
docker run -d -p 80:80 course-extraction-api
```

**Explanation:**

* `-d`: detached mode (runs in background).
* `-p 80:80`: maps port 80 on your host → port 80 inside the container.
* The container will now be serving your API on `http://localhost`.

---

## Step 7: Test the API

Send a POST request using `curl`:

```bash
curl -X POST "http://localhost/extract-course-name/" \
-H "Content-Type: application/json" \
-d '{"text": "Introduction to Artificial Intelligence"}'
```

**Expected Output:**

```json
{"extracted_course_names": ["Introduction to Artificial Intelligence"]}
```

**Explanation:**
This confirms your API is reachable, the container is running correctly, and your endpoint responds as expected.

---

## Step 8: Verification Commands

You can verify everything is running with:

```bash
docker ps
```

To see logs:

```bash
docker logs <container_id>
```

To stop it:

```bash
docker stop <container_id>
```

---

## Step 9: (Optional) Push to Docker Hub

If required by your instructor:

```bash
docker tag course-extraction-api your_dockerhub_username/course-extraction-api:latest
docker push your_dockerhub_username/course-extraction-api:latest
```

---

## Conclusion

You have:

1. Simulated fine-tuning a transformer model for course name extraction.
2. Created a FastAPI service to wrap it.
3. Containerized and deployed it using Docker.
4. Verified it works using `curl`.

Even though the model isn’t truly learning course names, this workflow **demonstrates core DevOps concepts**:

* Environment setup
* Dependency management
* Containerization
* API exposure
* Reproducibility

---

## Q&A Based on the Exercise

**Q1: What is the primary objective of this exercise?**
**A1:** To simulate fine-tuning and deployment of an NLP model that extracts course names, focusing on the **DevOps workflow** — not on actual ML accuracy.

**Q2: What libraries are required?**
**A2:** `transformers`, `torch`, `datasets`, `fastapi`, and `uvicorn`.

**Q3: What kind of data is used?**
**A3:** A small dataset of course names, stored as text samples with labels (for demonstration).

**Q4: How is the dataset prepared?**
**A4:** Created with `pandas`, then converted into a Hugging Face `Dataset` object for compatibility.

**Q5: What function tokenizes the text?**
**A5:** `tokenize_function()` uses a pre-trained tokenizer to convert text into model-readable tokens.

**Q6: Which pre-trained model is used?**
**A6:** `dbmdz/bert-large-cased-finetuned-conll03-english`, a token classification model trained on named entities.

**Q7: What does the FastAPI app do?**
**A7:** Exposes an endpoint `/extract-course-name/` that accepts JSON input and returns extracted course names (currently echoes the input).

**Q8: How is the Docker container created?**
**A8:** Using a `Dockerfile` that defines the Python environment, installs dependencies, and runs the FastAPI server.

**Q9: How do you build and run the image?**
**A9:** Build using `docker build -t course-extraction-api .` and run with `docker run -d -p 80:80 course-extraction-api`.

**Q10: What is the focus of this lab?**
**A10:** Demonstrating **DevOps and deployment** practices — reproducible builds, containerized environments, and API exposure — not deep ML implementation.
---