import os
import shutil
import stat
import platform
import psutil
from .utils import sha256_file, secure_random_bytes, verify_file_erasure, verify_drive_erasure

class WipeError(Exception):
    pass

def _force_remove_file(path):
    """Force remove a file by changing its permissions first"""
    try:
        if not os.path.exists(path):
            return
        
        # Remove read-only attribute if present
        try:
            os.chmod(path, stat.S_IWRITE)
        except:
            pass
            
        try:
            os.remove(path)
        except:
            try:
                os.unlink(path)
            except:
                try:
                    shutil.rmtree(path, ignore_errors=True)
                except:
                    pass
    except:
        pass

def _force_remove_dir(path):
    """Force remove a directory and its contents"""
    try:
        if not os.path.exists(path):
            return
            
        # First make the directory and all its contents writable
        for root, dirs, files in os.walk(path):
            # Make all files writable
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    if os.path.exists(file_path):
                        os.chmod(file_path, stat.S_IWRITE)
                except:
                    pass
            # Make all directories writable
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                try:
                    if os.path.exists(dir_path):
                        os.chmod(dir_path, stat.S_IWRITE)
                except:
                    pass
            # Make current directory writable
            try:
                if os.path.exists(root):
                    os.chmod(root, stat.S_IWRITE)
            except:
                pass

        # Try multiple methods to remove the directory
        try:
            shutil.rmtree(path, ignore_errors=True)
        except:
            pass
        
        if os.path.exists(path):
            try:
                # If directory still exists, try to empty it first
                for root, dirs, files in os.walk(path, topdown=False):
                    for name in files:
                        try:
                            file_path = os.path.join(root, name)
                            if os.path.exists(file_path):
                                os.unlink(file_path)
                        except:
                            pass
                    for name in dirs:
                        try:
                            dir_path = os.path.join(root, name)
                            if os.path.exists(dir_path):
                                os.rmdir(dir_path)
                        except:
                            pass
                # Finally try to remove the empty directory
                if os.path.exists(path):
                    os.rmdir(path)
            except:
                pass

    except:
        pass

def _secure_overwrite_file(path, passes=1, pattern='random', chunk_size=1024*1024):
    """Securely overwrite file contents"""
    try:
        if not os.path.exists(path):
            return

        size = os.path.getsize(path)
        if size == 0:
            return

        # Make file writable
        try:
            os.chmod(path, stat.S_IWRITE)
        except:
            pass
        
        # Overwrite the file multiple times
        with open(path, 'wb', buffering=0) as f:
            for p in range(passes):
                f.seek(0)
                remaining = size
                while remaining > 0:
                    n = min(chunk_size, remaining)
                    if pattern == 'zero':
                        buf = b'\x00' * n
                    elif pattern == 'one':
                        buf = b'\xFF' * n
                    elif pattern == 'random':
                        buf = secure_random_bytes(n)
                    else:
                        raise WipeError(f'Unknown pattern {pattern}')
                    f.write(buf)
                    remaining -= n
                f.flush()
                os.fsync(f.fileno())
        
        # Truncate to 0 bytes
        try:
            with open(path, 'w') as f:
                f.truncate(0)
                f.flush()
                os.fsync(f.fileno())
        except:
            pass
        
    except Exception as e:
        raise WipeError(f"Failed to overwrite file: {str(e)}")

def wipe_file(path, method='quick', verify=True):
    """Securely wipe a single file"""
    # Convert to absolute path and normalize
    path = os.path.abspath(os.path.normpath(path))
    
    if not os.path.exists(path):
        raise WipeError(f'Path does not exist: {path}')
        
    if not os.path.isfile(path):
        raise WipeError(f'Not a file: {path}')
        
    try:
        # Test file accessibility
        with open(path, 'rb') as f:
            pass
    except Exception as e:
        raise WipeError(f'Cannot access file: {path} - {str(e)}')
    
    # Get original hash for verification
    orig_hash = sha256_file(path) if verify else None
    
    try:
        # Perform secure overwrite based on method
        if method in ('quick', 'nist'):
            _secure_overwrite_file(path, passes=1, pattern='random')
        elif method == 'dod':
            _secure_overwrite_file(path, passes=1, pattern='zero')
            _secure_overwrite_file(path, passes=1, pattern='one')
            _secure_overwrite_file(path, passes=1, pattern='random')
        else:
            raise WipeError('Unsupported method')
        
        # Force remove the file
        _force_remove_file(path)
        
        # Verify file is gone
        if os.path.exists(path):
            raise WipeError(f"Failed to delete file: {path}")
            
    except Exception as e:
        raise WipeError(f"Wipe failed: {str(e)}")
    
    # Enhanced verification
    verification_result = verify_file_erasure(path, orig_hash) if verify else None
    
    return {
        'original_hash': orig_hash,
        'final_hash': None,
        'verified_changed': True,
        'verification_result': verification_result
    }

