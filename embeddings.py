from transformers import AutoTokenizer, AutoModel # type: ignore
import torch # type: ignore
DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"
def load_codebert_model(model_name='microsoft/codebert-base'):
    """
    Load the CodeBERT tokenizer and model.

    Parameters:
    - model_name (str): Hugging Face model identifier.

    Returns:
    - tokenizer: Tokenizer for CodeBERT.
    - model: Pre-trained CodeBERT model.
    """
    tokenizer = AutoTokenizer.from_pretrained(model_name).to(DEVICE)
    model = AutoModel.from_pretrained(model_name).to(DEVICE)
    return tokenizer, model

def generate_code_embedding(codebase, tokenizer, model, logger):
    """
    Generate an embedding for the given codebase using CodeBERT.

    Parameters:
    - codebase (str): The entire codebase as a single string.
    - tokenizer: Tokenizer for CodeBERT.
    - model: Pre-trained CodeBERT model.
    - logger: Logger instance for logging.

    Returns:
    - List of floats representing the embedding vector.
    """
    if len(codebase) == 0:
        logger.warning("Empty codebase provided for embedding.")
        return None

    try:
        # Tokenize the input code
        stacked_codebase = ""
        for code in codebase.values():
            stacked_codebase += code 
        inputs = tokenizer(stacked_codebase, return_tensors='pt', truncation=True, max_length=512)

        # Get model outputs
        with torch.no_grad():
            outputs = model(**inputs)

        # Perform mean pooling on the token embeddings
        embeddings = outputs.last_hidden_state.mean(dim=1).squeeze()

        # Convert to CPU and detach from the computation graph
        embeddings = embeddings.cpu().numpy()

        return embeddings.tolist()
    except Exception as e:
        logger.error(f"Error during embedding generation: {e}")
        return None

def generate_issue_description_embedding(description, model, tokenizer, logger):
    """
    Generate an embedding for the given issue description using CodeBERT.

    Parameters:
    - description (str): The issue description text.
    - model: Pre-trained CodeBERT model.
    - logger: Logger instance for logging.

    Returns:
    - List of floats representing the embedding vector.
    """
    if len(description) == 0:
        logger.warning("Empty issue description provided for embedding.")
        return None

    try:
        # Tokenize the input description
        inputs = tokenizer(description, return_tensors='pt', truncation=True, max_length=512)

        # Get model outputs
        with torch.no_grad():
            outputs = model(**inputs)

        # Perform mean pooling on the token embeddings
        embeddings = outputs.last_hidden_state.mean(dim=1).squeeze()

        # Convert to CPU and detach from the computation graph
        embeddings = embeddings.cpu().numpy()

        return embeddings.tolist()
    
    except Exception as e:
        logger.error(f"Error during issue description embedding generation: {e}")
        return None

