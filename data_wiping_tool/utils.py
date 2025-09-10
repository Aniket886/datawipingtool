import hashlib, os, random, time

def sha256_file(path, chunk_size=1024*1024):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def file_size(path):
    return os.path.getsize(path)

def secure_random_bytes(n):
    return os.urandom(n)

def random_pattern_byte():
    return random.randint(0, 255).to_bytes(1, 'little')

def verify_file_erasure(file_path, original_hash=None, sample_size=1024):
    """
    Enhanced verification of file erasure with multiple methods:
    1. Check if file exists (should be False)
    2. If file exists, sample random chunks and verify they're overwritten
    3. Compare with original hash if provided
    """
    verification_results = {
        'file_exists': False,
        'file_accessible': False,
        'sampling_verified': False,
        'hash_verified': False,
        'verification_time': time.time()
    }
    
    # Check if file still exists
    if not os.path.exists(file_path):
        verification_results['file_exists'] = False
        verification_results['sampling_verified'] = True  # Can't sample if file doesn't exist
        return verification_results
    
    verification_results['file_exists'] = True
    
    try:
        # Test file accessibility
        with open(file_path, 'rb') as f:
            verification_results['file_accessible'] = True
            
            # Get file size for sampling
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                verification_results['sampling_verified'] = True
                return verification_results
            
            # Sample random chunks to verify overwrite
            samples_verified = 0
            total_samples = min(10, max(1, file_size // sample_size))
            
            for _ in range(total_samples):
                # Random position in file
                pos = random.randint(0, max(0, file_size - sample_size))
                f.seek(pos)
                chunk = f.read(sample_size)
                
                # Check if chunk contains only zeros or random data (not original content)
                if len(chunk) == sample_size:
                    # Simple heuristic: check if chunk is all zeros or has high entropy
                    if chunk == b'\x00' * sample_size or len(set(chunk)) > sample_size // 4:
                        samples_verified += 1
            
            verification_results['sampling_verified'] = (samples_verified >= total_samples * 0.8)
            
            # Hash verification if original hash provided
            if original_hash:
                current_hash = sha256_file(file_path)
                verification_results['hash_verified'] = (current_hash != original_hash)
            
    except Exception as e:
        verification_results['error'] = str(e)
    
    return verification_results

def verify_drive_erasure(drive_path, sample_files=None):
    """
    Verify drive erasure by checking if files are properly wiped
    """
    verification_results = {
        'drive_accessible': False,
        'files_checked': 0,
        'files_verified': 0,
        'verification_time': time.time()
    }
    
    try:
        # Check if drive is accessible
        os.listdir(drive_path)
        verification_results['drive_accessible'] = True
        
        # If specific files provided, check them
        if sample_files:
            for file_path in sample_files:
                if os.path.exists(file_path):
                    verification_results['files_checked'] += 1
                    # For drive verification, we mainly check if files are gone
                    if not os.path.exists(file_path):
                        verification_results['files_verified'] += 1
        else:
            # Check a sample of remaining files
            remaining_files = []
            for root, dirs, files in os.walk(drive_path):
                remaining_files.extend([os.path.join(root, f) for f in files[:5]])  # Sample first 5 files per directory
                if len(remaining_files) >= 20:  # Limit to 20 files for performance
                    break
            
            verification_results['files_checked'] = len(remaining_files)
            verification_results['files_verified'] = len([f for f in remaining_files if not os.path.exists(f)])
    
    except Exception as e:
        verification_results['error'] = str(e)
    
    return verification_results
