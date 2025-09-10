import argparse, json, os
from .wipe import wipe_file, wipe_folder
from .cert import generate_certificate

def main():
    p = argparse.ArgumentParser(description='Data Wiping Tool (CLI)')
    p.add_argument('target', help='file or folder path')
    p.add_argument('--method', choices=['quick','nist','dod'], default='quick', help='wipe method')
    p.add_argument('--no-verify', action='store_true', help='skip verification')
    p.add_argument('--cert-out', default=None, help='certificate PDF output path')
    args = p.parse_args()
    verify = not args.no_verify
    target = args.target
    if os.path.isfile(target):
        result = wipe_file(target, method=args.method, verify=verify)
    elif os.path.isdir(target):
        result = wipe_folder(target, method=args.method, verify=verify)
    else:
        p.error('target must be a file or folder')
    payload = {
        'target': target,
        'method': args.method,
        'verified': (result.get('verified_changed', True) if isinstance(result, dict) else all([r.get('verified_changed', True) for r in result if 'verified_changed' in r])),
        'results': result,
    }
    print(json.dumps(payload, indent=2))
    if args.cert_out:
        info = generate_certificate(args.cert_out, payload)
        print(f"Certificate saved to {info['path']}")

if __name__ == '__main__':
    main()
