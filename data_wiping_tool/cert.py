import uuid, time, platform, os, psutil
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
try:
    import qrcode
    from PIL import Image
    QR_AVAILABLE = True
except Exception:
    QR_AVAILABLE = False

def generate_certificate(output_path, payload: dict):
    cert_id = str(uuid.uuid4())
    issued_at = time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime())
    # Get device information
    device_info = {
        'hostname': platform.node(),
        'system': platform.platform(),
        'processor': platform.processor(),
        'architecture': platform.architecture()[0],
    }
    
    # Get drive information if target is a drive
    target_path = payload.get('target', '')
    drive_info = {}
    try:
        if platform.system() == "Windows" and len(target_path) == 3 and target_path[1] == ':':
            # Windows drive
            drive_info = {
                'drive_letter': target_path[0],
                'drive_type': 'Windows Drive',
                'drive_id': f"\\\\.\\{target_path[0]}:"
            }
        else:
            # Try to get partition info
            partitions = psutil.disk_partitions()
            for partition in partitions:
                if partition.mountpoint == target_path:
                    drive_info = {
                        'device': partition.device,
                        'fstype': partition.fstype,
                        'drive_type': 'Partition'
                    }
                    break
    except:
        pass
    
    meta = {
        'certificate_id': cert_id,
        'issued_at': issued_at,
        'device_info': device_info,
        'drive_info': drive_info,
    }
    payload = {**payload, **meta}
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    c.setFont('Helvetica-Bold', 18)
    c.drawString(25*mm, height-30*mm, 'Certificate of Secure Data Erasure')
    c.setFont('Helvetica', 11)
    y = height-45*mm
    def line(txt, dy=7*mm):
        nonlocal y
        c.drawString(25*mm, y, txt)
        y -= dy
    line(f'Certificate ID: {cert_id}')
    line(f'Issued At: {issued_at}')
    line(f'Target: {payload.get("target")}')
    line(f'Method: {payload.get("method")}')
    line(f'Verified: {payload.get("verified")}')
    
    # Device information
    device_info = payload.get('device_info', {})
    if device_info:
        line(f'Device: {device_info.get("hostname", "Unknown")}')
        line(f'System: {device_info.get("system", "Unknown")}')
    
    # Drive information
    drive_info = payload.get('drive_info', {})
    if drive_info:
        if 'drive_letter' in drive_info:
            line(f'Drive: {drive_info["drive_letter"]} ({drive_info.get("drive_type", "Unknown")})')
        elif 'device' in drive_info:
            line(f'Device: {drive_info["device"]} ({drive_info.get("fstype", "Unknown")})')
    
    results = payload.get('results')
    if isinstance(results, list):
        line(f'Items Processed: {len(results)}')
    elif isinstance(results, dict) and 'total_files_processed' in results:
        line(f'Files Processed: {results["total_files_processed"]}')
    else:
        line('Items Processed: 1')
    c.showPage()
    c.setFont('Courier', 9)
    c.drawString(20*mm, height-20*mm, 'Erasure Metadata (JSON)')
    from reportlab.platypus import Preformatted, Frame
    from reportlab.lib.styles import getSampleStyleSheet
    import json
    styles = getSampleStyleSheet()
    text = json.dumps(payload, indent=2)
    frame = Frame(15*mm, 15*mm, width-30*mm, height-40*mm, showBoundary=0)
    pre = Preformatted(text, styles['Code'])
    frame.addFromList([pre], c)
    if QR_AVAILABLE:
        # Start a new page for the QR code
        c.showPage()
        c.setFont('Helvetica', 12)
        c.drawString(25*mm, height-30*mm, 'Scan QR for Certificate Metadata')
        # Generate a QR code image with only essential data
        essential_data = {
            'certificate_id': payload['certificate_id'],
            'issued_at': payload['issued_at'],
            'target': payload['target'],
            'method': payload['method']
        }
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(json.dumps(essential_data))
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save the image to a temporary file
        temp_path = os.path.join(os.path.dirname(output_path), f'temp_qr_{cert_id}.png')
        img.save(temp_path)
        
        # Draw the QR code on the page
        c.drawImage(temp_path, 25*mm, height-130*mm, 80*mm, 80*mm)
        
        # Clean up temporary file
        try:
            os.remove(temp_path)
        except:
            pass
            
    c.save()
    return {'certificate_id': cert_id, 'path': output_path}