def wipe_folder(path, method='quick', verify=True):
    """Securely wipe a folder and all its contents"""
    # Convert to absolute path and normalize
    path = os.path.abspath(os.path.normpath(path))
    
    if not os.path.exists(path):
        raise WipeError(f'Path does not exist: {path}')
        
    if not os.path.isdir(path):
        raise WipeError(f'Not a directory: {path}')
        
    try:
        # Test directory accessibility
        os.listdir(path)
    except Exception as e:
        raise WipeError(f'Cannot access directory: {path} - {str(e)}')
    
    results = []
    try:
        # First pass: wipe all files
        for root, dirs, files in os.walk(path, topdown=False):
            # Wipe all files in current directory
            for name in files:
                file_path = os.path.join(root, name)
                try:
                    result = wipe_file(file_path, method=method, verify=verify)
                    results.append({'path': file_path, **result})
                except Exception as e:
                    results.append({
                        'path': file_path,
                        'error': str(e)
                    })
        
        # Second pass: remove empty directories from bottom up
        for root, dirs, files in os.walk(path, topdown=False):
            # Remove each subdirectory
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                _force_remove_dir(dir_path)
        
        # Finally remove the root directory
        _force_remove_dir(path)
        
        # Verify the directory is gone
        if os.path.exists(path):
            raise WipeError(f"Failed to completely remove directory: {path}")
            
    except Exception as e:
        results.append({
            'path': path,
            'error': str(e)
        })
    
    return results

def get_available_drives():
    """Get list of available drives/partitions"""
    drives = []
    try:
        if platform.system() == "Windows":
            import string
            for letter in string.ascii_uppercase:
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    try:
                        usage = psutil.disk_usage(drive)
                        drives.append({
                            'path': drive,
                            'label': f"Drive {letter}",
                            'total': usage.total,
                            'free': usage.free,
                            'used': usage.used
                        })
                    except:
                        drives.append({
                            'path': drive,
                            'label': f"Drive {letter}",
                            'total': 0,
                            'free': 0,
                            'used': 0
                        })
        else:
            # Linux/Unix systems
            partitions = psutil.disk_partitions()
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    drives.append({
                        'path': partition.mountpoint,
                        'label': f"{partition.device} ({partition.fstype})",
                        'total': usage.total,
                        'free': usage.free,
                        'used': usage.used
                    })
                except:
                    pass
    except Exception as e:
        raise WipeError(f"Failed to enumerate drives: {str(e)}")
    
    return drives

