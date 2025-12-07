import torch


def padding(tensors, padding_value=0):
    """
    Pad a list of tensors to the same length.
    
    Args:
        tensors: List of tensors to pad
        padding_value: Value to use for padding
        
    Returns:
        Tuple of (padded_tensors, lengths)
    """
    if not tensors:
        return torch.tensor([]), torch.tensor([])
    
    # Get max length
    max_len = max(t.shape[-1] for t in tensors)
    
    # Pad each tensor
    padded = []
    lengths = []
    for t in tensors:
        length = t.shape[-1]
        lengths.append(length)
        
        if length < max_len:
            pad_size = max_len - length
            # Pad on the right side
            t = torch.nn.functional.pad(t, (0, pad_size), value=padding_value)
        
        padded.append(t)
    
    # Stack tensors
    padded_tensor = torch.stack(padded)
    lengths_tensor = torch.tensor(lengths)
    
    return padded_tensor, lengths_tensor

class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self
