import os
from typing import Optional, Tuple

import torch
from llama_cpp import Llama

def load_model_with_cache(model_id: str, local_dir: str, device: str) -> Tuple[Optional[object], object]:
    """
    Loads a model and tokenizer. If a local .gguf model is available, load it with llama.cpp
    (llama_cpp.Llama) and return (None, llm_instance). Otherwise fall back to downloading/loading
    via Hugging Face transformers and return (tokenizer, model).
    """
    # Create the local directory if it doesn't exist
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
        print(f"Created local model directory: {local_dir}")

    # The directory where this specific model should be stored
    model_name_slug = model_id.replace("/", "--")
    save_path = os.path.join(local_dir, model_name_slug)

    # If the model_id is a direct path to a .gguf file, prefer that
    gguf_path = None
    if model_id.endswith(".gguf") and os.path.exists(model_id):
        gguf_path = model_id

    # Otherwise, look for a .gguf file in the save_path directory
    if not gguf_path and os.path.exists(save_path):
        for f in os.listdir(save_path):
            if f.endswith(".gguf"):
                gguf_path = os.path.join(save_path, f)
                break

    # If we found a GGUF file, load using llama.cpp
    if gguf_path:
        print(f"Loading GGUF model with llama.cpp from: {gguf_path}")
        n_threads = min(8, (os.cpu_count() or 1))
        llm = Llama(
            model_path=gguf_path,
            n_ctx=4096,
            n_threads=n_threads,
            n_gpu_layers=999, # if device != "cpu" else 0,
            n_batch=512,
            temperature=0.7,
            top_p=0.9,
            repeat_penalty=1.1,
            verbose=True,
        )
        # Tokenizer is managed internally by llama_cpp; return None for tokenizer for compatibility
        return None, llm
    
    if not model_id.endswith(".gguf"):

        # If not a GGUF model, fall back to Hugging Face transformers behavior
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except Exception as e:
            raise RuntimeError("transformers package required for non-gguf models and it is not available") from e

        # If model files exist locally, try loading from there first
        if os.path.exists(save_path) and os.listdir(save_path):
            print(f"Loading model from local path: {save_path}")
            try:
                tok = AutoTokenizer.from_pretrained(save_path, use_fast=True)
                model = AutoModelForCausalLM.from_pretrained(
                    save_path,
                    torch_dtype=torch.float32 if device == "cpu" else torch.bfloat16,
                    device_map={"": device} if device != "cpu" else None,
                )
                return tok, model
            except Exception as e:
                print(f"Failed to load from local path: {e}. Falling back to Hugging Face Hub.")

        # Download from Hugging Face Hub
        print(f"Downloading model '{model_id}' from Hugging Face Hub...")
        tok = AutoTokenizer.from_pretrained(model_id, use_fast=True)
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.float32 if device == "cpu" else torch.bfloat16,
            device_map={"": device} if device != "cpu" else None,
        )

        # Save locally for future use
        print(f"Saving model to local path: {save_path}")
        tok.save_pretrained(save_path)
        model.save_pretrained(save_path)

        return tok, model
    return None, None
