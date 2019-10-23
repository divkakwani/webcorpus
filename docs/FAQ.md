## FAQs and Known Issues

### Module not found even after `pip3 install .`
It is possibly due to conflicting installations of `python3` (especially sometimes with `anaconda3`).  
Ensure if `pip3` and `python3` are present in the same directory by:
```bash
which pip3
which python3
```

If they're in different directories, fix the issue, or temporarily use the following:
```bash
python3 -m pip install .
```

### `AttributeError: module 'lib' has no attribute 'X509_up_ref'`
Try the following and reinstall:
```bash
pip3 uninstall pyOpenSSL
```

### My modifications are not reflected in `corpora`
It's recommended to do `pip3 install .` after your modifications to them in effect in `corpora`.