import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any

class WipeLogger:
    """Comprehensive logging system for data wiping operations"""
    
    def __init__(self, log_dir=None):
        if log_dir is None:
            log_dir = os.path.join(os.path.expanduser('~'), 'DataWipingLogs')
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Create main log file
        self.log_file = os.path.join(self.log_dir, 'wipe_history.json')
        self.session_log = os.path.join(self.log_dir, f'session_{int(time.time())}.json')
        
        # Initialize log files if they don't exist
        if not os.path.exists(self.log_file):
            self._initialize_log_file()
    
    def _initialize_log_file(self):
        """Initialize the main log file with empty structure"""
        initial_data = {
            'version': '1.0',
            'created_at': datetime.now().isoformat(),
            'total_operations': 0,
            'operations': []
        }
        with open(self.log_file, 'w') as f:
            json.dump(initial_data, f, indent=2)
    
    def log_operation(self, operation_data: Dict[str, Any]) -> str:
        """Log a complete wiping operation"""
        operation_id = f"op_{int(time.time())}_{operation_data.get('method', 'unknown')}"
        
        log_entry = {
            'operation_id': operation_id,
            'timestamp': datetime.now().isoformat(),
            'target': operation_data.get('target', ''),
            'method': operation_data.get('method', ''),
            'verified': operation_data.get('verified', False),
            'success': operation_data.get('success', False),
            'error': operation_data.get('error', None),
            'results': operation_data.get('results', {}),
            'certificate_path': operation_data.get('certificate_path', ''),
            'device_info': operation_data.get('device_info', {}),
            'drive_info': operation_data.get('drive_info', {})
        }
        
        # Add to main log
        self._add_to_main_log(log_entry)
        
        # Create individual operation log
        self._create_operation_log(operation_id, log_entry)
        
        return operation_id
    
    def _add_to_main_log(self, log_entry: Dict[str, Any]):
        """Add entry to the main log file"""
        try:
            with open(self.log_file, 'r') as f:
                data = json.load(f)
        except:
            data = {'operations': [], 'total_operations': 0}
        
        data['operations'].append(log_entry)
        data['total_operations'] = len(data['operations'])
        data['last_updated'] = datetime.now().isoformat()
        
        # Keep only last 100 operations in main log
        if len(data['operations']) > 100:
            data['operations'] = data['operations'][-100:]
        
        with open(self.log_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _create_operation_log(self, operation_id: str, log_entry: Dict[str, Any]):
        """Create individual log file for this operation"""
        op_log_file = os.path.join(self.log_dir, f'{operation_id}.json')
        with open(op_log_file, 'w') as f:
            json.dump(log_entry, f, indent=2)
    
    def get_operation_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent operation history"""
        try:
            with open(self.log_file, 'r') as f:
                data = json.load(f)
            operations = data.get('operations', [])
            return operations[-limit:] if limit > 0 else operations
        except:
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get wiping statistics"""
        try:
            with open(self.log_file, 'r') as f:
                data = json.load(f)
            
            operations = data.get('operations', [])
            if not operations:
                return {'total_operations': 0}
            
            # Calculate statistics
            total_ops = len(operations)
            successful_ops = len([op for op in operations if op.get('success', False)])
            failed_ops = total_ops - successful_ops
            
            # Method usage
            method_counts = {}
            for op in operations:
                method = op.get('method', 'unknown')
                method_counts[method] = method_counts.get(method, 0) + 1
            
            # Recent activity (last 7 days)
            recent_ops = []
            week_ago = time.time() - (7 * 24 * 60 * 60)
            for op in operations:
                try:
                    op_time = datetime.fromisoformat(op['timestamp']).timestamp()
                    if op_time > week_ago:
                        recent_ops.append(op)
                except:
                    pass
            
            return {
                'total_operations': total_ops,
                'successful_operations': successful_ops,
                'failed_operations': failed_ops,
                'success_rate': (successful_ops / total_ops * 100) if total_ops > 0 else 0,
                'method_usage': method_counts,
                'recent_operations_7days': len(recent_ops),
                'last_operation': operations[-1]['timestamp'] if operations else None
            }
        except:
            return {'total_operations': 0}
    
    def export_logs(self, output_path: str, format: str = 'json'):
        """Export logs to a file"""
        try:
            with open(self.log_file, 'r') as f:
                data = json.load(f)
            
            if format.lower() == 'json':
                with open(output_path, 'w') as f:
                    json.dump(data, f, indent=2)
            elif format.lower() == 'csv':
                import csv
                with open(output_path, 'w', newline='') as f:
                    if data.get('operations'):
                        writer = csv.DictWriter(f, fieldnames=data['operations'][0].keys())
                        writer.writeheader()
                        writer.writerows(data['operations'])
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            return True
        except Exception as e:
            print(f"Export failed: {e}")
            return False
    
    def clear_old_logs(self, days_to_keep: int = 30):
        """Clear logs older than specified days"""
        try:
            cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)
            removed_count = 0
            
            for filename in os.listdir(self.log_dir):
                if filename.startswith('op_') and filename.endswith('.json'):
                    file_path = os.path.join(self.log_dir, filename)
                    if os.path.getmtime(file_path) < cutoff_time:
                        os.remove(file_path)
                        removed_count += 1
            
            return removed_count
        except Exception as e:
            print(f"Cleanup failed: {e}")
            return 0
