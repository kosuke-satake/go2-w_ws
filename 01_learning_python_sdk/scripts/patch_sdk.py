import os

def main():
    filepath = '/home/user/Developer/Projects/go2-w/unitree_sdk2_python/unitree_sdk2py/core/channel.py'
    if not os.path.exists(filepath):
        print(f"Error: SDK path not found at {filepath}")
        return

    with open(filepath, 'r') as f:
        content = f.read()

    # Target is our previous basic patch
    target = """            config = None
            # choose config
            import os as sys_os
            if "CYCLONEDDS_URI" in sys_os.environ:
                config = None
            elif networkInterface is None:
                config = ChannelConfigAutoDetermine
            else:
                config = ChannelConfigHasInterface.replace('$__IF_NAME__$', networkInterface)"""

    replacement = """            config = None
            # choose config
            import os as sys_os
            if "CYCLONEDDS_URI" in sys_os.environ:
                uri = sys_os.environ["CYCLONEDDS_URI"]
                path = uri[7:] if uri.startswith("file://") else uri
                try:
                    with open(path, "r") as f:
                        config = f.read()
                    print(f"[ChannelFactory] Loaded custom CycloneDDS config from: {path}")
                except Exception as e:
                    print(f"[ChannelFactory] Error reading CYCLONEDDS_URI: {e}")
                    config = None
            elif networkInterface is None:
                config = ChannelConfigAutoDetermine
            else:
                config = ChannelConfigHasInterface.replace('$__IF_NAME__$', networkInterface)"""

    if target in content:
        with open(filepath, 'w') as f:
            f.write(content.replace(target, replacement))
        print("PATCH_SUCCESS")
    else:
        # Try the original target just in case
        target_orig = """            config = None
            # choose config
            if networkInterface is None:
                config = ChannelConfigAutoDetermine
            else:
                config = ChannelConfigHasInterface.replace('$__IF_NAME__$', networkInterface)"""
        if target_orig in content:
            with open(filepath, 'w') as f:
                f.write(content.replace(target_orig, replacement))
            print("PATCH_SUCCESS")
        else:
            if "Loaded custom CycloneDDS config from" in content:
                print("PATCH_ALREADY_APPLIED")
            else:
                print("PATCH_TARGET_NOT_FOUND")

if __name__ == "__main__":
    main()