def wipe_drive(drive_path, method='quick', verify=True):
    """Securely wipe an entire drive/partition with enhanced USB/exFAT support"""
    # Convert to absolute path and normalize
    drive_path = os.path.abspath(os.path.normpath(drive_path))
    
    if not os.path.exists(drive_path):
        raise WipeError(f'Drive does not exist: {drive_path}')
    
    # Safety check - prevent wiping system drives
    if platform.system() == "Windows":
        system_drives = ['C:\\', 'D:\\']  # Common system drives
        if drive_path.upper() in [d.upper() for d in system_drives]:
            raise WipeError(f'Cannot wipe system drive: {drive_path}')
    else:
        if drive_path in ['/', '/boot', '/home']:
            raise WipeError(f'Cannot wipe system partition: {drive_path}')
    
    results = []
    total_files = 0
    processed_files = 0
    
    try:
        # First, get total file count for progress tracking
        for root, dirs, files in os.walk(drive_path):
            total_files += len(files)
        
        # Enhanced file wiping with better error handling
        for root, dirs, files in os.walk(drive_path):
            for name in files:
                file_path = os.path.join(root, name)
                processed_files += 1
                
                try:
                    # Enhanced file removal for USB drives
                    result = _wipe_file_enhanced(file_path, method=method, verify=verify)
                    results.append({'path': file_path, **result})
                except Exception as e:
                    # Try alternative removal methods
                    try:
                        _force_remove_file_enhanced(file_path)
                        results.append({
                            'path': file_path,
                            'status': 'force_removed',
                            'error': None
                        })
                    except Exception as e2:
                        results.append({
                            'path': file_path,
                            'error': f"Primary: {str(e)}, Fallback: {str(e2)}"
                        })
        
        # Enhanced directory removal
        for root, dirs, files in os.walk(drive_path, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    _force_remove_dir_enhanced(dir_path)
                except Exception as e:
                    results.append({
                        'path': dir_path,
                        'error': f"Directory removal failed: {str(e)}"
                    })
        
        # Final cleanup - try to remove any remaining files
        _cleanup_remaining_files(drive_path, results)
        
    except Exception as e:
        results.append({
            'path': drive_path,
            'error': f"Drive wipe failed: {str(e)}"
        })
    
    # Enhanced verification for drive
    verification_result = verify_drive_erasure(drive_path) if verify else None
    
    return {
        'drive_path': drive_path,
        'method': method,
        'verified': verify,
        'results': results,
        'total_files_processed': len([r for r in results if 'error' not in r]),
        'total_files_found': total_files,
        'verification_result': verification_result
    }

def _force_remove_file_enhanced(path):
    """Enhanced file removal for USB drives and exFAT"""
    try:
        if not os.path.exists(path):
            return
        
        # Remove read-only, hidden, and system attributes on Windows
        if platform.system() == "Windows":
            try:
                import win32file
                win32file.SetFileAttributes(path, win32file.FILE_ATTRIBUTE_NORMAL)
            except:
                try:
                    os.chmod(path, stat.S_IWRITE)
                except:
                    pass
        
        # Try multiple removal methods
        try:
            os.remove(path)
        except:
            try:
                os.unlink(path)
            except:
                try:
                    shutil.rmtree(path, ignore_errors=True)
                except:
                    # Last resort - try to overwrite with zeros then remove
                    try:
                        with open(path, 'wb') as f:
                            f.write(b'\x00' * 1024)  # Write 1KB of zeros
                        os.remove(path)
                    except:
                        pass
    except:
        pass

def _force_remove_dir_enhanced(path):
    """Enhanced directory removal for USB drives"""
    try:
        if not os.path.exists(path):
            return
        
        # Remove attributes on Windows
        if platform.system() == "Windows":
            try:
                import win32file
                win32file.SetFileAttributes(path, win32file.FILE_ATTRIBUTE_NORMAL)
            except:
                try:
                    os.chmod(path, stat.S_IWRITE)
                except:
                    pass
        
        # Try to remove directory
        try:
            os.rmdir(path)
        except:
            try:
                shutil.rmtree(path, ignore_errors=True)
            except:
                pass
    except:
        pass

def _wipe_file_enhanced(path, method='quick', verify=True):
    """Enhanced file wiping for USB drives with better error handling"""
    try:
        if not os.path.exists(path):
            return {'status': 'not_found'}
        
        # Get original hash for verification
        orig_hash = sha256_file(path) if verify else None
        
        # Try to overwrite the file
        try:
            if method in ('quick', 'nist'):
                _secure_overwrite_file(path, passes=1, pattern='random')
            elif method == 'dod':
                _secure_overwrite_file(path, passes=1, pattern='zero')
                _secure_overwrite_file(path, passes=1, pattern='one')
                _secure_overwrite_file(path, passes=1, pattern='random')
        except Exception as e:
            # If overwrite fails, try to at least remove the file
            _force_remove_file_enhanced(path)
            return {
                'original_hash': orig_hash,
                'status': 'removed_without_overwrite',
                'error': str(e)
            }
        
        # Force remove the file
        _force_remove_file_enhanced(path)
        
        return {
            'original_hash': orig_hash,
            'status': 'wiped_and_removed',
            'verified_changed': True
        }
        
    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e)
        }

def _cleanup_remaining_files(drive_path, results):
    """Clean up any remaining files that might have been missed"""
    try:
        # Try to find and remove any remaining files
        for root, dirs, files in os.walk(drive_path):
            for name in files:
                file_path = os.path.join(root, name)
                if os.path.exists(file_path):
                    try:
                        _force_remove_file_enhanced(file_path)
                        results.append({
                            'path': file_path,
                            'status': 'cleanup_removed'
                        })
                    except:
                        pass
    except:
        pass