.. :changelog:

History
-------

0.1.1 (2014-10-02)
------------------

* First release

0.1.2 (2014-10-02)
------------------

* Changed AbstractTask uids to be shorter
  (Easier to read for logging purposes)

0.1.3 (2014-10-08)
------------------

* Added ability to specify Pickle protocol version

0.1.4 (2014-10-11)
------------------

* Removed Pickle and reverted to using JSON intead due to compatibility
  issues between Python 2 -> Python 3.

0.1.5 (2014-10-23)
------------------

* Removed setup.py import of redisqueue. Causing failed installation if
  redis is not already installed.
