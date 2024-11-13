from transformers import AutoTokenizer, AutoModel # type: ignore
from sentence_transformers import SentenceTransformer # type: ignore
import torch # type: ignore

def load_codebert_model(model_name='microsoft/codebert-base'):
    """
    Load the CodeBERT tokenizer and model.

    Parameters:
    - model_name (str): Hugging Face model identifier.

    Returns:
    - tokenizer: Tokenizer for CodeBERT.
    - model: Pre-trained CodeBERT model.
    """
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
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
    if not codebase.strip():
        logger.warning("Empty codebase provided for embedding.")
        return None

    try:
        # Tokenize the input code
        inputs = tokenizer(codebase, return_tensors='pt', truncation=True, max_length=512)

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

def load_sentencebert_model(model_name='sentence-transformers/all-MiniLM-L6-v2', logger=None):
    """
    Load the Sentence-BERT model for embedding issue descriptions.

    Parameters:
    - model_name (str): Hugging Face model identifier for Sentence-BERT.

    Returns:
    - model: Pre-trained Sentence-BERT model.
    """
    try:
        model = SentenceTransformer(model_name)
        return model
    except Exception as e:
        logger.error(f"Failed to load Sentence-BERT model '{model_name}': {e}")
        raise

def generate_issue_description_embedding(description, sentencebert_model, logger):
    """
    Generate an embedding for the given issue description using Sentence-BERT.

    Parameters:
    - description (str): The issue description text.
    - sentencebert_model: Pre-trained Sentence-BERT model.
    - logger: Logger instance for logging.

    Returns:
    - List of floats representing the embedding vector.
    """
    if not description.strip():
        logger.warning("Empty issue description provided for embedding.")
        return None

    try:
        # Generate embedding
        embedding = sentencebert_model.encode(description, show_progress_bar=False)
        return embedding.tolist()
    except Exception as e:
        logger.error(f"Error during issue description embedding generation: {e}")
        return None

