import os
import sys
import polars as pl
import numpy as np
import torch
from tqdm import tqdm

# Add project paths
sys.path.append(os.path.abspath('../CodonFM'))

from src.inference.encodon import EncodonInference
from src.inference.task_types import TaskTypes

from src.data.mutation_dataset import MutationDataset, collate_fn
from src.data.preprocess.mutation_pred import mlm_process_item
from src.data.metadata import MetadataFields

def load_encodon_inference_model(checkpoint_path: str, device: str = "cuda") -> EncodonInference:
    """
    Load pretrained Encodon model using the inference wrapper.
    
    Args:
        checkpoint_path: Path to the pretrained checkpoint
        device: Device to load model on ('cuda' or 'cpu')
        
    Returns:
        EncodonInference object ready for mutation prediction
    """
    print(f"Loading Encodon model from: {checkpoint_path}")
    
    # Create inference wrapper
    inference_model = EncodonInference(
        model_path=checkpoint_path,
        task_type=TaskTypes.MUTATION_PREDICTION
    )
    
    # Configure the model (loads checkpoint and tokenizer)
    inference_model.configure_model()
    inference_model.eval()
    
    print(f"✅ Model loaded successfully on {device}")
    print(f"Model parameters: {sum(p.numel() for p in inference_model.model.parameters()):,}")
    print(f"Tokenizer vocabulary size: {inference_model.tokenizer.vocab_size}")
    
    return inference_model

def load_dataset(config):
    """Load and inspect the ClinVar Alphamissense dataset."""
    print(f"Loading {config['name']} dataset...")
    print(f"Path: {config['data_path']}")
    
    if not os.path.exists(config['data_path']):
        print(f"❌ Dataset not found: {config['data_path']}")
        return None
    
    try:
        # Load data using polars then convert to pandas
        data = pl.read_csv(config['data_path'], ignore_errors=True).to_pandas()
        print(f"✅ Loaded {len(data)} variants")
        print(f"Shape: {data.shape}")
        print(f"Columns: {list(data.columns)}")
        
        # Check for required columns
        required_cols = ['id', 'ref_seq', 'ref_codon', 'alt_codon', 'codon_position']
        missing_cols = [col for col in required_cols if col not in data.columns]
        
        if missing_cols:
            print(f"⚠️ Missing columns: {missing_cols}")
        else:
            print("✅ All required columns present")
        
        # Handle labels based on dataset type
        # data['pathogenicity_label'] = data['label']
        
        # Show sample data
        display_cols = [col for col in ['id', 'ref_codon', 'alt_codon', 'codon_position'] if col in data.columns]
        # display_cols.append('pathogenicity_label')
        
        print(f"\nSample data:")
        print(data[display_cols].head(3))
        
        return data
        
    except Exception as e:
        print(f"❌ Failed to load dataset: {e}")
        return None

def run_mutation_predictions(models, data):
    """Run mutation predictions for ClinVar Alphamissense dataset."""
    if data is None or not models:
        print("❌ No data or models available")
        return {}
    
    print(f"\n=== RUNNING MUTATION PREDICTIONS FOR CLINVAR ALPHAMISSENSE ===")
    
    data_subset = data.copy()
    all_predictions = {}
    
    for model_name, model_info in models.items():
        print(f"\n--- Processing {model_name} ---")
        
        # Create temporary CSV file
        temp_csv_path = f"/tmp/clinvar_alphamissense_{model_name.replace(' ', '_')}_temp.csv"
        data_subset.to_csv(temp_csv_path, index=False)
        
        try:
            # Create MutationDataset
            mutation_dataset = MutationDataset(
                data_path=temp_csv_path,
                tokenizer=model_info['model'].tokenizer,
                process_item=mlm_process_item,
                context_length=2048,
                task="mlm",
                extract_seq=True,
                train_val_test_ratio=None
            )
            
            # Create DataLoader
            dataloader = torch.utils.data.DataLoader(
                mutation_dataset,
                batch_size=32,
                shuffle=False,
                collate_fn=collate_fn,
                num_workers=0
            )
            
            # Run predictions
            all_ids = []
            all_likelihood_ratios = []
            
            model_info['model'].eval()
            model_info['model'].to(model_info['device'])
            with torch.no_grad():
                for batch in tqdm(dataloader, desc=f"{model_name} predictions"):
                    # Move batch to device
                    for key in batch:
                        if isinstance(batch[key], torch.Tensor):
                            batch[key] = batch[key].to(model_info['device'])
                    
                    # Get predictions
                    output = model_info['model'].predict_mutation(batch, ids=batch[MetadataFields.ID])
                    
                    all_ids.extend(output.ids)
                    all_likelihood_ratios.extend(output.likelihood_ratios)
            
            all_predictions[model_name] = {
                'ids': np.array(all_ids),
                'likelihood_ratios': np.array(all_likelihood_ratios)
            }
            
            print(f"✅ Completed {len(all_ids)} predictions")
            print(f"Likelihood ratio range: [{np.min(all_likelihood_ratios):.3f}, {np.max(all_likelihood_ratios):.3f}]")
            
        except Exception as e:
            print(f"❌ Failed predictions for {model_name}: {e}")
            continue
        finally:
            # Clean up temporary file
            if os.path.exists(temp_csv_path):
                os.remove(temp_csv_path)
            
            # Offload model from GPU to free memory
            if 'model' in model_info and hasattr(model_info['model'], 'cpu'):
                model_info['model'].cpu()
                print(f"🔄 Offloaded {model_name} from GPU")
            
            # Clear GPU cache
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                print(f"🧹 Cleared GPU cache after {model_name}")
    
    return all_predictions