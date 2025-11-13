import pandas as pd
from transformers import AutoModelForTokenClassification, AutoTokenizer
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

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

from datasets import Dataset
dataset = Dataset.from_pandas(df)

model_name = "dbmdz/bert-large-cased-finetuned-conll03-english"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForTokenClassification.from_pretrained(model_name)

def tokenize_function(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True)

tokenized_dataset = dataset.map(tokenize_function, batched=True)

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