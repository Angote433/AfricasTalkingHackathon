import traceback

try:
    import main
    print('Imported main successfully')
except Exception:
    print('Importing main failed with traceback:')
    traceback.print_exc()

print('Done')
