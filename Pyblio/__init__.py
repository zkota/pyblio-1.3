"""
This is the root of all the Pybliographer classes.

Main sub-modules:

  - Pyblio.GnomeUI: specific classes for the Gnome 2 UI

  - Pyblio.Format: import/export modules for bibliographic formats

  - Pyblio.ConfDir: configuration options for all the modules
    (importers, GUI,...)


Current architecture

 A complete database is an instance of Pyblio.Base.DataBase. It
behaves like a dictionnary, where the keys are instances of
Pyblio.Key.Key, and the values are instances of
Pyblio.Base.Entry. Alternatively, the database can provide an iterator
to loop over its entries. It is also possible to specify filters on
the iterator to obtain a subset, possibly sorted, of entries.

In turn, each entry has a type (article,...) and is seen as a
dictionnary of typed fields (text, author group, url,...)

The structure of the database (required fields for each entry type for
instance), is defined by instances of Pyblio.Types.EntryDescription.

The import/export code for each format is handled by a generic
mechanism of on-demand loading of python extensions. This is
implemented by Pyblio.Autoload.

Entry points

  - Pyblio.Base: this module is derived for all the supported file
    formats. It provides the abstractions of a database and
    a bibliographic entry.

  - Pyblio.Fields: base class for the field data types

  - Pyblio.Types: definition of an entry type, with mandatory and optional
    fields.
  
"""

