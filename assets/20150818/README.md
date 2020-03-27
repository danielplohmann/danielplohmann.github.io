# README #

This repository accompanies the blog posts:

* http://byte-atlas.blogspot.com/2015/08/knowledge-fragment-unwrapping-fobber.html
* http://byte-atlas.blogspot.com/2015/08/knowledge-fragment-fobber-inline-string.html

The Python scripts can be used to decrypt different parts of a Fobber memory dump, according to their script name.

* applying fobber_decrypt_functions.py:
* 49974f869f8f5d32620685bc1818c957_rw_0x950000 -----> 49974f869f8f5d32620685bc1818c957_rw_0x950000_decrypted

and  

* applying fobber_decrypt_strings.py:
* 49974f869f8f5d32620685bc1818c957_rw_0x950000_decrypted -----> 49974f869f8f5d32620685bc1818c957_rw_0x950000_decrypted_strfixed

Sample used for demonstration:

md5:    `49974f869f8f5d32620685bc1818c957`  
sha256: `93508580e84d3291f55a1f2cb15f27666238add9831fd20736a3c5e6a73a2cb4`