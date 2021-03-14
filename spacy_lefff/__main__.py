def _optional_arg(argv):
    download_dir = None
    try:
        opts, args = getopt.getopt(argv,"d:",["download_dir="])
    except getopt.GetoptError:
        return None
    for opt, arg in opts:
        if opt in ("-o", "--download_dir"):
            download_dir = arg
    return download_dir

if __name__ == "__main__":
    import sys
    import getopt
    from wasabi import msg
    commands = [
        "download_tagger"
    ]
    if len(sys.argv) < 3:
        msg.info("Available commands needs one parameter", ", ".join(commands), exits=1)
    command = sys.argv.pop(1)
    if command == 'download_tagger':
        from . import melt_tagger
        from . import downloader
        download_dir = _optional_arg(sys.argv[1:])
        download_dir = download_dir if download_dir else melt_tagger.DATA_DIR
        downloader.Downloader(melt_tagger.PACKAGE, melt_tagger.URL_MODEL, download_dir)
    else:
        available = "Available: {}".format(", ".join(commands))
        msg.fail("Unknown command: {}".format(command), available, exits=1)
